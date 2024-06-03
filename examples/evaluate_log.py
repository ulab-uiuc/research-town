import json

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
    insight_list: ResearchInsight,
    idea_list: ResearchIdea,
    paper_list: ResearchPaperSubmission,
    review_list: AgentPaperReviewLog,
    meta_review_list: AgentPaperMetaReviewLog,
    model_name: str = 'together_ai/mistralai/Mixtral-8x7B-Instruct-v0.1',
) -> None:
    # Serialize Logs
    insight_serialize = f'content: {insight_list.content}'
    idea_serialize = f'content: {idea_list.content}'
    paper_serialize = {
        'title': paper_list.title,
        'abstract': paper_list.abstract,
        'conference': paper_list.conference,
    }
    review_serialize = (
        f'score: {review_list.review_score}\ncontent: {review_list.review_content}'
    )
    meta_review_serialize = f'decision: {meta_review_list.decision}\nmeta review:{meta_review_list.meta_review}'
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
    with open('examples/evaluate_log/idea_quality.json', 'w') as file:
        json.dump(idea_quality.dict(), file)
    with open('examples/evaluate_log/paper_quality.json', 'w') as file:
        json.dump(paper_quality.dict(), file)
    with open('examples/evaluate_log/review_quality.json', 'w') as file:
        json.dump(review_quality.dict(), file)


def main() -> None:
    run_sync_evaluation(
        insight_list=insight_A,
        idea_list=idea_A,
        paper_list=paper_submission_A,
        review_list=paper_review_A,
        meta_review_list=paper_meta_review_A,
    )


if __name__ == '__main__':
    main()
