from research_town.dbs import (
    ResearchIdea,
    ResearchInsight,
    ResearchMetaReviewForPaperSubmission,
    ResearchPaperSubmission,
    ResearchRebuttalForPaperSubmission,
    ResearchReviewForPaperSubmission,
)


def test_researchprogress_class_extra_args() -> None:
    idea = ResearchIdea(content='Idea for a new AI algorithm', extra='extra')
    assert hasattr(idea, 'extra')
    assert idea.extra == 'extra'

    insight = ResearchInsight(content='Insight for a new AI algorithm', extra='extra')
    assert hasattr(insight, 'extra')
    assert insight.extra == 'extra'

    paper = ResearchPaperSubmission(
        content='Paper for a new AI algorithm', extra='extra'
    )
    assert hasattr(paper, 'extra')
    assert paper.extra == 'extra'

    review = ResearchReviewForPaperSubmission(
        content='Review for a new AI algorithm', extra='extra'
    )
    assert hasattr(review, 'extra')
    assert review.extra == 'extra'

    rebuttal = ResearchRebuttalForPaperSubmission(
        content='Rebuttal for a new AI algorithm', extra='extra'
    )
    assert hasattr(rebuttal, 'extra')
    assert rebuttal.extra == 'extra'

    meta_review = ResearchMetaReviewForPaperSubmission(
        content='Meta Review for a new AI algorithm', extra='extra'
    )
    assert hasattr(meta_review, 'extra')
    assert meta_review.extra == 'extra'
