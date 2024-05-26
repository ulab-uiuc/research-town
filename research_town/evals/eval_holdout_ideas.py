
from typing import Optional, Tuple, Any
import eval_output
class PromptBasedHoldOutIdeaEval():
    def __init__(self, model_name: str, progress_dic: dict, *args: Any, **kwargs: Any )-> None:
        self.model_name = model_name
        self.prompt = ""
        # progress with info in a dict to evaluate
        # keys: 1) idea; 2) paper; 3) review; 4) discussion. 
        required_keys = ['idea', 'paper', 'review', 'discussion']
        for key in required_keys:
            if key not in progress_dic:
                raise ValueError(f"Missing required key in progress dic: {key}")
        self.progress2eval = {key: progress_dic[key] for key in required_keys}
        self.eval_res = None # to store the result of evaluation
    def step(self) -> None:
        pass
    