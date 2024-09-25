import os
from typing import Any, Dict, List, Optional, Union

import yaml
from pydantic import BaseModel, ConfigDict, root_validator


class ParamConfig(BaseModel):
    related_paper_num: int
    base_llm: str
    member_num: int
    reviewer_num: int
    domain: str
    result_path: str
    return_num: Optional[int]
    max_token_num: Optional[int]
    temperature: Optional[float]
    top_p: Optional[float]
    stream: Optional[bool]
    write_proposal_strategy: str
    max_env_run_num: int

    model_config = ConfigDict(extra='allow')


class EvalPromptConfig(BaseModel):
    insight_quality: Dict[str, Union[str, List[str]]]
    idea_quality: Dict[str, Union[str, List[str]]]
    proposal_quality: Dict[str, Union[str, List[str]]]
    review_quality: Dict[str, Union[str, List[str]]]
    rebuttal_quality: Dict[str, Union[str, List[str]]]
    metareview_quality: Dict[str, Union[str, List[str]]]

    model_config = ConfigDict(extra='allow')

    @root_validator(pre=True)
    def validate_placeholders(cls, values):
        required_placeholders = {
            'write_bio': ['{publication_info}'],
            'review_literature': ['{bio}', '{papers}'],
            'brainstorm_idea': ['{bio}', '{insights}'],
            'discuss_idea': ['{bio}', '{ideas}'],
            'write_proposal': ['{idea}', '{papers}'],
            'write_proposal_cot': ['{idea}', '{papers}'],
            'write_proposal_react': ['{idea}', '{papers}'],
            'write_proposal_reflexion': ['{idea}', '{papers}'],
            'write_review_summary': ['{proposal}'],
            'write_review_strength': ['{proposal}', '{summary}'],
            'write_review_weakness': ['{proposal}', '{summary}'],
            'write_review_score': ['{proposal}', '{summary}', '{strength}', '{weakness}'],
            'write_metareview_summary': ['{proposal}', '{reviews}', '{rebuttals}'],
            'write_metareview_strength': ['{proposal}', '{reviews}', '{rebuttals}', '{summary}'],
            'write_metareview_weakness': ['{proposal}', '{reviews}', '{rebuttals}', '{summary}'],
            'write_metareview_decision': ['{proposal}','{reviews}', '{rebuttals}', '{summary}', '{strength}', '{weakness}'],
            'write_rebuttal': ['{proposal}', '{review}'],
        }

        for template_name, placeholders in required_placeholders.items():
            template = values.get(template_name, {}).get('template', '')
            missing_placeholders = [p for p in placeholders if p not in template]
            if missing_placeholders:
                raise ValueError(f"Template '{template_name}' is missing placeholders: {', '.join(missing_placeholders)}")

        return values


class AgentPromptConfig(BaseModel):
    write_bio: Dict[str, Union[str, List[str]]]
    review_literature: Dict[str, Union[str, List[str]]]
    brainstorm_idea: Dict[str, Union[str, List[str]]]
    discuss_idea: Dict[str, Union[str, List[str]]]
    write_proposal: Dict[str, Union[str, List[str]]]
    write_proposal_cot: Dict[str, Union[str, List[str]]]
    write_proposal_react: Dict[str, Union[str, List[str]]]
    write_proposal_reflexion: Dict[str, Union[str, List[str]]]
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

    model_config = ConfigDict(extra='allow')

    @root_validator(pre=True)
    def validate_placeholders(cls, values):
        required_placeholders = {
            'write_bio': ['{publication_info}'],
            'review_literature': ['{bio}', '{papers}'],
            'brainstorm_idea': ['{bio}', '{insights}'],
            'discuss_idea': ['{bio}', '{ideas}'],
            'write_proposal': ['{idea}', '{papers}'],
            'write_proposal_cot': ['{idea}', '{papers}'],
            'write_proposal_react': ['{idea}', '{papers}'],
            'write_proposal_reflexion': ['{idea}', '{papers}'],
            'write_review_summary': ['{proposal}'],
            'write_review_strength': ['{proposal}', '{summary}'],
            'write_review_weakness': ['{proposal}', '{summary}'],
            'write_review_score': ['{proposal}', '{summary}', '{strength}', '{weakness}'],
            'write_metareview_summary': ['{proposal}', '{reviews}', '{rebuttals}'],
            'write_metareview_strength': ['{proposal}', '{reviews}', '{rebuttals}', '{summary}'],
            'write_metareview_weakness': ['{proposal}', '{reviews}', '{rebuttals}', '{summary}'],
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
    agent_prompt: AgentPromptConfig
    eval_prompt: EvalPromptConfig

    def __init__(self, yaml_config_path: Optional[str] = None, **data: Any) -> None:
        super().__init__(**data)
        if yaml_config_path:
            self.load_from_yaml(yaml_config_path)

    def load_from_yaml(self, yaml_config_path: str) -> None:
        self._load_prompt_configs(os.path.join(yaml_config_path, 'agent_prompts'), 'agent_prompt')
        self._load_prompt_configs(os.path.join(yaml_config_path, 'eval_prompts'), 'eval_prompt')

    def save_to_yaml(self, yaml_config_path: str) -> None:
        self._save_prompt_configs(os.path.join(yaml_config_path, 'agent_prompts'), self.agent_prompt)
        self._save_prompt_configs(os.path.join(yaml_config_path, 'eval_prompts'), self.eval_prompt)

    def _load_prompt_configs(self, directory: str, prompt_type: str) -> None:
        if not os.path.exists(directory):
            raise FileNotFoundError(f"Directory {directory} does not exist.")
        
        for file_name in os.listdir(directory):
            if file_name.endswith(('.yaml', '.yml')):
                file_path = os.path.join(directory, file_name)
                with open(file_path, 'r') as f:
                    yaml_cfg = yaml.safe_load(f)
                    prompt_name = file_name.rsplit('.', 1)[0]  # Extract prompt name from the file name
                    setattr(self.__getattribute__(prompt_type), prompt_name, yaml_cfg)

    def _save_prompt_configs(self, directory: str, prompt_data: BaseModel) -> None:
        os.makedirs(directory, exist_ok=True)
        prompt_dict = prompt_data.model_dump()
        
        for prompt_name, config in prompt_dict.items():
            file_path = os.path.join(directory, f'{prompt_name}.yaml')
            with open(file_path, 'w') as f:
                yaml.dump(config, f)

    def _remove_unused_yaml_files(self, yaml_config_path: str, keep_files: set) -> None:
        for file_name in os.listdir(yaml_config_path):
            if file_name.endswith('.yaml') and file_name not in keep_files:
                os.remove(os.path.join(yaml_config_path, file_name))