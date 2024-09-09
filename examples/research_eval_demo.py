from research_town.configs import Config
from research_town.dbs import (
    Idea,
    Insight,
    MetaReview,
    ProgressDB,
    Proposal,
    Rebuttal,
    Review,
)
from research_town.evaluators import BaseEvaluator


def main(
    model_name: str = 'openai/gpt-4o',
    config_file_path: str = '../configs',
    load_file_path: str = './research_town_demo_log',
    save_file_path: str = './research_eval_demo_log',
) -> None:
    # step 1: load the log from file
    conditions = {'project_name': 'research_town_demo'}
    progress_db = ProgressDB(load_file_path)
    insights = progress_db.get(Insight, **conditions)
    idea = progress_db.get(Idea, **conditions)[0]
    paper = progress_db.get(Proposal, **conditions)[0]
    reviews = progress_db.get(Review, **conditions)
    rebuttals = progress_db.get(Rebuttal, **conditions)
    meta_review = progress_db.get(MetaReview, **conditions)[0]
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
            Insight,
            updates={'eval_score': insight_quality.dimension_scores},
            pk=insight.pk,
        )
    progress_db.update(
        Idea,
        updates={'eval_score': idea_quality.dimension_scores},
        pk=idea.pk,
    )
    progress_db.update(
        Proposal,
        updates={'eval_score': paper_quality.dimension_scores},
        pk=paper.pk,
    )
    for review, review_quality in zip(reviews, reviews_quality):
        progress_db.update(
            Review,
            updates={'eval_score': review_quality.dimension_scores},
            pk=review.pk,
        )
    for rebuttal, rebuttal_quality in zip(rebuttals, rebuttals_quality):
        progress_db.update(
            Rebuttal,
            updates={'eval_score': rebuttal_quality.dimension_scores},
            pk=rebuttal.pk,
        )
    progress_db.update(
        MetaReview,
        updates={'eval_score': meta_review_quality.dimension_scores},
        pk=meta_review.pk,
    )

    # step 5: save the database logs with evaluation results to file
    progress_db.save_to_json(save_file_path)


if __name__ == '__main__':
    main()
