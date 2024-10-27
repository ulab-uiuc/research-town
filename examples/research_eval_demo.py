from research_town.configs import Config
from research_town.data import Idea, Insight, MetaReview, Proposal, Rebuttal, Review
from research_town.dbs import ProgressDB
from research_town.evaluators import BaseEvaluator


def main(
    model_name: str = 'openai/gpt-4o-mini',
    config_file_path: str = '../configs',
) -> None:
    # step 1: load the log from file
    config = Config(config_file_path)
    conditions = {'project_name': 'research_town_demo'}
    progress_db = ProgressDB(config=config.database)
    insights = progress_db.get(Insight, **conditions)
    idea = progress_db.get(Idea, **conditions)[0]
    paper = progress_db.get(Proposal, **conditions)[0]
    reviews = progress_db.get(Review, **conditions)
    rebuttals = progress_db.get(Rebuttal, **conditions)
    metareview = progress_db.get(MetaReview, **conditions)[0]
    evaluator = BaseEvaluator(model_name=model_name, config=config)

    # step 3: evaluations
    (
        insights_quality,
        idea_quality,
        paper_quality,
        reviews_quality,
        rebuttals_quality,
        metareview_quality,
    ) = evaluator.pipeline_eval(
        insights=insights,
        idea=idea,
        paper=paper,
        reviews=reviews,
        rebuttals=rebuttals,
        metareview=metareview,
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
        updates={'eval_score': metareview_quality.dimension_scores},
        pk=metareview.pk,
    )


if __name__ == '__main__':
    main()
