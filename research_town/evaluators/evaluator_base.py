from typing import List, Tuple

from research_town.configs import Config
from research_town.dbs import (
    ResearchIdea,
    ResearchInsight,
    ResearchMetaReview,
    ResearchPaperSubmission,
    ResearchRebuttal,
    ResearchReview,
)

from ..utils.serializer import Serializer
from .evaluator_output import (
    ResearchIdeaEvalOutput,
    ResearchInsightEvalOutput,
    ResearchMetaReviewEvalOutput,
    ResearchPaperSubmissionEvalOutput,
    ResearchRebuttalEvalOutput,
    ResearchReviewEvalOutput,
)
from .evaluator_quality import (
    ResearchIdeaQualityEvaluator,
    ResearchInsightQualityEvaluator,
    ResearchMetaReviewQualityEvaluator,
    ResearchPaperSubmissionQualityEvaluator,
    ResearchRebuttalQualityEvaluator,
    ResearchReviewQualityEvaluator,
)


class BaseEvaluator:
    def __init__(self, model_name: str, config: Config):
        self.model_name = model_name
        self.config = config
        self.serializer = Serializer()

    def evaluate_insight_quality(
        self, insight: ResearchInsight
    ) -> ResearchInsightEvalOutput:
        evaluator = ResearchInsightQualityEvaluator(
            model_name=self.model_name, config=self.config
        )
        return evaluator.eval(
            insight=self.serializer.serialize(insight),
        )

    def evaluate_idea_quality(
        self, insights: List[ResearchInsight], idea: ResearchIdea
    ) -> ResearchIdeaEvalOutput:
        evaluator = ResearchIdeaQualityEvaluator(
            model_name=self.model_name, config=self.config
        )
        return evaluator.eval(
            insights=self.serializer.serialize(insights),
            idea=self.serializer.serialize(idea),
        )

    def evaluate_paper_quality(
        self,
        insights: List[ResearchInsight],
        idea: ResearchIdea,
        paper: ResearchPaperSubmission,
    ) -> ResearchPaperSubmissionEvalOutput:
        evaluator = ResearchPaperSubmissionQualityEvaluator(
            model_name=self.model_name, config=self.config
        )
        return evaluator.eval(
            insights=self.serializer.serialize(insights),
            idea=self.serializer.serialize(idea),
            paper=self.serializer.serialize(paper),
        )

    def evaluate_review_quality(
        self,
        insights: List[ResearchInsight],
        idea: ResearchIdea,
        paper: ResearchPaperSubmission,
        review: ResearchReview,
    ) -> ResearchReviewEvalOutput:
        evaluator = ResearchReviewQualityEvaluator(
            model_name=self.model_name, config=self.config
        )
        return evaluator.eval(
            insights=self.serializer.serialize(insights),
            idea=self.serializer.serialize(idea),
            paper=self.serializer.serialize(paper),
            review=self.serializer.serialize(review),
        )

    def evaluate_rebuttal_quality(
        self,
        insights: List[ResearchInsight],
        idea: ResearchIdea,
        paper: ResearchPaperSubmission,
        review: ResearchReview,
        rebuttal: ResearchRebuttal,
    ) -> ResearchRebuttalEvalOutput:
        evaluator = ResearchRebuttalQualityEvaluator(
            model_name=self.model_name, config=self.config
        )
        return evaluator.eval(
            insights=self.serializer.serialize(insights),
            idea=self.serializer.serialize(idea),
            paper=self.serializer.serialize(paper),
            review=self.serializer.serialize(review),
            rebuttal=self.serializer.serialize(rebuttal),
        )

    def evaluate_meta_review_quality(
        self,
        insights: List[ResearchInsight],
        idea: ResearchIdea,
        paper: ResearchPaperSubmission,
        reviews: List[ResearchReview],
        rebuttals: List[ResearchRebuttal],
        meta_review: ResearchMetaReview,
    ) -> ResearchMetaReviewEvalOutput:
        evaluator = ResearchMetaReviewQualityEvaluator(
            model_name=self.model_name, config=self.config
        )
        return evaluator.eval(
            insights=self.serializer.serialize(insights),
            idea=self.serializer.serialize(idea),
            paper=self.serializer.serialize(paper),
            reviews=self.serializer.serialize(reviews),
            rebuttals=self.serializer.serialize(rebuttals),
            meta_review=self.serializer.serialize(meta_review),
        )

    def pipeline_eval(
        self,
        insights: List[ResearchInsight],
        idea: ResearchIdea,
        paper: ResearchPaperSubmission,
        reviews: List[ResearchReview],
        rebuttals: List[ResearchRebuttal],
        meta_review: ResearchMetaReview,
    ) -> Tuple[
        List[ResearchInsightEvalOutput],
        ResearchIdeaEvalOutput,
        ResearchPaperSubmissionEvalOutput,
        List[ResearchReviewEvalOutput],
        List[ResearchRebuttalEvalOutput],
        ResearchMetaReviewEvalOutput,
    ]:
        insights_quality = [
            self.evaluate_insight_quality(insight) for insight in insights
        ]
        idea_quality = self.evaluate_idea_quality(insights, idea)
        paper_quality = self.evaluate_paper_quality(insights, idea, paper)
        reviews_quality = [
            self.evaluate_review_quality(insights, idea, paper, review)
            for review in reviews
        ]
        rebuttals_quality = [
            self.evaluate_rebuttal_quality(insights, idea, paper, review, rebuttal)
            for review, rebuttal in zip(reviews, rebuttals)
        ]
        meta_review_quality = self.evaluate_meta_review_quality(
            insights, idea, paper, reviews, rebuttals, meta_review
        )

        return (
            insights_quality,
            idea_quality,
            paper_quality,
            reviews_quality,
            rebuttals_quality,
            meta_review_quality,
        )
