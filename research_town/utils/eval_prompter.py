from typing import Dict, List

from beartype import beartype

from .model_prompting import model_prompting


@beartype
def idea_quality_eval_prompting(
    idea: str,
    trend:  str,
    model_name: str,
) -> str:
    prompt_idea = (
    "<Instruction> Please evaluate the idea based on the following dimensions, considering the current research trend within the ML community. If the research trend field is left blank, please use your common knowledge to assess the trend.  Finally, give an overall score (0-100) and 10 dimension scores (for each dimension, provide a rating (1-10)) as the evaluation for the idea. The output format should follow these rules: Overall Score of an idea (0-100), with 10 Dimension Scores: [d1, d2, d3, ..., d10], where di is the score of the i-th dimension. An example of output is: 'Overall Score=89. Dimension Scores=[8,9,9,9,9,9,9,9,9,9]'.<Instruction>\n"
    "<Approach> The details of rating are as follow:\n"
    "1. Novelty\n"
    "Rating (1-10):\n"
    "Comments:\n"
    "How original and unique is the idea?\n"
    "Does it introduce a new perspective or significant advancement compared to existing methods?\n"
    "How does it align with or diverge from the innovations highlighted in the trend?\n"
    "2. Technical Depth\n"
    "Rating (1-10):\n"
    "Comments:\n"
    "Assess the technical rigor of the idea.\n"
    "Does it include solid theoretical foundations, robust algorithms, and detailed methodologies?\n"
    "Is the technical depth in line with the state-of-the-art techniques noted in the trend?\n"
    "3. Impact and Significance\n"
    "Rating (1-10):\n"
    "Comments:\n"
    "Evaluate the potential impact of the idea on the ML community and beyond.\n"
    "How significant is its contribution to advancing the field?\n"
    "Does it address high-impact problems or gaps identified in the trend?\n"
    "4. Feasibility and Practicality\n"
    "Rating (1-10):\n"
    "Comments:\n"
    "Assess the feasibility of implementing the idea.\n"
    "Is it practically applicable in real-world scenarios?\n"
    "Does it consider efficiency and scalability, in line with the practical application focus of the trend?\n"
    "5. Theoretical Foundation and Conceptual Soundness\n"
    "Rating (1-10):\n"
    "Comments:\n"
    "Evaluate the theoretical foundation and conceptual soundness of the idea.\n"
    "Are the underlying principles well-defined and logically consistent?\n"
    "Does the idea demonstrate a deep understanding of relevant theories and concepts?\n"
    "How does it contribute to advancing theoretical understanding within the field?\n"
    "6. Clarity and Presentation\n"
    "Rating (1-10):\n"
    "Comments:\n"
    "Assess the clarity, organization, and presentation quality of the idea.\n"
    "Is the idea communicated effectively, adhering to high presentation standards seen in top-tier ML conferences?\n"
    "7. Potential for Real-world Applications\n"
    "Rating (1-10):\n"
    "Comments:\n"
    "Evaluate the potential of the idea to be applied in real-world scenarios.\n"
    "How applicable is it in practical settings and industry contexts?\n"
    "Does it address real-world problems or challenges identified in the trend?\n"
    "8. Innovation Potential\n"
    "Rating (1-10):\n"
    "Comments:\n"
    "Assess the potential of the idea to inspire further research and innovation within the ML community.\n"
    "Does it open up new avenues for research or provide a novel framework aligning with the emerging trends and future directions of the trend?\n"
    "9. Ethical Considerations\n"
    "Rating (1-10):\n"
    "Comments:\n"
    "Consider the ethical implications and societal impact of the idea.\n"
    "Does it adhere to the growing emphasis on ethical AI and responsible ML practices as highlighted in the trend?\n"
    "10. Interdisciplinary Connections\n"
    "Rating (1-10):\n"
    "Comments:\n"
    "Evaluate the potential for the idea to connect with and contribute to other disciplines beyond ML.\n"
    "Does it align with the trend of interdisciplinary research and collaboration, integrating with fields such as data science, neuroscience, or social sciences?</Approach>\n"

    "Here is the idea to evaluate: {idea}.\n"
    "Here is the research trend: {trend}.\n"

    )



    input_data = {
        "idea": idea,
        "trend": trend
    }
    prompt = prompt_idea.format_map(input_data)
    evaluation_result = model_prompting(model_name, prompt)
    # merge results from List[Str] to Str
    combined_result = "\n".join(evaluation_result)

    return combined_result

@beartype
def paper_quality_eval_prompting(
    idea: str,
    paper: Dict[str,str],
    model_name: str
) -> str:
    paper_prompt = """
    <Instruction> Please evaluate the paper draft based on the following dimensions. Finally, give an overall score (0-100) and 10 dimension scores (for each dimension, provide a rating (1-10)) as the evaluation for the draft. The output format should follow these rules: Overall Score of a paper draft (0-100), with 10 Dimension Scores: [d1, d2, d3, ..., d10], where di is the score of the i-th dimension. An example of output is: 'Overall Score=85. Dimension Scores=[7,8,9,7,8,9,8,8,8,9]'. <Instruction>

    <Approach> The details of rating are as follows:

    1. Title Appeal
    Rating (1-10):
    Comments:
    Does the title grab attention and generate interest?
    Is it informative and reflective of the paper's content?

    2. Abstract Quality
    Rating (1-10):
    Comments:
    How well does the abstract summarize the paper?
    Is it clear, concise, and informative?
    Does it effectively convey the significance and main contributions of the paper?

    3. Title and Abstract Consistency
    Rating (1-10):
    Comments:
    How well do the title and abstract align with each other?
    Do they accurately represent the core idea and content of the paper?

    4. Literature Review and Background
    Rating (1-10):
    Comments:
    Assess the thoroughness of the literature review and background provided.
    Is the context and relevance of the research well-established?
    Does it cover key works and current trends in the field?

    5. Methodology
    Rating (1-10):
    Comments:
    Evaluate the soundness and appropriateness of the methodology used.
    Are the research design and methods clearly described and justified?
    Is the methodology robust and suitable for addressing the research questions?

    6. Results and Analysis
    Rating (1-10):
    Comments:
    Assess the quality and clarity of the results presented.
    Are the results well-analyzed and interpreted?
    Do the findings support the claims made in the paper?

    7. Clarity and Presentation
    Rating (1-10):
    Comments:
    Evaluate the clarity, organization, and presentation quality of the paper.
    Is the content well-structured and easy to follow?
    Are figures, tables, and references used effectively?

    8. Contribution to the Field
    Rating (1-10):
    Comments:
    Evaluate the significance of the paper's contributions to the field.
    Does it advance knowledge or offer new insights?
    How does it compare to existing works in terms of impact?

    9. Ethical Considerations
    Rating (1-10):
    Comments:
    Consider the ethical implications and societal impact of the work.
    Does it adhere to ethical guidelines and responsible research practices?
    Are potential negative consequences or biases addressed?

    10. Interdisciplinary Connections
    Rating (1-10):
    Comments:
    Evaluate the potential for the work to connect with and contribute to other disciplines.
    Does it integrate knowledge from other fields or offer insights relevant to them?
    How well does it align with the trend of interdisciplinary research and collaboration?

    Here is the paper draft to evaluate:

    Title: {title}
    Abstract: {abstract}
    Idea: {idea}
    <Approach>
    """



    input_data = {
        "idea": idea,
        "title": paper["title"],
        "abstract": paper["abstract"],
    }
    prompt = paper_prompt.format_map(input_data)
    evaluation_result = model_prompting(model_name, prompt)
    # merge results from List[Str] to Str
    combined_result = "\n".join(evaluation_result)

    return combined_result



def review_quality_eval_prompting(
    idea: str,
    paper: Dict[str,str],
    review: List[str],
    model_name: str
) -> str:
    pass