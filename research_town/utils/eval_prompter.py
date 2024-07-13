from beartype import beartype
from beartype.typing import Dict, List, Optional

from .model_prompting import model_prompting


@beartype
def research_insight_quality_eval_prompting(
    insight: str,
    trend: str,
    model_name: str,
    return_num: Optional[int] = 1,
    max_token_num: Optional[int] = 512,
    temperature: Optional[float] = 0.0,
    top_p: Optional[float] = None,
    stream: Optional[bool] = None,
) -> str:
    prompt_insight = """
    <Instruction> Please evaluate the insight based on the following dimensions, considering the current research trend within the research community. If the research trend field is left blank, please use your common knowledge to assess the trend.  Finally, give an overall score (0-100) and 6 dimension scores (for each dimension, provide a rating (1-10)) as the evaluation for the insight. <Instruction>

    <Input>
    Here is the insight to evaluate: {insight}.
    Here is the research trend: {trend}.
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
    How does it align with or diverge from the innovations highlighted in the trend?
    2. Validity
    Rating (1-10):
    Comments:
    Does it include solid theoretical foundations, robust algorithms, and detailed methodologies?
    Is the method in line with the state-of-the-art techniques noted in the trend?
    Are the underlying principles well-defined and logically consistent?
    Does the insight demonstrate a deep understanding of relevant theories and concepts?
    3. Significance
    Rating (1-10):
    Comments:
    Evaluate the potential impact of the insight on the specific domain of research community that the insight belongs to and beyond.
    How significant is its contribution to advancing the field?
    Does it address high-impact problems or gaps identified in the trend?
    How applicable is it in practical settings and industry contexts?
    4. Feasibility
    Rating (1-10):
    Comments:
    Assess the feasibility of implementing the insight.
    Is it practically applicable in real-world scenarios?
    Does it consider efficiency and scalability, in line with the practical application focus of the trend?
    5. Clarity
    Rating (1-10):
    Comments:
    Assess the clarity, organization, and presentation quality of the insight.
    Is the insight communicated effectively, adhering to high presentation standards seen in top-tier conferences?
    6. Ethical Considerations
    Rating (1-10):
    Comments:
    Consider the ethical implications and societal impact of the insight.
    Does it adhere to the growing emphasis on ethical research practices as highlighted in the trend?
    </Approach>
    """

    input_data = {'insight': insight, 'trend': trend}
    prompt = prompt_insight.format_map(input_data)
    evaluation_result = model_prompting(
        model_name,
        prompt,
        return_num=return_num,
        max_token_num=max_token_num,
        temperature=temperature,
        top_p=top_p,
        stream=stream,
    )
    # merge results from List[Str] to Str
    combined_result = '\n'.join(evaluation_result)

    return combined_result


@beartype
def research_idea_quality_eval_prompting(
    idea: str,
    trend: str,
    model_name: str,
    return_num: Optional[int] = 1,
    max_token_num: Optional[int] = 512,
    temperature: Optional[float] = 0.0,
    top_p: Optional[float] = None,
    stream: Optional[bool] = None,
) -> str:
    prompt_idea = """
    <Instruction> Please evaluate the idea based on the following dimensions, considering the current research trend within the research community. If the research trend field is left blank, please use your common knowledge to assess the trend.  Finally, give an overall score (0-100) and 6 dimension scores (for each dimension, provide a rating (1-10)) as the evaluation for the idea. <Instruction>

    <Input>
    Here is the idea to evaluate: {idea}.
    Here is the research trend: {trend}.
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
    How does it align with or diverge from the innovations highlighted in the trend?
    2. Validity
    Rating (1-10):
    Comments:
    Does it include solid theoretical foundations, robust algorithms, and detailed methodologies?
    Is the method in line with the state-of-the-art techniques noted in the trend?
    Are the underlying principles well-defined and logically consistent?
    Does the idea demonstrate a deep understanding of relevant theories and concepts?
    3. Significance
    Rating (1-10):
    Comments:
    Evaluate the potential impact of the idea on the specific domain of research community that the idea belongs to and beyond.
    How significant is its contribution to advancing the field?
    Does it address high-impact problems or gaps identified in the trend?
    How applicable is it in practical settings and industry contexts?
    4. Feasibility
    Rating (1-10):
    Comments:
    Assess the feasibility of implementing the idea.
    Is it practically applicable in real-world scenarios?
    Does it consider efficiency and scalability, in line with the practical application focus of the trend?
    5. Clarity
    Rating (1-10):
    Comments:
    Assess the clarity, organization, and presentation quality of the idea.
    Is the idea communicated effectively, adhering to high presentation standards seen in top-tier conferences?
    6. Ethical Considerations
    Rating (1-10):
    Comments:
    Consider the ethical implications and societal impact of the idea.
    Does it adhere to the growing emphasis on ethical research practices as highlighted in the trend?
    </Approach>
    """

    input_data = {'idea': idea, 'trend': trend}
    prompt = prompt_idea.format_map(input_data)
    evaluation_result = model_prompting(
        model_name,
        prompt,
        return_num=return_num,
        max_token_num=max_token_num,
        temperature=temperature,
        top_p=top_p,
        stream=stream,
    )
    # merge results from List[Str] to Str
    combined_result = '\n'.join(evaluation_result)

    return combined_result


@beartype
def research_paper_submission_quality_eval_prompting(
    idea: str,
    paper: Dict[str, str],
    model_name: str,
    trend: Optional[str] = None,
    return_num: Optional[int] = 1,
    max_token_num: Optional[int] = 512,
    temperature: Optional[float] = 0.0,
    top_p: Optional[float] = None,
    stream: Optional[bool] = None,
) -> str:
    # refer to idea eval, but replace those not needed, and paraphrase those have overlaps.
    paper_prompt = """
    <Instruction> Please evaluate the paper draft based on the following dimensions. Finally, give an overall score (0-100) and 6 dimension scores (for each dimension, provide a rating (1-10)) as the evaluation for the draft.
    <Instruction>

    <Input>
    Here is the paper draft to evaluate:
    Title: {title}
    Abstract: {abstract}
    Idea: {idea}
    Research Trend: {trend}
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
    How does it align with or diverge from the innovations highlighted in the trend?
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

    input_data = {
        'idea': idea,
        'title': paper['title'],
        'abstract': paper['abstract'],
        'trend': trend if trend is not None else '',  # Provide default value if None
    }
    prompt = paper_prompt.format_map(input_data)
    evaluation_result = model_prompting(
        model_name,
        prompt,
        return_num=return_num,
        max_token_num=max_token_num,
        temperature=temperature,
        top_p=top_p,
        stream=stream,
    )
    # merge results from List[Str] to Str
    combined_result = '\n'.join(evaluation_result)

    return combined_result


def research_review_for_paper_submission_quality_eval_prompting(
    idea: str,
    trend: str,
    paper: Dict[str, str],
    review: List[str],
    model_name: str,
    return_num: Optional[int] = 1,
    max_token_num: Optional[int] = 512,
    temperature: Optional[float] = 0.0,
    top_p: Optional[float] = None,
    stream: Optional[bool] = None,
) -> str:
    review_prompt = """
    <Instruction>
    Please evaluate the review based on the following dimensions. You only need to give an overall score (0-100) and 10 dimension scores (for each dimension, provide a rating (1-10)) as the evaluation for the review. For these components are left blank(for example: rebutal, meta_review, etc), please provide your common knowledge to assess the review. You must give a overall score with dimension scores. No detailed anaylsis is needed.
    </Instruction>

    <Input>
    Here is the review to evaluate:
    idea: {idea}
    research trend: {trend}
    paper: title-- {title}; abstract-- {abstract}.
    reviews: {review}
    </Input>

    <Output>
    Output format:
    The output format should follow these rules: Overall Score of a review (0-100), with 10 Dimension Scores: [d1, d2, d3, ..., d10], where di is the score of the i-th dimension. An example of output is: Overall Score=91. Dimension Scores=[9,9,9,9,9,9,9,9,9,10].
    </Output>

    <Approach> The details of rating are as follows:
    {regulations}
    </Approach>
    """

    regulations = """
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
    """

    # Organize the reviews
    organized_reviews = '\n'.join(
        [f"Reviewer {i+1}'s comment: {review[i]}" for i in range(len(review))]
    )
    input_data = {
        'regulations': regulations,
        'idea': idea,
        'trend': trend,
        'title': paper['title'],
        'abstract': paper['abstract'],
        'review': organized_reviews,
    }
    prompt = review_prompt.format_map(input_data)
    evaluation_result = model_prompting(
        model_name,
        prompt,
        return_num=return_num,
        max_token_num=max_token_num,
        temperature=temperature,
        top_p=top_p,
        stream=stream,
    )
    # merge results from List[Str] to Str
    combined_result = '\n'.join(evaluation_result)

    return combined_result


def research_rebuttal_for_paper_submission_quality_eval_prompting(
    idea: str,
    trend: str,
    paper: Dict[str, str],
    review: List[str],
    model_name: str,
    rebuttal: Optional[str] = None,
    return_num: Optional[int] = 1,
    max_token_num: Optional[int] = 512,
    temperature: Optional[float] = 0.0,
    top_p: Optional[float] = None,
    stream: Optional[bool] = None,
) -> str:
    rebuttal_prompt = """
    <Instruction>
    Please evaluate the rebuttal based on the following dimensions. Finally, give an overall score (0-100) and 10 dimension scores (for each dimension, provide a rating (1-10)) as the evaluation for the review.
    </Instruction>

    <Input>
    Here is the review to evaluate:
    idea: {idea}
    research trend: {trend}
    paper: title-- {title}; abstract-- {abstract}.
    reviews: {review}
    rebutal: {rebuttal}
    </Input>

    <Output>
    Output format:
    The output format should follow these rules: Overall Score of a review (0-100), with 10 Dimension Scores: [d1, d2, d3, ..., d10], where di is the score of the i-th dimension. An example of output is: Overall Score=91. Dimension Scores=[9,9,9,9,9,9,9,9,9,10].
    </Output>

    <Approach> The details of rating are as follows:
    {regulations}
    </Approach>
    """

    regulations = """
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
    """

    # Organize the reviews
    organized_reviews = '\n'.join(
        [f"Reviewer {i+1}'s comment: {review[i]}" for i in range(len(review))]
    )
    input_data = {
        'regulations': regulations,
        'idea': idea,
        'trend': trend,
        'title': paper['title'],
        'abstract': paper['abstract'],
        'review': organized_reviews,
        'rebuttal': rebuttal if rebuttal is not None else '',
    }
    prompt = rebuttal_prompt.format_map(input_data)
    evaluation_result = model_prompting(
        model_name,
        prompt,
        return_num=return_num,
        max_token_num=max_token_num,
        temperature=temperature,
        top_p=top_p,
        stream=stream,
    )
    # merge results from List[Str] to Str
    combined_result = '\n'.join(evaluation_result)

    return combined_result


def research_meta_review_for_paper_submission_quality_eval_prompting(
    idea: str,
    trend: str,
    paper: Dict[str, str],
    review: List[str],
    decision: str,
    model_name: str,
    rebuttal: Optional[str] = None,
    meta_review: Optional[str] = None,
    return_num: Optional[int] = 1,
    max_token_num: Optional[int] = 512,
    temperature: Optional[float] = 0.0,
    top_p: Optional[float] = None,
    stream: Optional[bool] = None,
) -> str:
    meta_review_prompt = """
    <Instruction>
    Please evaluate the review based on the following dimensions. Finally, give an overall score (0-100) and 10 dimension scores (for each dimension, provide a rating (1-10)) as the evaluation for the review.
    </Instruction>

    <Input>
    Here is the review to evaluate:
    idea: {idea}
    research trend: {trend}
    paper: title-- {title}; abstract-- {abstract}.
    reviews: {review}
    rebutal: {rebuttal}
    meta_review: {meta_review}
    final_decision:{final_decision}
    </Input>

    <Output>
    Output format:
    The output format should follow these rules: Overall Score of a review (0-100), with 10 Dimension Scores: [d1, d2, d3, ..., d10], where di is the score of the i-th dimension. An example of output is: Overall Score=91. Dimension Scores=[9,9,9,9,9,9,9,9,9,10].
    </Output>

    <Approach> The details of rating are as follows:
    {regulations}
    </Approach>
    """

    regulations = """
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
    """

    # Organize the reviews
    organized_reviews = '\n'.join(
        [f"Reviewer {i+1}'s comment: {review[i]}" for i in range(len(review))]
    )
    input_data = {
        'regulations': regulations,
        'idea': idea,
        'trend': trend,
        'title': paper['title'],
        'abstract': paper['abstract'],
        'review': organized_reviews,
        'rebuttal': rebuttal if rebuttal is not None else '',
        'meta_review': meta_review if meta_review is not None else '',
        'final_decision': decision,
    }
    prompt = meta_review_prompt.format_map(input_data)
    evaluation_result = model_prompting(
        model_name,
        prompt,
        return_num=return_num,
        max_token_num=max_token_num,
        temperature=temperature,
        top_p=top_p,
        stream=stream,
    )
    # merge results from List[Str] to Str
    combined_result = '\n'.join(evaluation_result)

    return combined_result
