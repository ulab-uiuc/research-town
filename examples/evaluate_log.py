import json
from typing import List

from research_town.dbs import AgentPaperMetaReviewLog  # Meta-Review
from research_town.dbs import AgentPaperReviewLog  # Review
from research_town.dbs import ResearchIdea  # Idea
from research_town.dbs import ResearchInsight  # Trend
from research_town.dbs import ResearchPaperSubmission  # Paper
from research_town.evaluators import (
    IdeaQualityEvaluator,
    PaperQualityEvaluator,
    ReviewQualityEvaluator,
)

from .evaluator_constants import (
    idea_A,
    insight_A,
    paper_meta_review_A,
    paper_review_A,
    paper_submission_A,
)


def run_sync_evaluation(
    insight_list: List[ResearchInsight],
    idea_list: List[ResearchIdea],
    paper_list: List[ResearchPaperSubmission],
    review_list: List[AgentPaperReviewLog],
    meta_review_list: List[AgentPaperMetaReviewLog],
    model_name: str | None = 'together_ai/mistralai/Mixtral-8x7B-Instruct-v0.1',
):
    # Serialize Logs
    insight_serialize = '\n\n'.join(
        [f'Content: {insight.content}' for insight in insight_list]
    )
    idea_serialize = '\n\n'.join(
        [f'Content: {idea.content}' for idea in idea_list])
    paper_serialize = '\n\n'.join(
        [
            f'Title: {paper.title}\nAbstract: {paper.abstract}\nConference: {paper.conference}'
            for paper in paper_list
        ]
    )
    review_serialize = '\n\n'.join(
        [
            f'Score: {review.review_score}\nContent: {review.review_content}'
            for review in review_list
        ]
    )
    meta_review_serialize = '\n\n'.join(
        [
            f'Decision: {meta_review.decision}\nMeta Review:{meta_review.meta_review}'
            for meta_review in meta_review_list
        ]
    )
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
    with open('evaluate_log/idea_quality.json', 'w') as file:
        json.dump(idea_quality.dict(), file)
    with open('evaluate_log/paper_quality.json', 'w') as file:
        json.dump(paper_quality.dict(), file)
    with open('evaluate_log/review_quality.json', 'w') as file:
        json.dump(review_quality.dict(), file)


def main() -> None:
    run_sync_evaluation(
        insight_list=[insight_A],
        idea_list=[idea_A],
        paper_list=[paper_submission_A],
        review_list=[paper_review_A],
        meta_review_list=[paper_meta_review_A],
    )


if __name__ == '__main__':
    main()
