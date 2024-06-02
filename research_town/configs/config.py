from beartype.typing import Optional, MutableMapping, Union, Dict, Any
import yaml

# Define the specific type for the nested dictionaries
NestedDictType = Dict[str, Any]

def merge_a_into_b(a: Dict[str, Any], b: Dict[str, Any]) -> None:
    """
    Merge dictionary a into dictionary b recursively.
    """
    for key, value in a.items():
        if isinstance(value, dict) and key in b and isinstance(b[key], dict):
            merge_a_into_b(value, b[key])
        else:
            b[key] = value

class ConfigDict(Dict[str, Any]):
    def __getattr__(self, attr: str) -> Any:
        try:
            value = self[attr]
            return value
        except KeyError:
            raise AttributeError(f"No such attribute: {attr}")

    def __setattr__(self, key: str, value: Any) -> None:
        self[key] = value

    def __delattr__(self, item: str) -> None:
        del self[item]

class Config(object):
    def __init__(self, yaml_config_path: Optional[str] = None) -> None:
        super().__init__()

        # Initialize default parameters and prompt templates
        self.param = ConfigDict()
        self.set_default_params()
        self.prompt_template = ConfigDict()
        self.set_default_prompt_templates()

        if yaml_config_path:
            self.load_from_yaml(yaml_config_path)

        # Perform any necessary checks on the loaded configuration
        self.check_prompt_template_placeholder()

    def set_default_params(self) -> None:
        param: NestedDictType = {
            'related_paper_num': 10,
            'base_llm': 'mistralai/Mixtral-8x7B-Instruct-v0.1',
            'max_collaborators_num': 3,
        }
        self.param.update(param)

    def set_default_prompt_templates(self) -> None:
        templates: NestedDictType = {
            'find_collaborators': (
                'Given the name and profile of me, could you find {max_number} collaborators for the following collaboration task?'
                'Here is my profile: {self_serialize_all}'
                'The collaboration task include: {task_serialize_all}'
                'Here are a full list of the names and profiles of potential collaborators: {collaborators_serialize_all}'
                "Generate the collaborator in a list separated by '-' for each collaborator"
            ),
            'query_paper': (
                'Given the profile of me, keywords, some recent paper titles and abstracts. Could you summarize the keywords of high level research backgrounds and insights in this field (related to my profile if possible).'
                'Here is my profile biology: {profile_bio}'
                'Here are the domains: {domains}'
            ),
            'read_paper': (
                'Given the profile of me, keywords, some recent paper titles and abstracts. Could you summarize the keywords of high level research backgrounds and insights in this field (related to my profile if possible).'
                'Here is my profile biology: {profile_bio}'
                'Here are the research domains: {domains}'
                'Here are some recent paper titles and abstracts: {papers}'
            ),
            'think_idea': (
                'Here is a high-level summarized insight of a research field {insights}. '
                'How do you view this field? Do you have any novel ideas or insights? '
                'Please give me 3 to 5 novel ideas and insights in bullet points. Each bullet point should be concise, containing 2 or 3 sentences.'
            ),
            'summarize_idea': (
                'Given a list of research ideas, please summarize them by removing duplicates '
                'and resolving any contradictory ideas by selecting the more reasonable one. '
                'Here are the research ideas:\n{ideas}\n'
            ),
            'write_paper': (
                'Please write a paper based on the following ideas and external data. To save time, you only need to write the abstract. '
                'You might use two or more of these ideas if they are related and works well together. '
                'Here is the idea: {idea}'
                'Here are the external data, which is a list abstracts of related papers: {papers}'
            ),
            'review_score': (
                'Please provide a score for the following reviews. The score should be between 1 and 10, where 1 is the lowest and 10 is the highest. Only returns one number score.'
                'Here are the reviews: {paper_review}'
            ),
            'review_paper': (
                'Please give some reviews based on the following inputs and external data.'
                'You might use two or more of these titles if they are related and works well together.'
                'Here are the external data, which is a list of related papers: {papers}'
            ),
            'write_meta_review': (
                'Please make an review decision to decide whether the following submission should be accepted or rejected by an academic conference. Here are several reviews from reviewers for this submission. Please indicate your review decision as accept or reject.'
                'Here is the submission: {paper}'
                'Here are the reviews: {reviews}'
            ),
            'write_rebuttal': (
                'Please write a rebuttal for the following submission you have made to an academic conference. Here are the reviews and decisions from the reviewers. Your rebuttal should rebut the reviews to convince the reviewers to accept your submission.'
                'Here is the submission: {paper}'
                'Here are the reviews: {review}'
            ),
            'discuss': (
                'Please continue in a conversation with other fellow researchers for me, where you will address their concerns in a scholarly way. '
                'Here are the messages from other researchers: {message}'
            )
        }
        self.prompt_template.update(templates)

    def load_from_yaml(self, yaml_config_path: str) -> None:
        with open(yaml_config_path, 'r') as f:
            yaml_cfg: NestedDictType = yaml.safe_load(f)
        self.merge_from_other_cfg(ConfigDict(yaml_cfg))

    def save_to_yaml(self, yaml_config_path: str) -> None:
        with open(yaml_config_path, 'w') as f:
            yaml.dump(self.to_dict(), f)

    def to_dict(self) -> NestedDictType:
        """
        Convert the Config object to a dictionary.
        """
        result: NestedDictType = {}
        for attr in vars(self):
            value = getattr(self, attr)
            if isinstance(value, ConfigDict):
                result[attr] = dict(value)
            else:
                result[attr] = value
        return result

    def check_prompt_template_placeholder(self) -> None:
        templates = self.prompt_template
        required_placeholders = {
            'find_collaborators': ['{max_number}', '{self_serialize_all}', '{task_serialize_all}', '{collaborators_serialize_all}'],
            'query_paper': ['{profile_bio}', '{domains}'],
            'read_paper': ['{profile_bio}', '{domains}', '{papers}'],
            'think_idea': ['{insights}'],
            'summarize_idea': ['{ideas}'],
            'write_paper': ['{idea}', '{papers}'],
            'review_score': ['{paper_review}'],
            'review_paper': ['{papers}'],
            'write_meta_review': ['{paper}', '{reviews}'],
            'write_rebuttal': ['{paper}', '{review}'],
            'discuss': ['{message}'],
        }

        for template_name, placeholders in required_placeholders.items():
            template = templates.get(template_name, "")
            for placeholder in placeholders:
                assert placeholder in template, f"Template '{template_name}' is missing placeholder '{placeholder}'"

    def merge_from_other_cfg(self, other_cfg: ConfigDict) -> None:
        for attr, value in other_cfg.items():
            if isinstance(value, dict):
                if hasattr(self, attr) and isinstance(getattr(self, attr), ConfigDict):
                    merge_a_into_b(value, getattr(self, attr))
                else:
                    setattr(self, attr, ConfigDict(value))
            else:
                setattr(self, attr, value)
