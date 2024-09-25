import os
from typing import Any, Dict, List, Optional, Union
import yaml
from pydantic import BaseModel, root_validator, Field, ValidationError


# ParamConfig definition for handling parameters
class ParamConfig(BaseModel):
    related_paper_num: int
    base_llm: str
    member_num: int
    reviewer_num: int
    domain: str
    result_path: str
    return_num: Optional[int] = None
    max_token_num: Optional[int] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    stream: Optional[bool] = None
    write_proposal_strategy: str
    max_env_run_num: int


# EvalPromptConfig for validation of eval-related prompts
class EvalPromptTemplate(BaseModel):
    insight_quality: Dict[str, Union[str, List[str]]]
    idea_quality: Dict[str, Union[str, List[str]]]
    proposal_quality: Dict[str, Union[str, List[str]]]
    review_quality: Dict[str, Union[str, List[str]]]
    rebuttal_quality: Dict[str, Union[str, List[str]]]
    metareview_quality: Dict[str, Union[str, List[str]]]

    # Validation to check placeholders
    @root_validator(pre=True)
    def validate_placeholders(cls, values):
        required_placeholders = {
            'insight_quality': ['{insight}'],
            'idea_quality': ['{idea}', '{insights}'],
            'proposal_quality': ['{paper}', '{idea}', '{insights}'],
            'review_quality': ['{idea}', '{insights}', '{paper}', '{review}'],
            'rebuttal_quality': ['{insights}', '{idea}', '{paper}', '{review}', '{rebuttal}'],
            'metareview_quality': ['{insights}', '{idea}', '{paper}', '{reviews}', '{rebuttals}', '{metareview}'],
        }

        for template_name, placeholders in required_placeholders.items():
            template = values.get(template_name, {}).get('template', '')
            missing_placeholders = [p for p in placeholders if p not in template]
            if missing_placeholders:
                raise ValueError(f"Template '{template_name}' is missing placeholders: {', '.join(missing_placeholders)}")

        return values


# AgentPromptConfig for handling prompts related to the agent
class AgentPromptTemplate(BaseModel):
    write_bio: Dict[str, Union[str, List[str]]]
    review_literature: Dict[str, Union[str, List[str]]]
    brainstorm_idea: Dict[str, Union[str, List[str]]]
    discuss_idea: Dict[str, Union[str, List[str]]]
    write_proposal: Dict[str, Union[str, List[str]]]
    write_review_summary: Dict[str, Union[str, List[str]]]
    write_review_strength: Dict[str, Union[str, List[str]]]
    write_review_weakness: Dict[str, Union[str, List[str]]]
    write_review_ethical: Dict[str, Union[str, List[str]]]
    write_review_score: Dict[str, Union[str, List[str]]]
    write_metareview_summary: Dict[str, Union[str, List[str]]]
    write_metareview_strength: Dict[str, Union[str, List[str]]]
    write_metareview_weakness: Dict[str, Union[str, List[str]]]
    write_metareview_ethical: Dict[str, Union[str, List[str]]]
    write_metareview_decision: Dict[str, Union[str, List[str]]]
    write_rebuttal: Dict[str, Union[str, List[str]]]

    @root_validator(pre=True)
    def validate_placeholders(cls, values):
        required_placeholders = {
            'write_bio': ['{publication_info}'],
            'review_literature': ['{bio}', '{papers}'],
            'brainstorm_idea': ['{bio}', '{insights}'],
            'discuss_idea': ['{bio}', '{ideas}'],
            'write_proposal': ['{idea}', '{papers}'],
            'write_review_summary': ['{proposal}'],
            'write_review_strength': ['{proposal}', '{summary}'],
            'write_review_weakness': ['{proposal}', '{summary}'],
            'write_review_ethical': ['{proposal}', '{summary}'],
            'write_review_score': ['{proposal}', '{summary}', '{strength}', '{weakness}'],
            'write_metareview_summary': ['{proposal}', '{reviews}', '{rebuttals}'],
            'write_metareview_strength': ['{proposal}', '{reviews}', '{rebuttals}', '{summary}'],
            'write_metareview_weakness': ['{proposal}', '{reviews}', '{rebuttals}', '{summary}'],
            'write_metareview_ethical': ['{proposal}', '{reviews}', '{rebuttals}', '{summary}'],
            'write_metareview_decision': ['{proposal}', '{reviews}', '{rebuttals}', '{summary}', '{strength}', '{weakness}'],
            'write_rebuttal': ['{proposal}', '{review}'],
        }

        for template_name, placeholders in required_placeholders.items():
            template = values.get(template_name, {}).get('template', '')
            missing_placeholders = [p for p in placeholders if p not in template]
            if missing_placeholders:
                raise ValueError(f"Template '{template_name}' is missing placeholders: {', '.join(missing_placeholders)}")

        return values


class Config(BaseModel):
    param: ParamConfig
    agent_prompt_template: AgentPromptTemplate
    eval_prompt_template: EvalPromptTemplate

    def __init__(self, yaml_config_path: Optional[str] = None, **kwargs: Any) -> None:
        if yaml_config_path:
            yaml_data = self._load_from_yaml(yaml_config_path)
            kwargs.update(yaml_data)
        super().__init__(**kwargs)

    def _load_from_yaml(self, yaml_config_path: str) -> Dict[str, Any]:
        return {
            'param': self._load_yaml_file(os.path.join(yaml_config_path, 'param.yaml')),
            'agent_prompt_template': self._load_prompt_configs(os.path.join(yaml_config_path, 'agent_prompts')),
            'eval_prompt_template': self._load_prompt_configs(os.path.join(yaml_config_path, 'eval_prompts'))
        }

    def _load_yaml_file(self, file_path: str) -> Dict[str, Any]:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"YAML file '{file_path}' does not exist.")
        
        with open(file_path, 'r') as f:
            return yaml.safe_load(f)

    def _load_prompt_configs(self, directory: str) -> Dict[str, Any]:
        if not os.path.exists(directory):
            raise FileNotFoundError(f"Directory '{directory}' does not exist.")
        
        prompt_configs = {}
        for file_name in os.listdir(directory):
            if file_name.endswith(('.yaml', '.yml')):
                file_path = os.path.join(directory, file_name)
                prompt_name = os.path.splitext(file_name)[0]  # Extract the file name without extension
                prompt_configs[prompt_name] = self._load_yaml_file(file_path)

        return prompt_configs

    def save_prompt_configs(self, directory: str, prompt_data: BaseModel) -> None:
        os.makedirs(directory, exist_ok=True)
        prompt_dict = prompt_data.model_dump()

        for prompt_name, config in prompt_dict.items():
            file_path = os.path.join(directory, f'{prompt_name}.yaml')
            with open(file_path, 'w') as f:
                yaml.dump(config, f)

    def remove_unused_yaml_files(self, yaml_config_path: str, keep_files: set) -> None:
        for file_name in os.listdir(yaml_config_path):
            if file_name.endswith('.yaml') and file_name not in keep_files:
                os.remove(os.path.join(yaml_config_path, file_name))
