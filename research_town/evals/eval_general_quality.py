
from typing import Optional, Tuple, Any
from ..utils.eval_prompter import GeneralQuality_idea_EvalPrompting
import eval_output
class PromptBasedGeneralQualityEval:
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

    
    def eval_idea(self)-> None:
        # generate the prompt template and prompting (prompter in eval_prompter.py)
        model_output = GeneralQuality_idea_EvalPrompting(ideas=self.progress2eval['idea'],model_name=self.model_name)
        # parse the prompting output(parser in eval_out.py)

        # store it to self.eval_res

        pass

    def eval_paper(self)-> None:
        pass
    
    def eval_review(self)-> None:
        pass

    def eval_disc(self)-> None:
        pass
        