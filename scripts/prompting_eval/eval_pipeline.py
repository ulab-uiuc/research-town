from typing import List, Tuple

from research_town.configs import Config
from research_town.dbs import (
    ProgressDB,
    ResearchIdea,
    ResearchInsight,
    ResearchMetaReview,
    ResearchPaperSubmission,
    ResearchRebuttal,
    ResearchReview,
)
from research_town.evaluators import (
    ResearchIdeaEvalOutput,
    ResearchIdeaQualityEvaluator,
    ResearchInsightEvalOutput,
    ResearchInsightQualityEvaluator,
    ResearchMetaReviewEvalOutput,
    ResearchMetaReviewQualityEvaluator,
    ResearchPaperSubmissionEvalOutput,
    ResearchPaperSubmissionQualityEvaluator,
    ResearchRebuttalEvalOutput,
    ResearchRebuttalQualityEvaluator,
    ResearchReviewEvalOutput,
    ResearchReviewQualityEvaluator,
)
from research_town.utils.string_mapper import map_idea_to_str, map_insight_to_str


def evaluate_insight_quality(
    insight: ResearchInsight, model_name: str, config: Config
) -> ResearchInsightEvalOutput:
    evaluator = ResearchInsightQualityEvaluator(model_name=model_name, config=config)
    return evaluator.eval(
        insight=map_insight_to_str(insight.model_dump()),
    )


def evaluate_idea_quality(
    idea: ResearchIdea, insight: ResearchInsight, model_name: str, config: Config
) -> ResearchIdeaEvalOutput:
    evaluator = ResearchIdeaQualityEvaluator(model_name=model_name, config=config)
    return evaluator.eval(
        idea=map_idea_to_str(idea.model_dump()),
        insights=map_insight_to_str(insight.model_dump()),
    )


def evaluate_paper_quality(
    idea: ResearchIdea,
    insight: ResearchInsight,
    paper: ResearchPaperSubmission,
    model_name: str,
    config: Config,
) -> ResearchPaperSubmissionEvalOutput:
    evaluator = ResearchPaperSubmissionQualityEvaluator(
        model_name=model_name, config=config
    )
    return evaluator.eval(
        idea=idea.model_dump(),
        insights=insight.model_dump(),
        paper=paper.model_dump(),
    )


def evaluate_review_quality(
    idea: ResearchIdea,
    insight: ResearchInsight,
    paper: ResearchPaperSubmission,
    review: ResearchReview,
    meta_review: ResearchMetaReview,
    model_name: str,
    config: Config,
) -> ResearchReviewEvalOutput:
    evaluator = ResearchReviewQualityEvaluator(model_name=model_name, config=config)
    return evaluator.eval(
        idea=idea.model_dump(),
        insights=insight.model_dump(),
        paper=paper.model_dump(),
        review=review.model_dump(),
        decision=meta_review.model_dump(),
    )


def evaluate_rebuttal_quality(
    idea: ResearchIdea,
    insight: ResearchInsight,
    paper: ResearchPaperSubmission,
    review: ResearchReview,
    rebuttal: ResearchRebuttal,
    model_name: str,
    config: Config,
) -> ResearchRebuttalEvalOutput:
    evaluator = ResearchRebuttalQualityEvaluator(model_name=model_name, config=config)
    return evaluator.eval(
        idea=idea.model_dump(),
        insights=insight.model_dump(),
        paper=paper.model_dump(),
        review=review.model_dump(),
        rebuttal=rebuttal.model_dump(),
    )


def evaluate_meta_review_quality(
    idea: ResearchIdea,
    insight: ResearchInsight,
    paper: ResearchPaperSubmission,
    reviews: List[ResearchReview],
    rebuttals: List[ResearchRebuttal],
    meta_review: ResearchMetaReview,
    model_name: str,
    config: Config,
) -> ResearchMetaReviewEvalOutput:
    evaluator = ResearchMetaReviewQualityEvaluator(model_name=model_name, config=config)
    return evaluator.eval(
        idea=idea.model_dump(),
        insights=insight.model_dump(),
        paper=paper.model_dump(),
        review=[review.model_dump() for review in reviews],
        rebuttal=[rebuttal.model_dump() for rebuttal in rebuttals],
        meta_review=meta_review.model_dump(),
    )


def pipeline_eval(
    insight: ResearchInsight,
    idea: ResearchIdea,
    paper: ResearchPaperSubmission,
    reviews: List[ResearchReview],
    rebuttals: List[ResearchRebuttal],
    meta_review: ResearchMetaReview,
    model_name: str = 'together_ai/mistralai/Mixtral-8x7B-Instruct-v0.1',
    config: Config = Config(),
) -> Tuple[
    ResearchInsightEvalOutput,
    ResearchIdeaEvalOutput,
    ResearchPaperSubmissionEvalOutput,
    List[ResearchReviewEvalOutput],
    List[ResearchRebuttalEvalOutput],
    ResearchMetaReviewEvalOutput,
]:
    insight_quality = evaluate_insight_quality(insight, model_name, config)
    idea_quality = evaluate_idea_quality(idea, insight, model_name, config)
    paper_quality = evaluate_paper_quality(idea, insight, paper, model_name, config)
    reviews_quality = [
        evaluate_review_quality(
            idea, insight, paper, review, meta_review, model_name, config
        )
        for review in reviews
    ]
    rebuttals_quality = [
        evaluate_rebuttal_quality(
            idea, insight, paper, review, rebuttal, model_name, config
        )
        for review, rebuttal in zip(reviews, rebuttals)
    ]
    meta_review_quality = evaluate_meta_review_quality(
        idea, insight, paper, reviews, rebuttals, meta_review, model_name, config
    )

    return (
        insight_quality,
        idea_quality,
        paper_quality,
        reviews_quality,
        rebuttals_quality,
        meta_review_quality,
    )


def main(
    model_name: str = 'together_ai/mistralai/Mixtral-8x7B-Instruct-v0.1',
    config_file_path: str = '../../configs/default_config.yaml',
    load_file_path: str = '../../examples/research_town_demo_log',
    save_file_path: str = '../../examples/research_town_demo_log',
) -> None:
    # step 1: load the log from file
    progress_db = ProgressDB(load_file_path)
    insight = progress_db.get(ResearchInsight)[0]
    idea = progress_db.get(ResearchIdea)[0]
    paper = progress_db.get(ResearchPaperSubmission)[0]
    reviews = progress_db.get(ResearchReview)
    rebuttals = progress_db.get(ResearchRebuttal)
    meta_review = progress_db.get(ResearchMetaReview)[0]
    config = Config(config_file_path)

    # step 3: evaluations
    (
        insight_quality,
        idea_quality,
        paper_quality,
        reviews_quality,
        rebuttals_quality,
        meta_review_quality,
    ) = pipeline_eval(
        insight=insight,
        idea=idea,
        paper=paper,
        reviews=reviews,
        rebuttals=rebuttals,
        meta_review=meta_review,
        model_name=model_name,
        config=config,
    )

    # step 4: store the evaluation results to database
    progress_db.update(
        ResearchInsight,
        updates={'eval_score': insight_quality.dimension_scores},
        pk=insight.pk,
    )
    progress_db.update(
        ResearchIdea,
        updates={'eval_score': idea_quality.dimension_scores},
        pk=insight.pk,
    )
    progress_db.update(
        ResearchPaperSubmission,
        updates={'eval_score': paper_quality.dimension_scores},
        pk=insight.pk,
    )
    for review, review_quality in zip(reviews, reviews_quality):
        progress_db.update(
            ResearchReview,
            updates={'eval_score': review_quality.dimension_scores},
            pk=review.pk,
        )
    for rebuttal, rebuttal_quality in zip(rebuttals, rebuttals_quality):
        progress_db.update(
            ResearchRebuttal,
            updates={'eval_score': rebuttal_quality.dimension_scores},
            pk=rebuttal.pk,
        )
    progress_db.update(
        ResearchMetaReview,
        updates={'eval_score': meta_review_quality.dimension_scores},
        pk=meta_review.pk,
    )

    # step 5: save the database logs with evaluation results to file
    progress_db.save_to_json(save_file_path)


if __name__ == '__main__':
    main()
