import re

from beartype.typing import Any, Optional, Type, TypeVar

from ..configs import Config
from ..utils.error_handler import parsing_error_exponential_backoff
from ..utils.eval_prompter import (
    research_idea_quality_eval_prompting,
    research_insight_quality_eval_prompting,
    research_meta_review_for_paper_submission_quality_eval_prompting,
    research_paper_submission_quality_eval_prompting,
    research_rebuttal_for_paper_submission_quality_eval_prompting,
    research_review_for_paper_submission_quality_eval_prompting,
)
from .evaluator_output import (
    BaseEvalOutput,
    ResearchIdeaEvalOutput,
    ResearchInsightEvalOutput,
    ResearchMetaReviewForPaperSubmissionEvalOutput,
    ResearchPaperSubmissionEvalOutput,
    ResearchRebuttalForPaperSubmissionEvalOutput,
    ResearchReviewForPaperSubmissionEvalOutput,
)
from .evaluator_output_format import OutputFormatError

T = TypeVar('T', bound=BaseEvalOutput)


class BaseQualityEvaluator:
    def __init__(
        self,
        model_name: str,
        output_model: Type[BaseEvalOutput],
        config: Optional[Config] = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        self.model_name = model_name
        self.parsed_output = output_model()
        self.config = config

    def eval(self, *args: Any, **kwargs: Any) -> BaseEvalOutput:
        raise NotImplementedError('Subclasses should implement this method')

    def parse(self, raw_output: str, output_model: Type[T]) -> T:
        overall_score_match = re.search(
            r'Overall\s*Score\s*\W*(\d+)\W*', raw_output, re.IGNORECASE
        )
        dimension_scores_match = re.search(
            r'Dimension\s*Scores\s*\W*\s*\[([0-9,\s]+)\]', raw_output, re.IGNORECASE
        )

        if overall_score_match:
            try:
                overall_score = int(overall_score_match.group(1))
            except ValueError as e:
                raise OutputFormatError(f'Invalid overall score: {e}')
        else:
            raise OutputFormatError(
                f"Output format error: 'Overall Score' not found. Raw output is {raw_output}."
            )

        if dimension_scores_match:
            try:
                dimension_scores = list(
                    map(int, dimension_scores_match.group(1).split(','))
                )
            except ValueError as e:
                raise OutputFormatError(f'Invalid dimension scores: {e}')
        else:
            raise OutputFormatError(
                f"Output format error: 'Dimension Scores' not found. Raw output is {raw_output}."
            )

        return output_model(
            overall_score=overall_score, dimension_scores=dimension_scores
        )


class ResearchIdeaQualityEvaluator(BaseQualityEvaluator):
    def __init__(
        self,
        model_name: str,
        config: Optional[Config] = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(model_name, ResearchIdeaEvalOutput, *args, **kwargs)

    @parsing_error_exponential_backoff(retries=5, base_wait_time=1)
    def eval(self, *args: Any, **kwargs: Any) -> ResearchIdeaEvalOutput:
        raw_output = research_idea_quality_eval_prompting(
            idea=kwargs['idea'],
            trend=kwargs['trend'],
            model_name=self.model_name,
            return_num=self.config.param.return_num if self.config else 1,
            max_token_num=self.config.param.max_token_num if self.config else 512,
            temperature=self.config.param.temperature if self.config else None,
            top_p=self.config.param.top_p if self.config else None,
            stream=self.config.param.stream if self.config else None,
        )
        self.parsed_output = self.parse(raw_output, ResearchIdeaEvalOutput)

        for key, value in kwargs.items():
            setattr(self.parsed_output, key, value)
        return self.parsed_output


class ResearchPaperSubmissionQualityEvaluator(BaseQualityEvaluator):
    def __init__(
        self,
        model_name: str,
        config: Optional[Config] = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(model_name, ResearchPaperSubmissionEvalOutput, *args, **kwargs)

    @parsing_error_exponential_backoff(retries=5, base_wait_time=1)
    def eval(self, *args: Any, **kwargs: Any) -> ResearchPaperSubmissionEvalOutput:
        raw_output = research_paper_submission_quality_eval_prompting(
            idea=kwargs['idea'],
            paper=kwargs['paper'],
            model_name=self.model_name,
            trend=kwargs.get('trend'),
            return_num=self.config.param.return_num if self.config else 1,
            max_token_num=self.config.param.max_token_num if self.config else 512,
            temperature=self.config.param.temperature if self.config else None,
            top_p=self.config.param.top_p if self.config else None,
            stream=self.config.param.stream if self.config else None,
        )
        self.parsed_output = self.parse(raw_output, ResearchPaperSubmissionEvalOutput)

        for key, value in kwargs.items():
            setattr(self.parsed_output, key, value)
        return self.parsed_output


class ResearchReviewForPaperSubmissionQualityEvaluator(BaseQualityEvaluator):
    def __init__(
        self,
        model_name: str,
        config: Optional[Config] = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            model_name, ResearchReviewForPaperSubmissionEvalOutput, *args, **kwargs
        )

    @parsing_error_exponential_backoff(retries=5, base_wait_time=1)
    def eval(
        self, *args: Any, **kwargs: Any
    ) -> ResearchReviewForPaperSubmissionEvalOutput:
        raw_output = research_review_for_paper_submission_quality_eval_prompting(
            idea=kwargs['idea'],  # idea: str,
            trend=kwargs['trend'],  # trend: str,
            paper=kwargs['paper'],  # paper: Dict[str,str],
            review=kwargs['review'],
            model_name=self.model_name,
            return_num=self.config.param.return_num if self.config else 1,
            max_token_num=self.config.param.max_token_num if self.config else 512,
            temperature=self.config.param.temperature if self.config else None,
            top_p=self.config.param.top_p if self.config else None,
            stream=self.config.param.stream if self.config else None,
        )
        self.parsed_output = self.parse(
            raw_output, ResearchReviewForPaperSubmissionEvalOutput
        )

        for key, value in kwargs.items():
            setattr(self.parsed_output, key, value)
        return self.parsed_output


class ResearchInsightQualityEvaluator(BaseQualityEvaluator):
    def __init__(
        self,
        model_name: str,
        config: Optional[Config] = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(model_name, ResearchInsightEvalOutput, *args, **kwargs)

    @parsing_error_exponential_backoff(retries=5, base_wait_time=1)
    def eval(self, *args: Any, **kwargs: Any) -> ResearchInsightEvalOutput:
        raw_output = research_insight_quality_eval_prompting(
            insight=kwargs['insight'],
            trend=kwargs['trend'],
            model_name=self.model_name,
            return_num=self.config.param.return_num if self.config else 1,
            max_token_num=self.config.param.max_token_num if self.config else 512,
            temperature=self.config.param.temperature if self.config else None,
            top_p=self.config.param.top_p if self.config else None,
            stream=self.config.param.stream if self.config else None,
        )
        self.parsed_output = self.parse(raw_output, ResearchInsightEvalOutput)

        for key, value in kwargs.items():
            setattr(self.parsed_output, key, value)
        return self.parsed_output


class ResearchRebuttalQualityEvaluator(BaseQualityEvaluator):
    def __init__(
        self,
        model_name: str,
        config: Optional[Config] = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            model_name, ResearchRebuttalForPaperSubmissionEvalOutput, *args, **kwargs
        )

    @parsing_error_exponential_backoff(retries=5, base_wait_time=1)
    def eval(
        self, *args: Any, **kwargs: Any
    ) -> ResearchRebuttalForPaperSubmissionEvalOutput:
        raw_output = research_rebuttal_for_paper_submission_quality_eval_prompting(
            idea=kwargs['idea'],
            trend=kwargs['trend'],
            paper=kwargs['paper'],
            review=kwargs['review'],
            model_name=self.model_name,
            rebuttal=kwargs.get('rebuttal'),
            return_num=self.config.param.return_num if self.config else 1,
            max_token_num=self.config.param.max_token_num if self.config else 512,
            temperature=self.config.param.temperature if self.config else None,
            top_p=self.config.param.top_p if self.config else None,
            stream=self.config.param.stream if self.config else None,
        )
        self.parsed_output = self.parse(
            raw_output, ResearchRebuttalForPaperSubmissionEvalOutput
        )

        for key, value in kwargs.items():
            setattr(self.parsed_output, key, value)
        return self.parsed_output


class ResearchMetaReviewQualityEvaluator(BaseQualityEvaluator):
    def __init__(
        self,
        model_name: str,
        config: Optional[Config] = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            model_name, ResearchMetaReviewForPaperSubmissionEvalOutput, *args, **kwargs
        )

    @parsing_error_exponential_backoff(retries=5, base_wait_time=1)
    def eval(
        self, *args: Any, **kwargs: Any
    ) -> ResearchMetaReviewForPaperSubmissionEvalOutput:
        raw_output = research_meta_review_for_paper_submission_quality_eval_prompting(
            idea=kwargs['idea'],
            trend=kwargs['trend'],
            paper=kwargs['paper'],
            review=kwargs['review'],
            decision=kwargs['decision'],
            model_name=self.model_name,
            rebuttal=kwargs.get('rebuttal'),
            meta_review=kwargs.get('meta_review'),
            return_num=self.config.param.return_num if self.config else 1,
            max_token_num=self.config.param.max_token_num if self.config else 512,
            temperature=self.config.param.temperature if self.config else None,
            top_p=self.config.param.top_p if self.config else None,
            stream=self.config.param.stream if self.config else None,
        )
        self.parsed_output = self.parse(
            raw_output, ResearchMetaReviewForPaperSubmissionEvalOutput
        )

        for key, value in kwargs.items():
            setattr(self.parsed_output, key, value)
        return self.parsed_output
