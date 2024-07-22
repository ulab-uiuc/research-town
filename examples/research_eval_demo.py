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
from research_town.evaluators import BaseEvaluator


def main(
    model_name: str = 'openai/gpt-4o',
    config_file_path: str = '../configs/default_config.yaml',
    load_file_path: str = './research_town_demo_log',
    save_file_path: str = './research_eval_demo_log',
) -> None:
    # step 1: load the log from file
    conditions = {'project_name': 'research_town_demo'}
    progress_db = ProgressDB(load_file_path)
    insights = progress_db.get(ResearchInsight, **conditions)
    idea = progress_db.get(ResearchIdea, **conditions)[0]
    paper = progress_db.get(ResearchPaperSubmission, **conditions)[0]
    reviews = progress_db.get(ResearchReview, **conditions)
    rebuttals = progress_db.get(ResearchRebuttal, **conditions)
    meta_review = progress_db.get(ResearchMetaReview, **conditions)[0]
    config = Config(config_file_path)
    evaluator = BaseEvaluator(model_name=model_name, config=config)

    # step 3: evaluations
    (
        insights_quality,
        idea_quality,
        paper_quality,
        reviews_quality,
        rebuttals_quality,
        meta_review_quality,
    ) = evaluator.pipeline_eval(
        insights=insights,
        idea=idea,
        paper=paper,
        reviews=reviews,
        rebuttals=rebuttals,
        meta_review=meta_review,
    )

    # step 4: store the evaluation results to database
    for insight, insight_quality in zip(insights, insights_quality):
        progress_db.update(
            ResearchInsight,
            updates={'eval_score': insight_quality.dimension_scores},
            pk=insight.pk,
        )
    progress_db.update(
        ResearchIdea,
        updates={'eval_score': idea_quality.dimension_scores},
        pk=idea.pk,
    )
    progress_db.update(
        ResearchPaperSubmission,
        updates={'eval_score': paper_quality.dimension_scores},
        pk=paper.pk,
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
