
from typing import Optional, Tuple, Any
from ..utils.eval_prompter import GeneralQuality_idea_EvalPrompting
from eval_output import parser_GeneralQuality_idea, EvalOutput_GeneralQuality

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
        self.eval_res = EvalOutput_GeneralQuality() # to store the result of evaluation

    
    def eval_idea(self)-> None:
        # generate the prompt template and prompting (prompter in eval_prompter.py)
        model_output = GeneralQuality_idea_EvalPrompting(ideas=self.progress2eval['idea'],model_name=self.model_name)
        # parse the prompting output(parser in eval_out.py). Extract a score and text in List[Tuple(float, str)].
        parsed_idea_eval = parser_GeneralQuality_idea(idea_output=model_output)
        # store it to self.eval_res
        self.eval_res.idea = parsed_idea_eval
        

    def eval_paper(self)-> None:
        pass
    
    def eval_review(self)-> None:
        pass

    def eval_disc(self)-> None:
        pass
        