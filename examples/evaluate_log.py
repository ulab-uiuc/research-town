from typing import List
import json

from research_town.utils.serializer import Serializer

from .evaluator_constants import (
    insight_A,
    idea_A,
    paper_submission_A,
    paper_review_A,
    paper_meta_review_A
)

from research_town.dbs import (
    ResearchIdea,  # Idea
    ResearchInsight,  # Trend
    ResearchPaperSubmission,  # Paper
    AgentPaperReviewLog,  # Review
    AgentPaperMetaReviewLog,  # Meta-Review
)

from research_town.evaluators import (
    IdeaQualityEvaluator,
    PaperQualityEvaluator,
    ReviewQualityEvaluator,
    IdeaEvalOutput,
    ReviewEvalOutput,
    PaperEvalOutput,
)


def run_sync_evaluation(insight_list: List[ResearchInsight], idea_list: List[ResearchIdea],  paper_list: List[ResearchPaperSubmission], review_list: List[AgentPaperReviewLog], meta_review_list: List[AgentPaperMetaReviewLog], model_name: str | None = "together_ai/mistralai/Mixtral-8x7B-Instruct-v0.1"):

    # Serialize Logs
    serializer = Serializer()
    print(serializer.serialize(serializer.serialize(idea_list[0])))
    insight_serialize = "\n\n".join(
        [serializer.serialize(insight) for insight in insight_list])
    idea_serialize = "\n\n".join(
        [serializer.serialize(idea) for idea in idea_list])
    paper_serialize = "\n\n".join(
        [serializer.serialize(paper) for paper in paper_list])
    review_serialize = "\n\n".join(
        [serializer.serialize(review) for review in review_list])
    meta_review_serialize = "\n\n".join(
        [serializer.serialize(meta_review) for meta_review in meta_review_list])
    # Create Evaluators
    idea_quality_evaluator = IdeaQualityEvaluator(model_name="gpt-4")
    paper_quality_evaluator = PaperQualityEvaluator(model_name="gpt-4")
    review_quality_evaluator = ReviewQualityEvaluator(model_name="gpt-4")
    # Generate Evaluation
    idea_quality = idea_quality_evaluator.eval({
        "idea": idea_serialize,
        "trend": insight_serialize
    })
    paper_quality = paper_quality_evaluator.eval({
        "idea": idea_serialize,
        "trend": insight_serialize,
        "paper": paper_serialize,
    })
    review_quality = review_quality_evaluator.eval({
        "idea": idea_serialize,
        "trend": insight_serialize,
        "paper": paper_serialize,
        "review": review_serialize,
        "decision": meta_review_serialize
    })
    # Save Logs
    with open("evaluate_log/idea_quality.json", "w") as file:
        json.dumps(idea_quality.dict(), indent=4)
    with open("evaluate_log/paper_quality.json", "w") as file:
        json.dumps(paper_quality.dict(), indent=4)
    with open("evaluate_log/review_quality.json", "w") as file:
        json.dumps(review_quality.dict(), indent=4)


def main() -> None:
    run_sync_evaluation(
        insight_list=[insight_A],
        idea_list=[idea_A],
        paper_list=[paper_submission_A],
        review_list=[paper_review_A],
        meta_review_list=[paper_meta_review_A]
    )


if __name__ == '__main__':
    main()
