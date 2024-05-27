
from typing import Optional, Tuple, Any, List
from ..utils.eval_prompter import GeneralQuality_idea_EvalPrompting,GeneralQuality_paper_EvalPrompting
from eval_output import  EvalOutput_GeneralQuality

class PromptBasedGeneralQualityEval:
    def __init__(self, model_name: str, progress_dic: dict, *args: Any, **kwargs: Any )-> None:
        self.model_name = model_name
        self.prompt = ""
        # progress with info in a dict to evaluate
        # keys: 1) idea; 2) paper; 3) review; 4) discussion. 
        required_keys = ['idea', 'paper', 'review', 'discussion','trend']
        for key in required_keys:
            if key not in progress_dic:
                raise ValueError(f"Missing required key in progress dic: {key}")
        self.progress2eval = {key: progress_dic[key] for key in required_keys}
        self.eval_res = EvalOutput_GeneralQuality() # to store the result of evaluation

    
    def eval_idea(self)-> List[int]:
        # generate the prompt template and prompting (prompter in eval_prompter.py)
        model_output = GeneralQuality_idea_EvalPrompting(ideas=self.progress2eval['idea'],model_name=self.model_name)
        # parse the prompting output(parser in eval_out.py). Extract a score in List[int]. Tuple(overall score, soundness, insightful, novelty, practial..)
        parsed_idea_eval = self.eval_res.parser_GeneralQuality_idea(idea_output=model_output)
        return parsed_idea_eval
    
    def eval_paper(self)-> List[int]:
        model_output = GeneralQuality_paper_EvalPrompting(ideas=self.progress2eval['idea'],papers=self.progress2eval['paper'],model_name=self.model_name)
        # parse the prompting output(parser in eval_out.py). Extract a score in List[int]. Tuple(overall score, soundness, insightful, novelty, practial..)
        parsed_paper_eval = self.eval_res.parser_GeneralQuality_paper(paper_output=model_output)
        return parsed_paper_eval

    def eval_review(self)-> None:
        # component/stage evaluation: compare with open review by ranking consistency
        pass
    

    
        