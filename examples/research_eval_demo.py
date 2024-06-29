import json
from typing import Tuple

from research_town.dbs import AgentProfile  # Agent
from research_town.dbs import PaperProfile  # Paper
from research_town.dbs import ResearchIdea  # Idea
from research_town.dbs import ResearchInsight  # Trend
from research_town.dbs import ResearchMetaReviewForPaperSubmission  # Meta Review
from research_town.dbs import ResearchPaperSubmission  # Paper
from research_town.dbs import ResearchRebuttalForPaperSubmission  # Rebuttal
from research_town.dbs import ResearchReviewForPaperSubmission  # Review
from research_town.evaluators import (
    IdeaQualityEvaluator,
    PaperQualityEvaluator,
    ReviewQualityEvaluator,
)


def set_constants() -> (
    Tuple[
        AgentProfile,
        PaperProfile,
        ResearchInsight,
        ResearchIdea,
        ResearchPaperSubmission,
        ResearchReviewForPaperSubmission,
        ResearchRebuttalForPaperSubmission,
        ResearchMetaReviewForPaperSubmission,
    ]
):
    agent_A = AgentProfile(
        name='Danqi Chen',
        bio='An Assistant Professor at Princeton University specializing on natural language processing and machine learning.',
    )

    paper_A = PaperProfile(
        title='Evaluating Large Language Models at Evaluating Instruction Following',
        abstract='As research in large language models (LLMs) continues to accelerate, LLM-based evaluation has emerged as a scalable and cost-effective alternative to human evaluations for comparing the ever increasing list of models. This paper investigates the efficacy of these “LLM evaluators”, particularly in using them to assess instruction following, a metric that gauges how closely generated text adheres to the given instruction. We introduce a challenging meta-evaluation benchmark, LLMBar, designed to test the ability of an LLM evaluator in discerning instruction-following outputs. The authors manually curated 419 pairs of outputs, one adhering to instructions while the other diverging, yet may possess deceptive qualities that mislead an LLM evaluator, e.g., a more engaging tone. Contrary to existing meta-evaluation, we discover that different evaluators (i.e., combinations of LLMs and prompts) exhibit distinct performance on LLMBar and even the highest-scoring ones have substantial room for improvement. We also present a novel suite of prompting strategies that further close the gap between LLM and human evaluators. With LLMBar, we hope to offer more insight into LLM evaluators and foster future research in developing better instruction-following models.',
    )

    insight_A = ResearchInsight(
        content='Different evaluators (i.e., combinations of LLMs and prompts) exhibit distinct performance.'
    )

    idea_A = ResearchIdea(
        content='We introduce a challenging meta-evaluation benchmark, LLMBar, designed to test the ability of an LLM evaluator in discerning instruction-following outputs.'
    )

    paper_submission_A = ResearchPaperSubmission(
        title='Evaluating Large Language Models at Evaluating Instruction Following',
        abstract='As research in large language models (LLMs) continues to accelerate, LLM-based evaluation has emerged as a scalable and cost-effective alternative to human evaluations for comparing the ever increasing list of models. This paper investigates the efficacy of these “LLM evaluators”, particularly in using them to assess instruction following, a metric that gauges how closely generated text adheres to the given instruction. We introduce a challenging meta-evaluation benchmark, LLMBar, designed to test the ability of an LLM evaluator in discerning instruction-following outputs. The authors manually curated 419 pairs of outputs, one adhering to instructions while the other diverging, yet may possess deceptive qualities that mislead an LLM evaluator, e.g., a more engaging tone. Contrary to existing meta-evaluation, we discover that different evaluators (i.e., combinations of LLMs and prompts) exhibit distinct performance on LLMBar and even the highest-scoring ones have substantial room for improvement. We also present a novel suite of prompting strategies that further close the gap between LLM and human evaluators. With LLMBar, we hope to offer more insight into LLM evaluators and foster future research in developing better instruction-following models.',
        conference='ICLR 2024',
    )

    paper_review_A = ResearchReviewForPaperSubmission(
        review_pk=agent_A.pk,
        paper_pk=paper_A.pk,
        content='This paper proposes a challenge meta-evaluator benchmark, LLMBar, used to assess the quality of the LLM-evaluator (LLM + prompt strategies) for instruction following. The paper addresses an important current problem of scalable evaluation of the LLM-evaluator’s quality, but There is some confusion in how the evaluation set was generated.',
        score=8,
    )

    paper_rebuttal_A = ResearchRebuttalForPaperSubmission(
        paper_pk=paper_A.pk,
        reviewer_pk=agent_A.pk,
        author_pk=agent_A.pk,
        content='We appreciate the reviewer for the feedback. We will provide more details on how the evaluation set was generated in the revised version of the paper.',
    )

    paper_meta_review_A = ResearchMetaReviewForPaperSubmission(
        paper_pk=paper_A.pk,
        area_chair_pk=agent_A.pk,
        review_pks=[paper_review_A.pk],
        author_pk=agent_A.pk,
        content='This paper tries to address one important problem on how to assess the of the LLM, particularly on the instruction following. It provides a carefully curated dataset that is potentially useful for "stress-testing" the LLM evaluators.',
        decision=False,
    )
    return (
        insight_A,
        idea_A,
        paper_submission_A,
        paper_review_A,
        paper_rebuttal_A,
        paper_meta_review_A,
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
    review_serialize = f'score: {review.score}\ncontent: {review.content}'
    meta_review_serialize = (
        f'decision: {meta_review.decision}\nmeta review:{meta_review.content}'
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
    with open('examples/research_eval_demo_log/idea_quality.json', 'w') as file:
        json.dump(idea_quality.model_dump(), file)
    with open('examples/research_eval_demo_log/paper_quality.json', 'w') as file:
        json.dump(paper_quality.model_dump(), file)
    with open('examples/research_eval_demo_log/review_quality.json', 'w') as file:
        json.dump(review_quality.model_dump(), file)


def main() -> None:
    (
        insight_A,
        idea_A,
        paper_submission_A,
        paper_review_A,
        paper_rebuttal_A,
        paper_meta_review_A,
    ) = set_constants()
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
