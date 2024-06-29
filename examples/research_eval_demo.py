import json

from research_town.dbs import (
    ResearchIdea,  # Idea
    ResearchInsight,  # Trend
    ResearchPaperSubmission,  # Paper
    ResearchReviewForPaperSubmission,  # Review
    ResearchRebuttalForPaperSubmission,  # Rebuttal
    ResearchMetaReviewForPaperSubmission,  # Meta Review
)
from research_town.evaluators import (
    IdeaQualityEvaluator,
    PaperQualityEvaluator,
    ReviewQualityEvaluator,
)

from examples.research_eval_constants import (
    idea_A,
    insight_A,
    paper_meta_review_A,
    paper_review_A,
    paper_submission_A,
    paper_rebuttal_A,
)


def run_sync_evaluation(
    insight: ResearchInsight,
    idea: ResearchIdea,
    paper: ResearchPaperSubmission,
    review: ResearchReviewForPaperSubmission,
    rebuttal: ResearchRebuttalForPaperSubmission,
    meta_review: ResearchMetaReviewForPaperSubmission,
    model_name: str = 'together_ai/mistralai/Mixtral-8x7B-Instruct-v0.1',
) -> None:
    # Serialize Logs
    insight_serialize = f'content: {insight.content}'
    idea_serialize = f'content: {idea.content}'
    paper_serialize = {
        'title': paper.title,
        'abstract': paper.abstract,
        'conference': paper.conference,
    }
    review_serialize = (
        f'score: {review.score}\ncontent: {review.content}'
    )
    meta_review_serialize = f'decision: {meta_review.decision}\nmeta review:{meta_review.content}'
    # Create Evaluators
    idea_quality_evaluator = IdeaQualityEvaluator(model_name=model_name)
    paper_quality_evaluator = PaperQualityEvaluator(model_name=model_name)
    review_quality_evaluator = ReviewQualityEvaluator(model_name=model_name)
    # Generate Evaluation
    idea_quality = idea_quality_evaluator.eval(
        **{'idea': idea_serialize, 'trend': insight_serialize}
    )
    paper_quality = paper_quality_evaluator.eval(
        **{
            'idea': idea_serialize,
            'trend': insight_serialize,
            'paper': paper_serialize,
        }
    )
    review_quality = review_quality_evaluator.eval(
        **{
            'idea': idea_serialize,
            'trend': insight_serialize,
            'paper': paper_serialize,
            'review': review_serialize,
            'decision': meta_review_serialize,
        }
    )
    # Save Logs
    with open('examples/research_eval_demo_log/idea_quality.json', 'w') as file:
        json.dump(idea_quality.model_dump(), file)
    with open('examples/research_eval_demo_log/paper_quality.json', 'w') as file:
        json.dump(paper_quality.model_dump(), file)
    with open('examples/research_eval_demo_log/review_quality.json', 'w') as file:
        json.dump(review_quality.model_dump(), file)


def main() -> None:
    run_sync_evaluation(
        insight=insight_A,
        idea=idea_A,
        paper=paper_submission_A,
        review=paper_review_A,
        rebuttal=paper_rebuttal_A,
        meta_review=paper_meta_review_A,
    )


if __name__ == '__main__':
    main()
