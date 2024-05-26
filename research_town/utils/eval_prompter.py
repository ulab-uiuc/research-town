from typing import Dict, List, Optional, Tuple

from .model_prompting import model_prompting


def GeneralQuality_idea_EvalPrompting(ideas: Dict[str, str], model_name: Optional[str] = "mistralai/Mixtral-8x7B-Instruct-v0.1",) -> List[str]:

    prompt_idea = (
        "Given the ideas, could you please evaluate each idea? Ideas:{ideas}"
        
    )
    input = {"ideas": str(ideas)}
    prompt = prompt_idea.format_map(input)
    return model_prompting(model_name, prompt)