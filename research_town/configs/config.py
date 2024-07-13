from typing import Any, Dict, Optional

import yaml
from pydantic import BaseModel, ConfigDict


def merge_a_into_b(a: Dict[str, Any], b: Dict[str, Any]) -> None:
    """
    Merge dictionary a into dictionary b recursively.
    """
    for key, value in a.items():
        if isinstance(value, dict) and key in b and isinstance(b[key], dict):
            merge_a_into_b(value, b[key])
        else:
            b[key] = value


class ParamConfig(BaseModel):
    related_paper_num: int = 10
    base_llm: str = 'mistralai/Mixtral-8x7B-Instruct-v0.1'
    max_collaborators_num: int = 3
    domain: str = 'computer_vision'
    reviewer_num: int = 3
    result_path: str = 'Mixtral-8x7B'
    return_num: Optional[int] = 1
    max_token_num: Optional[int] = 512
    temperature: Optional[float] = 0.0
    top_p: Optional[float] = None
    stream: Optional[bool] = None

    model_config = ConfigDict(
        extra='allow',
    )


class PromptTemplateConfig(BaseModel):
    write_bio: str = (
        "Based on the list of the researcher's first person persona from different times, please write a comprehensive first person persona. Focus more on more rescent personas. Be concise and clear (around 300 words)."
        'Here are the personas from different times: {publication_info}'
    )
    find_collaborators: str = (
        'Given the name and profile of me, could you find {max_number} collaborators for the following collaboration task?'
        'Here is my profile: {self_serialize_all}'
        'The collaboration task include: {task_serialize_all}'
        'Here are a full list of the names and profiles of potential collaborators: {collaborators_serialize_all}'
        "Generate the collaborator in a list separated by '-' for each collaborator"
    )
    review_literature: str = (
        'Given the profile of me, keywords, some recent paper titles and abstracts. Could you summarize the keywords of high level research backgrounds and insights in this field (related to my profile if possible).'
        'Here is my profile biology: {profile_bio}'
        'Here are the research domains: {domains}'
        'Here are some recent paper titles and abstracts: {papers}'
    )
    brainstorm_idea: str = (
        'Here is a high-level summarized insight of a research field {insights}. '
        'How do you view this field? Do you have any novel ideas or insights? '
        'Please give me 3 to 5 novel ideas and insights in bullet points. Each bullet point should be concise, containing 2 or 3 sentences.'
    )
    discuss_idea: str = (
        'Given a list of research ideas, please summarize them by removing duplicates '
        'and resolving any contradictory ideas by selecting the more reasonable one. '
        'Here are the research ideas:\n{ideas}\n'
    )
    write_paper: str = (
        'Please write a paper based on the following ideas and external data. To save time, you only need to write the abstract. '
        'You might use two or more of these ideas if they are related and works well together. '
        'Here is the idea: {idea}'
        'Here are the external data, which is a list abstracts of related papers: {papers}'
    )
    write_review_summary: str = (
        'Please write a summary of the paper for the following submission you have made to an academic conference.'
        'Here is the submission: {paper}'
    )
    write_review_strength: str = (
        'Please write the strength of the paper for the following submission you have made to an academic conference.'
        'Here is the submission: {paper}'
        'Here is the summary of the paper: {summary}'
    )
    write_review_weakness: str = (
        'Please write the weakness of the paper for the following submission you have made to an academic conference.'
        'Here is the submission: {paper}'
        'Here is the summary of the paper: {summary}'
    )
    write_review_score: str = (
        'Please provide a score for the following submission you have made to an academic conference. The score should be between 1 and 10, where 1 is the lowest and 10 is the highest.'
        'Here is the submission: {paper}'
        'Here is the summary of the paper: {summary}'
        'Here is the strength of the paper: {strength}'
        'Here is the weakness of the paper: {weakness}'
    )
    write_meta_review_summary: str = (
        'Please write a summary of the reviews for the following submission you have made to an academic conference. Here are the reviews from the reviewers. Your summary should summarize the reviews and decisions to help the reviewers to make a decision.'
        'Here is the submission: {paper}'
        'Here are the reviews: {reviews}'
        'Here are the rebuttals: {rebuttals}'
    )
    write_meta_review_strength: str = (
        'Please write the strength of the submission for the following submission you have made to an academic conference. Here are the reviews from the reviewers. Your strength should summarize the reviews and decisions to help the reviewers to make a decision.'
        'Here is the submission: {paper}'
        'Here are the reviews: {reviews}'
        'Here are the rebuttals: {rebuttals}'
        'Here is the summary of the reviews: {summary}'
    )
    write_meta_review_weakness: str = (
        'Please write the weakness of the submission for the following submission you have made to an academic conference. Here are the reviews from the reviewers. Your weakness should summarize the reviews and decisions to help the reviewers to make a decision.'
        'Here is the submission: {paper}'
        'Here are the reviews: {reviews}'
        'Here are the rebuttals: {rebuttals}'
        'Here is the summary of the reviews: {summary}'
    )
    write_meta_review_decision: str = (
        'Please make an review decision to decide whether the following submission should be accepted or rejected by an academic conference. Here are several reviews from reviewers for this submission. Please indicate your review decision as accept or reject.'
        'Here is the submission: {paper}'
        'Here are the reviews: {reviews}'
        'Here are the rebuttals: {rebuttals}'
        'Here is the summary of the reviews: {summary}'
        'Here is the strength of the submission: {strength}'
        'Here is the weakness of the submission: {weakness}'
    )
    write_rebuttal: str = (
        'Please write a rebuttal for the following submission you have made to an academic conference. Here are the reviews and decisions from the reviewers. Your rebuttal should rebut the reviews to convince the reviewers to accept your submission.'
        'Here is the submission: {paper}'
        'Here are the reviews: {review}'
    )
    discuss: str = (
        'Please continue in a conversation with other fellow researchers for me, where you will address their concerns in a scholarly way. '
        'Here are the messages from other researchers: {message}'
    )

    model_config = ConfigDict(
        extra='allow',
    )


class Config(BaseModel):
    param: ParamConfig = ParamConfig()
    prompt_template: PromptTemplateConfig = PromptTemplateConfig()

    model_config = ConfigDict(extra='allow')

    def __init__(self, yaml_config_path: Optional[str] = None, **data: Any) -> None:
        super().__init__(**data)
        if yaml_config_path:
            self.load_from_yaml(yaml_config_path)
        self.check_prompt_template_placeholder()

    def load_from_yaml(self, yaml_config_path: str) -> None:
        with open(yaml_config_path, 'r') as f:
            yaml_cfg: Dict[str, Any] = yaml.safe_load(f)
        self.merge_from_other_cfg(yaml_cfg)
        self.check_prompt_template_placeholder()

    def save_to_yaml(self, yaml_config_path: str) -> None:
        with open(yaml_config_path, 'w') as f:
            yaml.dump(self.model_dump(), f)

    def check_prompt_template_placeholder(self) -> None:
        templates = self.prompt_template.model_dump()
        required_placeholders = {
            'write_bio': [
                '{publication_info}',
            ],
            'find_collaborators': [
                '{max_number}',
                '{self_serialize_all}',
                '{task_serialize_all}',
                '{collaborators_serialize_all}',
            ],
            'review_literature': ['{profile_bio}', '{domains}', '{papers}'],
            'brainstorm_idea': ['{insights}'],
            'discuss_idea': ['{ideas}'],
            'write_paper': ['{idea}', '{papers}'],
            'write_review_summary': ['{paper}'],
            'write_review_strength': ['{paper}', '{summary}'],
            'write_review_weakness': ['{paper}', '{summary}'],
            'write_review_score': ['{paper}', '{summary}', '{strength}', '{weakness}'],
            'write_meta_review_summary': ['{paper}', '{reviews}', '{rebuttals}'],
            'write_meta_review_strength': [
                '{paper}',
                '{reviews}',
                '{rebuttals}',
                '{summary}',
            ],
            'write_meta_review_weakness': [
                '{paper}',
                '{reviews}',
                '{rebuttals}',
                '{summary}',
            ],
            'write_meta_review_decision': [
                '{paper}',
                '{reviews}',
                '{rebuttals}',
                '{summary}',
                '{strength}',
                '{weakness}',
            ],
            'write_rebuttal': ['{paper}', '{review}'],
        }

        for template_name, placeholders in required_placeholders.items():
            template = templates.get(template_name, '')
            for placeholder in placeholders:
                assert (
                    placeholder in template
                ), f"Template '{template_name}' is missing placeholder '{placeholder}'"

    def merge_from_other_cfg(self, other_cfg: Dict[str, Any]) -> None:
        if 'param' in other_cfg:
            updated_param = self.param.model_dump()
            merge_a_into_b(other_cfg['param'], updated_param)
            self.param = ParamConfig(**updated_param)
        if 'prompt_template' in other_cfg:
            updated_template = self.prompt_template.model_dump()
            merge_a_into_b(other_cfg['prompt_template'], updated_template)
            self.prompt_template = PromptTemplateConfig(**updated_template)
