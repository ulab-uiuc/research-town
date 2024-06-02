from yacs.config import CfgNode as CN
from typing import Optional
import yaml

class Config(CN):
    def __init__(self, yaml_config_path: Optional[str] = None) -> None:
        super().__init__()

        self.param = CN()
        self.set_default_params()

        self.prompt_template = CN()
        self.set_default_prompt_templates()

        if yaml_config_path:
            self.load_from_yaml(yaml_config_path)

    def set_default_params(self) -> None:
        self.param = {
            'related_paper_num': 10,
            'base_llm': "mistralai/Mixtral-8x7B-Instruct-v0.1",
            'max_collaborators_num': 3
        }

    def set_default_prompt_templates(self) -> None:
        templates = {
            'read_paper_query': (
                'Given the profile of me, keywords, some recent paper titles and abstracts. '
                'Could you summarize the keywords of high level research backgrounds and insights in this field '
                '(related to my profile if possible). Here is my profile biology: {profile_bio}. '
                'Here are the domains: {domains}'
            ),
            'read_paper_sum': (
                'Given the profile of me, keywords, some recent paper titles and abstracts. '
                'Could you summarize the keywords of high level research backgrounds and insights in this field '
                '(related to my profile if possible). Here is my profile biology: {profile_bio}. '
                'Here are the research domains: {domains}. Here are some recent paper titles and abstracts: {papers}.'
            ),
            'find_collaborators': (
                'Given the name and profile of me, could you find {max_number} collaborators for the following collaboration task? '
                'Here is my profile: {self_serialize_all}, The collaboration task includes: {task_serialize_all}, '
                'Here are a full list of the names and profiles of potential collaborators: {collaborators_serialize_all}, '
                'Generate the collaborator in a list separated by "-" for each collaborator'
            ),
            'think_idea': (
                'Here is a high-level summarized trend of a research field {trend}. How do you view this field? '
                'Do you have any novel ideas or insights? Please give me 3 to 5 novel ideas and insights in bullet points. '
                'Each bullet point should be concise, containing 2 or 3 sentences.'
            ),
            'summarize_research_direction': (
                'Based on the list of the researchers first person persona from different times, please write a comprehensive '
                'first person persona. Focus more on more recent personas. Be concise and clear (around 300 words). '
                'Here are the personas from different times: {personalinfo}'
            ),
            'write_paper': (
                'Please write a paper based on the following ideas and external data. To save time, you only need to write the abstract. '
                'You might use two or more of these ideas if they are related and work well together. Here are the ideas: {ideas}. '
                'Here are the external data, which is a list abstracts of related papers: {papers}'
            ),
            'review_score': (
                'Please provide a score for the following reviews. The score should be between 1 and 10, where 1 is the lowest and 10 is the highest. '
                'Only returns one number score, Here are the reviews: {paper_review}'
            ),
            'review_paper': (
                'Please give some reviews based on the following inputs and external data. You might use two or more of these titles if they are related '
                'and work well together. Here are the external data, which is a list of related papers: {papers}'
            ),
            'write_meta_review': (
                'Please make a review decision to decide whether the following submission should be accepted or rejected by an academic conference. '
                'Here are several reviews from reviewers for this submission. Please indicate your review decision as accept or reject. '
                'Here is the submission: {paper}. Here are the reviews: {reviews}'
            ),
            'write_rebuttal': (
                'Please write a rebuttal for the following submission you have made to an academic conference. Here are the reviews and decisions from the reviewers. '
                'Your rebuttal should rebut the reviews to convince the reviewers to accept your submission. Here is the submission: {paper}. '
                'Here are the reviews: {review}'
            ),
            'discuss': (
                'Please continue in a conversation with other fellow researchers for me, where you will address their concerns in a scholarly way. '
                'Here are the messages from other researchers: {message}'
            ),
        }

        for key, value in templates.items():
            self.prompt_template[key] = value

    def load_from_yaml(self, yaml_config_path) -> None:
        with open(yaml_config_path, 'r') as f:
            yaml_cfg = yaml.safe_load(f)
        self.merge_from_other_cfg(CN(yaml_cfg))

    def save_to_yaml(self, yaml_config_path) -> None:
        with open(yaml_config_path, 'w') as f:
            yaml.dump(self, f)