
from research_town.utils.model_prompting import model_prompting

def compute_gpt_metric(current_5q: str, proposal_5q: str):
    """
    Computes a custom GPT-based metric to evaluate if the proposal_5q reflects the current_5q.

    Args:
        current_5q (str): The current five core questions.
        proposal_5q (str): The proposed five core questions.

    Returns:
        Optional[float]: A similarity score between 0 and 1.
    """
    prompt = [
        {
            'role': 'user',
            'content': (
                'Evaluate the alignment between the following two sets of five core research questions, with a particular emphasis on their objectives, methodologies, and expected outcomes.\n\n'
                'Alignment Criteria Definitions:\n'
                '1. **Objectives**: Do both sets of questions aim to address the same or complementary research goals?\n'
                '2. **Methodologies**: Are the proposed methods similar, compatible, or capable of being effectively integrated?\n'
                '3. **Expected Outcomes**: Are the anticipated research results and impacts consistent or mutually supportive?\n\n'
                'Current Five Research Questions (Current 5Q):\n'
                f'{current_5q}\n\n'
                'Proposed Five Research Questions (Proposal 5Q):\n'
                f'{proposal_5q}\n\n'
                'Based on the above alignment criteria, especially focusing on the methodologies, please provide a similarity score: **1** indicates alignment, and **0** indicates no alignment. **Only output the score without any additional information.**'
            ),
        }
    ]
    response = model_prompting('gpt-4o-mini', prompt, mode='TEST')
    print(response)

compute_gpt_metric('current_5q', 'proposal_5q')