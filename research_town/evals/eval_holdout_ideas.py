from eval_base import BaseEvaluator

class PromptBasedHoldOutIdeaEval(BaseEvaluator):
    def __init__(self, model_name: str, progress_dic: dict) -> None:
        super().__init__(model_name,progress_dic)
    def step(self) -> None:
        pass
    