import re

from beartype.typing import Any, Optional, Type, TypeVar

from ..configs import Config
from ..utils.error_handler import parsing_error_exponential_backoff
from ..utils.eval_prompter import (
    research_idea_quality_eval_prompting,
    research_insight_quality_eval_prompting,
    research_meta_review_quality_eval_prompting,
    research_paper_submission_quality_eval_prompting,
    research_rebuttal_quality_eval_prompting,
    research_review_quality_eval_prompting,
)
from .evaluator_output import (
    BaseEvalOutput,
    ResearchIdeaEvalOutput,
    ResearchInsightEvalOutput,
    ResearchMetaReviewEvalOutput,
    ResearchPaperSubmissionEvalOutput,
    ResearchRebuttalEvalOutput,
    ResearchReviewEvalOutput,
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
            model_name=self.model_name,
            insight=kwargs['insight'],
            return_num=self.config.param.return_num if self.config else 1,
            max_token_num=self.config.param.max_token_num if self.config else 512,
            temperature=self.config.param.temperature if self.config else None,
            top_p=self.config.param.top_p if self.config else None,
            stream=self.config.param.stream if self.config else None,
            prompt_template=self.config.eval_prompt_template.insight_quality
            if self.config
            else Config().eval_prompt_template.insight_quality,
        )
        self.parsed_output = self.parse(raw_output, ResearchInsightEvalOutput)

        for key, value in kwargs.items():
            setattr(self.parsed_output, key, value)
        return self.parsed_output


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
            model_name=self.model_name,
            insights=kwargs['insights'],
            idea=kwargs['idea'],
            return_num=self.config.param.return_num if self.config else 1,
            max_token_num=self.config.param.max_token_num if self.config else 512,
            temperature=self.config.param.temperature if self.config else None,
            top_p=self.config.param.top_p if self.config else None,
            stream=self.config.param.stream if self.config else None,
            prompt_template=self.config.eval_prompt_template.idea_quality
            if self.config
            else Config().eval_prompt_template.idea_quality,
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
            model_name=self.model_name,
            insights=kwargs['insights'],
            idea=kwargs['idea'],
            paper=kwargs['paper'],
            return_num=self.config.param.return_num if self.config else 1,
            max_token_num=self.config.param.max_token_num if self.config else 512,
            temperature=self.config.param.temperature if self.config else None,
            top_p=self.config.param.top_p if self.config else None,
            stream=self.config.param.stream if self.config else None,
            prompt_template=self.config.eval_prompt_template.paper_quality
            if self.config
            else Config().eval_prompt_template.paper_quality,
        )
        self.parsed_output = self.parse(raw_output, ResearchPaperSubmissionEvalOutput)

        for key, value in kwargs.items():
            setattr(self.parsed_output, key, value)
        return self.parsed_output


class ResearchReviewQualityEvaluator(BaseQualityEvaluator):
    def __init__(
        self,
        model_name: str,
        config: Optional[Config] = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(model_name, ResearchReviewEvalOutput, *args, **kwargs)

    @parsing_error_exponential_backoff(retries=5, base_wait_time=1)
    def eval(self, *args: Any, **kwargs: Any) -> ResearchReviewEvalOutput:
        raw_output = research_review_quality_eval_prompting(
            model_name=self.model_name,
            insights=kwargs['insights'],
            idea=kwargs['idea'],
            paper=kwargs['paper'],
            review=kwargs['review'],
            return_num=self.config.param.return_num if self.config else 1,
            max_token_num=self.config.param.max_token_num if self.config else 512,
            temperature=self.config.param.temperature if self.config else None,
            top_p=self.config.param.top_p if self.config else None,
            stream=self.config.param.stream if self.config else None,
            prompt_template=self.config.eval_prompt_template.review_quality
            if self.config
            else Config().eval_prompt_template.review_quality,
        )
        self.parsed_output = self.parse(raw_output, ResearchReviewEvalOutput)

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
        super().__init__(model_name, ResearchRebuttalEvalOutput, *args, **kwargs)

    @parsing_error_exponential_backoff(retries=5, base_wait_time=1)
    def eval(self, *args: Any, **kwargs: Any) -> ResearchRebuttalEvalOutput:
        raw_output = research_rebuttal_quality_eval_prompting(
            model_name=self.model_name,
            insights=kwargs['insights'],
            idea=kwargs['idea'],
            paper=kwargs['paper'],
            review=kwargs['review'],
            rebuttal=kwargs['rebuttal'],
            return_num=self.config.param.return_num if self.config else 1,
            max_token_num=self.config.param.max_token_num if self.config else 512,
            temperature=self.config.param.temperature if self.config else None,
            top_p=self.config.param.top_p if self.config else None,
            stream=self.config.param.stream if self.config else None,
            prompt_template=self.config.eval_prompt_template.rebuttal_quality
            if self.config
            else Config().eval_prompt_template.rebuttal_quality,
        )
        self.parsed_output = self.parse(raw_output, ResearchRebuttalEvalOutput)

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
        super().__init__(model_name, ResearchMetaReviewEvalOutput, *args, **kwargs)

    @parsing_error_exponential_backoff(retries=5, base_wait_time=1)
    def eval(self, *args: Any, **kwargs: Any) -> ResearchMetaReviewEvalOutput:
        raw_output = research_meta_review_quality_eval_prompting(
            model_name=self.model_name,
            insights=kwargs['insights'],
            idea=kwargs['idea'],
            paper=kwargs['paper'],
            reviews=kwargs['reviews'],
            rebuttals=kwargs['rebuttals'],
            meta_review=kwargs['meta_review'],
            return_num=self.config.param.return_num if self.config else 1,
            max_token_num=self.config.param.max_token_num if self.config else 512,
            temperature=self.config.param.temperature if self.config else None,
            top_p=self.config.param.top_p if self.config else None,
            stream=self.config.param.stream if self.config else None,
            prompt_template=self.config.eval_prompt_template.meta_review_quality
            if self.config
            else Config().eval_prompt_template.meta_review_quality,
        )
        self.parsed_output = self.parse(raw_output, ResearchMetaReviewEvalOutput)

        for key, value in kwargs.items():
            setattr(self.parsed_output, key, value)
        return self.parsed_output
