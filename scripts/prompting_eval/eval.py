from research_town.configs import Config
from research_town.evaluators import (
    ResearchIdeaQualityEvaluator,
    ResearchInsightQualityEvaluator,
    ResearchMetaReviewQualityEvaluator,
    ResearchProposalQualityEvaluator,
    ResearchRebuttalQualityEvaluator,
    ResearchReviewQualityEvaluator,
)


def main(
    model_name: str = 'together_ai/mistralai/Mixtral-8x7B-Instruct-v0.1',
    config: Config = Config(),
) -> None:
    insights = [
        {'content': 'insight1'},
        {'content': 'insight2'},
        {'content': 'insight3'},
    ]
    idea = {'content': 'idea'}
    paper = {'abstract': 'abstract'}
    reviews = [
        {
            'score': 6,
            'summary': 'review_summary1',
            'strength': 'review_strength1',
            'weakness': 'review_weakness1',
        },
        {
            'score': 7,
            'summary': 'review_summary2',
            'strength': 'review_strength2',
            'weakness': 'review_weakness2',
        },
    ]
    rebuttals = [
        {'content': 'rebuttal1'},
        {'content': 'rebuttal2'},
    ]
    meta_review = {
        'decision': 'accept',
        'summary': 'meta_review_summary',
        'strength': 'meta_review_strength',
        'weakness': 'meta_review_weakness',
    }

    insight_evaluator = ResearchInsightQualityEvaluator(model_name, config)
    idea_evaluator = ResearchIdeaQualityEvaluator(model_name, config)
    paper_evaluator = ResearchProposalQualityEvaluator(model_name, config)
    review_evaluator = ResearchReviewQualityEvaluator(model_name, config)
    rebuttal_evaluator = ResearchRebuttalQualityEvaluator(model_name, config)
    meta_review_evaluator = ResearchMetaReviewQualityEvaluator(model_name, config)

    for insight in insights:
        insight_quality = insight_evaluator.eval(insight=insight)
        print(insight_quality.overall_score)

    idea_quality = idea_evaluator.eval(insights=insights, idea=idea)
    print(idea_quality.overall_score)

    paper_quality = paper_evaluator.eval(insights=insights, idea=idea, paper=paper)
    print(paper_quality.overall_score)

    for review in reviews:
        review_quality = review_evaluator.eval(
            insights=insights, idea=idea, paper=paper, review=review
        )
        print(review_quality.overall_score)

    for review, rebuttal in zip(reviews, rebuttals):
        rebuttal_quality = rebuttal_evaluator.eval(
            insights=insights, idea=idea, paper=paper, review=review, rebuttal=rebuttal
        )
        print(rebuttal_quality.overall_score)

    meta_review_quality = meta_review_evaluator.eval(
        insights=insights,
        idea=idea,
        paper=paper,
        reviews=reviews,
        rebuttals=rebuttals,
        meta_review=meta_review,
    )
    print(meta_review_quality.overall_score)

    return


if __name__ == '__main__':
    main()
