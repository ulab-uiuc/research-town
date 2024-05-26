from dis import Instruction
from typing import Dict, List, Optional, Tuple

from .model_prompting import model_prompting


def GeneralQuality_idea_EvalPrompting(ideas: Dict[str, str], model_name: Optional[str] = "mistralai/Mixtral-8x7B-Instruct-v0.1",) -> List[str]:

    prompt_idea = (
    "<Instruction> Please evaluate the idea based on the following dimensions, considering the current research trend within the ML community. If the research trend field is left blank, please use your common knowledge to assess the trend. For each dimension, provide a rating (1-10) and detailed comments. Finally, give an overall score (0-100) and 10 dimension scores as the evaluation for the idea. The output format should follow these rules: Overall Score of an idea (0-100), with 10 Dimension Scores: [d1, d2, d3, ..., d10], where di is the score of the i-th dimension. An example of output is: 'Overall Score=89. Dimension Scores=[8,9,9,9,9,9,9,9,9,9]'.<Instruction>\n"
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
    "7. Relevance to Conference Scope\n"
    "Rating (1-10):\n"
    "Comments:\n"
    "Evaluate the relevance of the idea to the conference's scope and themes.\n"
    "Does it align with the topics of interest and focus areas as indicated by the conference call for papers and the trend?\n"
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

    # Todo(jinwei): add the research trend.
    input = {"ideas": str(ideas)}
    prompt = prompt_idea.format_map(input)
    return model_prompting(model_name, prompt)