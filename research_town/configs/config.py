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


class EvalPromptTemplateConfig(BaseModel):
    insight_quality: str = """
    <Instruction> Please evaluate the insight based on the following dimensions, considering the current research insights within the research community. If the research insights field is left blank, please use your common knowledge to assess the insights.  Finally, give an overall score (0-100) and 6 dimension scores (for each dimension, provide a rating (1-10)) as the evaluation for the insight. <Instruction>

    <Input>
    Here is the insight to evaluate: {insight}.
    </Input>

    <Output>
    The output format should follow these rules: Overall Score of an insight (0-100), with 6 Dimension Scores: [d1, d2, d3, ..., d6], where di is the score of the i-th dimension. An example of output is: Overall Score=89 Dimension Scores=[8,9,9,9,9,9].'
    </Output>

    <Approach> The details of rating are as follow:
    1. Novelty
    Rating (1-10):
    Comments:
    How original and unique is the insight?
    Does it introduce a new perspective or significant advancement compared to existing methods?
    How does it align with or diverge from the innovations highlighted in the insights?
    2. Validity
    Rating (1-10):
    Comments:
    Does it include solid theoretical foundations, robust algorithms, and detailed methodologies?
    Is the method in line with the state-of-the-art techniques noted in the insights?
    Are the underlying principles well-defined and logically consistent?
    Does the insight demonstrate a deep understanding of relevant theories and concepts?
    3. Significance
    Rating (1-10):
    Comments:
    Evaluate the potential impact of the insight on the specific domain of research community that the insight belongs to and beyond.
    How significant is its contribution to advancing the field?
    Does it address high-impact problems or gaps identified in the insights?
    How applicable is it in practical settings and industry contexts?
    4. Feasibility
    Rating (1-10):
    Comments:
    Assess the feasibility of implementing the insight.
    Is it practically applicable in real-world scenarios?
    Does it consider efficiency and scalability, in line with the practical application focus of the insights?
    5. Clarity
    Rating (1-10):
    Comments:
    Assess the clarity, organization, and presentation quality of the insight.
    Is the insight communicated effectively, adhering to high presentation standards seen in top-tier conferences?
    6. Ethical Considerations
    Rating (1-10):
    Comments:
    Consider the ethical implications and societal impact of the insight.
    Does it adhere to the growing emphasis on ethical research practices as highlighted in the insights?
    </Approach>
    """

    idea_quality: str = """
    <Instruction> Please evaluate the idea based on the following dimensions, considering the current research insights within the research community. If the research insights field is left blank, please use your common knowledge to assess the insights.  Finally, give an overall score (0-100) and 6 dimension scores (for each dimension, provide a rating (1-10)) as the evaluation for the idea. <Instruction>

    <Input>
    Here is the idea to evaluate: {idea}.
    Here is the research insights: {insights}.
    </Input>

    <Output>
    The output format should follow these rules: Overall Score of an idea (0-100), with 6 Dimension Scores: [d1, d2, d3, ..., d6], where di is the score of the i-th dimension. An example of output is: Overall Score=89 Dimension Scores=[8,9,9,9,9,9].'
    </Output>

    <Approach> The details of rating are as follow:
    1. Novelty
    Rating (1-10):
    Comments:
    How original and unique is the idea?
    Does it introduce a new perspective or significant advancement compared to existing methods?
    How does it align with or diverge from the innovations highlighted in the insights?
    2. Validity
    Rating (1-10):
    Comments:
    Does it include solid theoretical foundations, robust algorithms, and detailed methodologies?
    Is the method in line with the state-of-the-art techniques noted in the insights?
    Are the underlying principles well-defined and logically consistent?
    Does the idea demonstrate a deep understanding of relevant theories and concepts?
    3. Significance
    Rating (1-10):
    Comments:
    Evaluate the potential impact of the idea on the specific domain of research community that the idea belongs to and beyond.
    How significant is its contribution to advancing the field?
    Does it address high-impact problems or gaps identified in the insights?
    How applicable is it in practical settings and industry contexts?
    4. Feasibility
    Rating (1-10):
    Comments:
    Assess the feasibility of implementing the idea.
    Is it practically applicable in real-world scenarios?
    Does it consider efficiency and scalability, in line with the practical application focus of the insights?
    5. Clarity
    Rating (1-10):
    Comments:
    Assess the clarity, organization, and presentation quality of the idea.
    Is the idea communicated effectively, adhering to high presentation standards seen in top-tier conferences?
    6. Ethical Considerations
    Rating (1-10):
    Comments:
    Consider the ethical implications and societal impact of the idea.
    Does it adhere to the growing emphasis on ethical research practices as highlighted in the insights?
    </Approach>
    """

    paper_quality: str = """
    <Instruction> Please evaluate the paper draft based on the following dimensions. Finally, give an overall score (0-100) and 6 dimension scores (for each dimension, provide a rating (1-10)) as the evaluation for the draft.
    <Instruction>

    <Input>
    Here is the paper draft to evaluate:
    paper: {paper}
    Idea: {idea}
    Insights: {insights}
    </Input>

    <Output>
    The output format should follow these rules: Overall Score of an idea (0-100), with 6 Dimension Scores: [d1, d2, d3, ..., d6], where di is the score of the i-th dimension. An example of output is: Overall Score=89 Dimension Scores=[8,9,9,9,9,9].'
    </Output>

    <Approach> The details of rating are as follow:
    1. Novelty
    Rating (1-10):
    Comments:
    Does it paper introduce a novel problem or new perspective that has not been explored before?
    Does it introduce a new techniques or significant advancement compared to existing methods?
    How does it align with or diverge from the innovations highlighted in the insights?
    2. Validity
    Rating (1-10):
    Comments:
    Does it include solid theoretical foundations, robust algorithms, and detailed methodologies in addressing the research problem?
    Are the underlying principles well-defined and logically consistent?
    3. Significance
    Rating (1-10):
    Comments:
    Evaluate the potential contribution and impact of the paper on the specific domain of research community that the paper belongs to and beyond.
    How does it compare to existing works in terms of impact?
    4. Rigorousness
    Rating (1-10):
    Comments:
    Are the research design and methods clearly described and justified?
    Is the methodology robust and suitable for addressing the research questions?
    Are the results well-analyzed and interpreted?
    Do the findings support the claims made in the paper?
    5. Clarity
    Rating (1-10):
    Comments:
    Evaluate the clarity, organization, and presentation quality of the paper.
    How well do the title and abstract summarize the paper? Are they clear, concise, and informative?
    Does it effectively convey the significance and main contributions of the paper?
    How well do the title and abstract align with each other? Do they accurately represent the core idea and content of the paper?
    Is the content well-structured and easy to follow?
    6. Ethical Considerations
    Rating (1-10):
    Comments:
    Consider the ethical implications and societal impact of the paper.
    Does it adhere to ethical guidelines and responsible research practices?
    Are potential negative consequences or biases addressed?
    </Approach>
    """

    review_quality: str = """
    <Instruction>
    Please evaluate the review based on the following dimensions. You only need to give an overall score (0-100) and 10 dimension scores (for each dimension, provide a rating (1-10)) as the evaluation for the review. For these components are left blank(for example: rebutal, meta_review, etc), please provide your common knowledge to assess the review. You must give a overall score with dimension scores. No detailed anaylsis is needed.
    </Instruction>

    <Input>
    Here is the review to evaluate:
    idea: {idea}
    research insights: {insights}
    paper: {paper}
    review: {review}
    </Input>

    <Output>
    Output format:
    The output format should follow these rules: Overall Score of a review (0-100), with 10 Dimension Scores: [d1, d2, d3, ..., d10], where di is the score of the i-th dimension. An example of output is: Overall Score=91. Dimension Scores=[9,9,9,9,9,9,9,9,9,10].
    </Output>

    <Approach> The details of rating are as follows:
    1. Summarization
        - Rating (1-10):
        - Comments:
        - Does the review accurately summarize the paper's motivation?
        - Are the key contributions and achievements clearly summarized?
        - Are there any misunderstandings that need to be addressed in the author's response?

    2. Strengths
        - Rating (1-10):
        - Comments:
        - Are the strengths of the work clearly described?
        - Are the claims sound, both theoretically and empirically?
        - Is the contribution significant and novel?
        - Is the work relevant to the community?

    3. Weaknesses
        - Rating (1-10):
        - Comments:
        - Are the limitations of the work clearly explained?
        - Are the weaknesses addressed along the same axes as the strengths?
        - Are the criticisms detailed, specific, and polite?

    4. Correctness
        - Rating (1-10):
        - Comments:
        - Are the claims and methods correct?
        - Is the empirical methodology sound?
        - Are there any incorrect claims or methods detailed thoroughly?
        - Is the criticism well-motivated and understandable?

    5. Clarity
        - Rating (1-10):
        - Comments:
        - Is the paper well-written?
        - Is the exposition of the paper clear?
        - What parts of the paper need revision to improve clarity?

    6. Originality
        - Rating (1-10):
        - Comments:
        - Is it clearly discussed how this work differs from previous contributions?
        - Does the submission show due scholarship, relating the proposed work to prior work?
        - Does the related work section explain how the proposed work differs from prior literature?

    7. Reproducibility
        - Rating (1-10):
        - Comments:
        - Are there enough details to reproduce the major results of this work?
        - Is the work reasonably reproducible?
        - If not, are the reproducibility issues listed among the weaknesses?

    8. Significance
        - Rating (1-10):
        - Comments:
        - Have the authors adequately addressed the broader impact of their work?
        - Are potential negative ethical and societal implications considered?

    9. Ethical Considerations
        - Rating (1-10):
        - Comments:
        - Does the submission raise potential ethical concerns?
        - Are there methods, applications, or data that create or reinforce unfair bias?
        - Does the work have a primary purpose of harm or injury?

    10. Fairness
        - Rating (1-10):
        - Comments:
        - Are the review scores distributed fairly?
        - Is there a balance in the scoring, without significant bias towards extremely high or low scores?
        - Do the scores reflect a reasonable and unbiased assessment of the paper?
    </Approach>
    """

    rebuttal_quality: str = """
    <Instruction>
    Please evaluate the rebuttal based on the following dimensions. Finally, give an overall score (0-100) and 10 dimension scores (for each dimension, provide a rating (1-10)) as the evaluation for the review.
    </Instruction>

    <Input>
    Here is the review to evaluate:
    research insights: {insights}
    idea: {idea}
    paper: {paper}
    reviews: {review}
    rebutal: {rebuttal}
    </Input>

    <Output>
    Output format:
    The output format should follow these rules: Overall Score of a review (0-100), with 10 Dimension Scores: [d1, d2, d3, ..., d10], where di is the score of the i-th dimension. An example of output is: Overall Score=91. Dimension Scores=[9,9,9,9,9,9,9,9,9,10].
    </Output>

    <Approach> The details of rating are as follows:
    1. Clarity of Response
        - Rating (1-10):
        - Comments:
        - Is the rebuttal clear in addressing the criticisms raised in the reviews?
        - Are the responses to each criticism well-structured and understandable?

    2. Accuracy and Justification
        - Rating (1-10):
        - Comments:
        - Are the rebuttal claims and justifications adequately supported by evidence?
        - Are any disagreements or discrepancies with the reviews addressed convincingly?

    3. Responsiveness
        - Rating (1-10):
        - Comments:
        - Does the rebuttal address all major concerns and critiques raised in the reviews?
        - Are the rebuttal responses thorough and comprehensive?

    4. Persuasiveness
        - Rating (1-10):
        - Comments:
        - How persuasive are the arguments and explanations provided in the rebuttal?
        - Are the rebuttal responses effective in mitigating concerns and defending the paper?

    5. Professionalism
        - Rating (1-10):
        - Comments:
        - Is the tone and language of the rebuttal professional and respectful?
        - Are there any instances of defensive or dismissive language that need improvement?

    6. Insightfulness
        - Rating (1-10):
        - Comments:
        - Does the rebuttal provide new insights or perspectives that were not fully addressed in the original paper or reviews?

    7. Overall Improvement
        - Rating (1-10):
        - Comments:
        - How much does the rebuttal improve the overall perception and understanding of the paper's strengths and weaknesses?

    8. Clarity of Contributions
        - Rating (1-10):
        - Comments:
        - Are the contributions of the paper clarified and emphasized in the rebuttal?

    9. Ethical Considerations
        - Rating (1-10):
        - Comments:
        - Are there any ethical implications or considerations raised in the rebuttal?

    10. Balance and Fairness
        - Rating (1-10):
        - Comments:
        - Does the rebuttal acknowledge both strengths and weaknesses of the paper in a balanced manner?
        - Is there fairness in addressing criticisms without bias?
    </Approach>
    """

    meta_review_quality: str = """
    <Instruction>
    Please evaluate the review based on the following dimensions. Finally, give an overall score (0-100) and 10 dimension scores (for each dimension, provide a rating (1-10)) as the evaluation for the review.
    </Instruction>

    <Input>
    Here is the review to evaluate:
    research insights: {insights}
    idea: {idea}
    paper: {paper}
    reviews: {reviews}
    rebutals: {rebuttals}
    meta_review: {meta_review}
    </Input>

    <Output>
    Output format:
    The output format should follow these rules: Overall Score of a review (0-100), with 10 Dimension Scores: [d1, d2, d3, ..., d10], where di is the score of the i-th dimension. An example of output is: Overall Score=91. Dimension Scores=[9,9,9,9,9,9,9,9,9,10].
    </Output>

    <Approach> The details of rating are as follows:
    1. Summarization
        - Rating (1-10):
        - Comments:
        - Does the meta-review accurately summarize the strengths and weaknesses of the original reviews?
        - Are the key points of each review clearly and succinctly summarized?
        - Are any discrepancies or misunderstandings among the reviews identified and addressed?

    2. Quality
        - Rating (1-10):
        - Comments:
        - Are the strengths and weaknesses of the reviewed paper clearly identified and appropriately critiqued?
        - Do the critiques show a deep understanding of the paper's content and contributions?
        - Are the assessments fair and balanced?

    3. Consistency and Fairness
        - Rating (1-10):
        - Comments:
        - Is there consistency in evaluating different aspects of the reviewed paper across the reviews?
        - Are the assessments fair, avoiding significant bias towards any particular aspect of the paper?
        - Are any conflicting opinions among the reviews reconciled appropriately?

    4. Constructiveness
        - Rating (1-10):
        - Comments:
        - Are the critiques and suggestions provided in the meta-review constructive and actionable?
        - Do they offer meaningful insights for improving the reviewed paper or future revisions?
        - Are the recommendations clear and well-supported by evidence from the reviews?

    5. Clarity
        - Rating (1-10):
        - Comments:
        - Is the meta-review well-written and logically organized?
        - Are the points expressed clearly and effectively?
        - Is the language appropriate and professional?

    6. Insightfulness
        - Rating (1-10):
        - Comments:
        - Does the meta-review provide insightful commentary beyond summarizing individual reviews?
        - Are there novel observations or perspectives that enrich the understanding of the reviewed paper?

    7. Alignment with Review Criteria
        - Rating (1-10):
        - Comments:
        - Does the meta-review align with the evaluation criteria provided by the submission guidelines?
        - Are all relevant aspects of the reviewed paper adequately covered in the meta-review?

    8. Justification of Final Decision
        - Rating (1-10):
        - Comments:
        - Is the final decision or recommendation based on a thorough analysis of the reviews?
        - Are the reasons for the recommendation clearly articulated and justified?

    9. Ethical Considerations
        - Rating (1-10):
        - Comments:
        - Are there any ethical considerations raised in the meta-review regarding the reviewed paper or its reviews?
        - Are potential biases or conflicts of interest addressed appropriately?

    10. Overall Impression
        - Rating (1-10):
        - Comments:
        - What is your overall impression of the meta-review?
        - Does it meet the standards expected for a meta-review in terms of thoroughness, insightfulness, and clarity?
    </Approach>
    """

    model_config = ConfigDict(
        extra='allow',
    )


class AgentPromptTemplateConfig(BaseModel):
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
    agent_prompt_template: AgentPromptTemplateConfig = AgentPromptTemplateConfig()
    eval_prompt_template: EvalPromptTemplateConfig = EvalPromptTemplateConfig()

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
        if 'agent_prompt_template' in other_cfg:
            updated_template = self.prompt_template.model_dump()
            merge_a_into_b(other_cfg['prompt_template'], updated_template)
            self.prompt_template = AgentPromptTemplateConfig(**updated_template)
        if 'eval_prompt_template' in other_cfg:
            updated_template = self.prompt_template.model_dump()
            merge_a_into_b(other_cfg['prompt_template'], updated_template)
            self.prompt_template = EvalPromptTemplateConfig(**updated_template)
