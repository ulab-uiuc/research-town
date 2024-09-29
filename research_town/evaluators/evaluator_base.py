from typing import List, Tuple

from research_town.configs import Config
from research_town.data import Idea, Insight, MetaReview, Proposal, Rebuttal, Review

from ..utils.serializer import Serializer
from .evaluator_output import (
    IdeaEvalOutput,
    InsightEvalOutput,
    MetaReviewEvalOutput,
    ProposalEvalOutput,
    RebuttalEvalOutput,
    ReviewEvalOutput,
)
from .evaluator_quality import (
    IdeaQualityEvaluator,
    InsightQualityEvaluator,
    MetaReviewQualityEvaluator,
    ProposalQualityEvaluator,
    RebuttalQualityEvaluator,
    ReviewQualityEvaluator,
)


class BaseEvaluator:
    def __init__(self, model_name: str, config: Config):
        self.model_name = model_name
        self.config = config
        self.serializer = Serializer()

    def evaluate_insight_quality(self, insight: Insight) -> InsightEvalOutput:
        evaluator = InsightQualityEvaluator(
            model_name=self.model_name, config=self.config
        )
        return evaluator.eval(
            insight=self.serializer.serialize(insight),
        )

    def evaluate_idea_quality(
        self, insights: List[Insight], idea: Idea
    ) -> IdeaEvalOutput:
        evaluator = IdeaQualityEvaluator(model_name=self.model_name, config=self.config)
        return evaluator.eval(
            insights=self.serializer.serialize(insights),
            idea=self.serializer.serialize(idea),
        )

    def evaluate_paper_quality(
        self,
        insights: List[Insight],
        idea: Idea,
        paper: Proposal,
    ) -> ProposalEvalOutput:
        evaluator = ProposalQualityEvaluator(
            model_name=self.model_name, config=self.config
        )
        return evaluator.eval(
            insights=self.serializer.serialize(insights),
            idea=self.serializer.serialize(idea),
            paper=self.serializer.serialize(paper),
        )

    def evaluate_review_quality(
        self,
        insights: List[Insight],
        idea: Idea,
        paper: Proposal,
        review: Review,
    ) -> ReviewEvalOutput:
        evaluator = ReviewQualityEvaluator(
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
        insights: List[Insight],
        idea: Idea,
        paper: Proposal,
        review: Review,
        rebuttal: Rebuttal,
    ) -> RebuttalEvalOutput:
        evaluator = RebuttalQualityEvaluator(
            model_name=self.model_name, config=self.config
        )
        return evaluator.eval(
            insights=self.serializer.serialize(insights),
            idea=self.serializer.serialize(idea),
            paper=self.serializer.serialize(paper),
            review=self.serializer.serialize(review),
            rebuttal=self.serializer.serialize(rebuttal),
        )

    def evaluate_metareview_quality(
        self,
        insights: List[Insight],
        idea: Idea,
        paper: Proposal,
        reviews: List[Review],
        rebuttals: List[Rebuttal],
        metareview: MetaReview,
    ) -> MetaReviewEvalOutput:
        evaluator = MetaReviewQualityEvaluator(
            model_name=self.model_name, config=self.config
        )
        return evaluator.eval(
            insights=self.serializer.serialize(insights),
            idea=self.serializer.serialize(idea),
            paper=self.serializer.serialize(paper),
            reviews=self.serializer.serialize(reviews),
            rebuttals=self.serializer.serialize(rebuttals),
            metareview=self.serializer.serialize(metareview),
        )

    def pipeline_eval(
        self,
        insights: List[Insight],
        idea: Idea,
        paper: Proposal,
        reviews: List[Review],
        rebuttals: List[Rebuttal],
        metareview: MetaReview,
    ) -> Tuple[
        List[InsightEvalOutput],
        IdeaEvalOutput,
        ProposalEvalOutput,
        List[ReviewEvalOutput],
        List[RebuttalEvalOutput],
        MetaReviewEvalOutput,
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
        metareview_quality = self.evaluate_metareview_quality(
            insights, idea, paper, reviews, rebuttals, metareview
        )

        return (
            insights_quality,
            idea_quality,
            paper_quality,
            reviews_quality,
            rebuttals_quality,
            metareview_quality,
        )
