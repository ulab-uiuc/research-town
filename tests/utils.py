from typing import List, Optional

def mock_papers(corpus: List[str], query: str, num: int) -> List[str]:
    return corpus[:num]

def mock_prompting(
    llm_model: str, 
    prompt: str, 
    return_num: Optional[int]=2,
    max_tokens: Optional[int]=512,
) -> List[str]:
    if "Please give some reviews based on the following inputs and external data." in prompt:
        return ["This is a paper review for MambaOut."]
    elif "Please provide a score for the following reviews." in prompt:
        return ["2"]
    return ["Default response"]