import re

from beartype.typing import Any, Type, TypeVar

from ..configs import Config
from ..utils.error_handler import parsing_error_exponential_backoff
from ..utils.eval_prompter import (
    research_idea_quality_eval_prompting,
    research_insight_quality_eval_prompting,
    research_metareview_quality_eval_prompting,
    research_proposal_quality_eval_prompting,
    research_rebuttal_quality_eval_prompting,
    research_review_quality_eval_prompting,
)
from .evaluator_output import (
    BaseEvalOutput,
    IdeaEvalOutput,
    InsightEvalOutput,
    MetaReviewEvalOutput,
    ProposalEvalOutput,
    RebuttalEvalOutput,
    ReviewEvalOutput,
)
from .evaluator_output_format import OutputFormatError

T = TypeVar('T', bound=BaseEvalOutput)


class BaseQualityEvaluator:
    def __init__(
        self,
        model_name: str,
        output_model: Type[BaseEvalOutput],
        config: Config,
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


class InsightQualityEvaluator(BaseQualityEvaluator):
    def __init__(
        self,
        model_name: str,
        config: Config,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(model_name, InsightEvalOutput, config, *args, **kwargs)

    @parsing_error_exponential_backoff(retries=5, base_wait_time=1)
    def eval(self, *args: Any, **kwargs: Any) -> InsightEvalOutput:
        raw_output = research_insight_quality_eval_prompting(
            model_name=self.model_name,
            insight=kwargs['insight'],
            return_num=self.config.param.return_num if self.config else 1,
            max_token_num=self.config.param.max_token_num if self.config else 512,
            temperature=self.config.param.temperature if self.config else None,
            top_p=self.config.param.top_p if self.config else None,
            stream=self.config.param.stream if self.config else None,
            prompt_template=self.config.eval_prompt_template.insight_quality,
        )
        self.parsed_output = self.parse(raw_output, InsightEvalOutput)

        for key, value in kwargs.items():
            setattr(self.parsed_output, key, value)
        return self.parsed_output


class IdeaQualityEvaluator(BaseQualityEvaluator):
    def __init__(
        self,
        model_name: str,
        config: Config,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(model_name, IdeaEvalOutput, config, *args, **kwargs)

    @parsing_error_exponential_backoff(retries=5, base_wait_time=1)
    def eval(self, *args: Any, **kwargs: Any) -> IdeaEvalOutput:
        raw_output = research_idea_quality_eval_prompting(
            model_name=self.model_name,
            insights=kwargs['insights'],
            idea=kwargs['idea'],
            return_num=self.config.param.return_num if self.config else 1,
            max_token_num=self.config.param.max_token_num if self.config else 512,
            temperature=self.config.param.temperature if self.config else None,
            top_p=self.config.param.top_p if self.config else None,
            stream=self.config.param.stream if self.config else None,
            prompt_template=self.config.eval_prompt_template.idea_quality,
        )
        self.parsed_output = self.parse(raw_output, IdeaEvalOutput)

        for key, value in kwargs.items():
            setattr(self.parsed_output, key, value)
        return self.parsed_output


class ProposalQualityEvaluator(BaseQualityEvaluator):
    def __init__(
        self,
        model_name: str,
        config: Config,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(model_name, ProposalEvalOutput, config, *args, **kwargs)

    @parsing_error_exponential_backoff(retries=5, base_wait_time=1)
    def eval(self, *args: Any, **kwargs: Any) -> ProposalEvalOutput:
        raw_output = research_proposal_quality_eval_prompting(
            model_name=self.model_name,
            insights=kwargs['insights'],
            idea=kwargs['idea'],
            paper=kwargs['paper'],
            return_num=self.config.param.return_num if self.config else 1,
            max_token_num=self.config.param.max_token_num if self.config else 512,
            temperature=self.config.param.temperature if self.config else None,
            top_p=self.config.param.top_p if self.config else None,
            stream=self.config.param.stream if self.config else None,
            prompt_template=self.config.eval_prompt_template.proposal_quality,
        )
        self.parsed_output = self.parse(raw_output, ProposalEvalOutput)

        for key, value in kwargs.items():
            setattr(self.parsed_output, key, value)
        return self.parsed_output


class ReviewQualityEvaluator(BaseQualityEvaluator):
    def __init__(
        self,
        model_name: str,
        config: Config,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(model_name, ReviewEvalOutput, config, *args, **kwargs)

    @parsing_error_exponential_backoff(retries=5, base_wait_time=1)
    def eval(self, *args: Any, **kwargs: Any) -> ReviewEvalOutput:
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
            prompt_template=self.config.eval_prompt_template.review_quality,
        )
        self.parsed_output = self.parse(raw_output, ReviewEvalOutput)

        for key, value in kwargs.items():
            setattr(self.parsed_output, key, value)
        return self.parsed_output


class RebuttalQualityEvaluator(BaseQualityEvaluator):
    def __init__(
        self,
        model_name: str,
        config: Config,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(model_name, RebuttalEvalOutput, config, *args, **kwargs)

    @parsing_error_exponential_backoff(retries=5, base_wait_time=1)
    def eval(self, *args: Any, **kwargs: Any) -> RebuttalEvalOutput:
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
            prompt_template=self.config.eval_prompt_template.rebuttal_quality,
        )
        self.parsed_output = self.parse(raw_output, RebuttalEvalOutput)

        for key, value in kwargs.items():
            setattr(self.parsed_output, key, value)
        return self.parsed_output


class MetaReviewQualityEvaluator(BaseQualityEvaluator):
    def __init__(
        self,
        model_name: str,
        config: Config,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(model_name, MetaReviewEvalOutput, config, *args, **kwargs)

    @parsing_error_exponential_backoff(retries=5, base_wait_time=1)
    def eval(self, *args: Any, **kwargs: Any) -> MetaReviewEvalOutput:
        raw_output = research_metareview_quality_eval_prompting(
            model_name=self.model_name,
            insights=kwargs['insights'],
            idea=kwargs['idea'],
            paper=kwargs['paper'],
            reviews=kwargs['reviews'],
            rebuttals=kwargs['rebuttals'],
            metareview=kwargs['metareview'],
            return_num=self.config.param.return_num if self.config else 1,
            max_token_num=self.config.param.max_token_num if self.config else 512,
            temperature=self.config.param.temperature if self.config else None,
            top_p=self.config.param.top_p if self.config else None,
            stream=self.config.param.stream if self.config else None,
            prompt_template=self.config.eval_prompt_template.metareview_quality,
        )
        self.parsed_output = self.parse(raw_output, MetaReviewEvalOutput)

        for key, value in kwargs.items():
            setattr(self.parsed_output, key, value)
        return self.parsed_output
