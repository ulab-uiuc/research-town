from research_town.dbs import (
    ResearchIdea,  # Idea
    ResearchInsight,
    ResearchPaperSubmission,  # Paper
    AgentPaperReviewLog,  # Review
    AgentPaperMetaReviewLog,
    AgentPaperRebuttalLog,
)

from research_town.evaluators import (
    IdeaQualityEvaluator,
    PaperQualityEvaluator,
    ReviewQualityEvaluator,
    IdeaEvalOutput,
    ReviewEvalOutput,
    PaperEvalOutput,
)


def run_sync_evaluation():
    idea_quality_evaluator = IdeaQualityEvaluator(model_name="gpt-4")
    paper_quality_evaluator = PaperQualityEvaluator(model_name="gpt-4")
    review_quality_evaluator = ReviewQualityEvaluator(model_name="gpt-4")
    pass


def main() -> None:
    run_sync_evaluation()


if __name__ == '__main__':
    main()
