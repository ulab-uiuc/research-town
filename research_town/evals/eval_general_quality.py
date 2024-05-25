from eval_base import BaseEvaluator
from typing import Optional, Tuple
class PromptBasedGeneralQualityEval(BaseEvaluator):
    def __init__(self, model_name: str,progress_dic: dict, max_turns: Optional[int]=1) -> None:
        super().__init__(model_name,progress_dic)
        self.turn_number = 0
        self.turn_max = max_turns
        self.terminated = False
    def step(self) -> None:
        # evaluate idea
        self.eval_idea()
        # evaluate paper
        self.eval_paper()
        # evaluate review
        self.eval_review()
        # evaluate discussion
        self.eval_disc()
        
        self.turn_number += 1
        if self.turn_number >= self.turn_max:
            self.terminated = True
    
    def eval_idea(self)-> None:
        pass

    def eval_paper(self)-> None:
        pass
    
    def eval_review(self)-> None:
        pass

    def eval_disc(self)-> None:
        pass
        