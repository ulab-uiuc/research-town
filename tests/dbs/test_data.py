from research_town.dbs import (
    ResearchIdea,
    ResearchInsight,
    ResearchMetaReview,
    ResearchProposal,
    ResearchRebuttal,
    ResearchReview,
)


def test_researchprogress_class_extra_args() -> None:
    idea = ResearchIdea(content='Idea for a new AI algorithm', additional_attr='extra')
    assert hasattr(idea, 'additional_attr')
    assert idea.additional_attr == 'extra'

    insight = ResearchInsight(
        content='Insight for a new AI algorithm', additional_attr='extra'
    )
    assert hasattr(insight, 'additional_attr')
    assert insight.additional_attr == 'extra'

    paper = ResearchProposal(
        title='title', abstract='Paper for a new AI algorithm', additional_attr='extra'
    )
    assert hasattr(paper, 'additional_attr')
    assert paper.additional_attr == 'extra'

    review = ResearchReview(
        content='Review for a new AI algorithm', additional_attr='extra'
    )
    assert hasattr(review, 'additional_attr')
    assert review.additional_attr == 'extra'

    rebuttal = ResearchRebuttal(
        content='Rebuttal for a new AI algorithm', additional_attr='extra'
    )
    assert hasattr(rebuttal, 'additional_attr')
    assert rebuttal.additional_attr == 'extra'

    meta_review = ResearchMetaReview(
        content='Meta Review for a new AI algorithm', additional_attr='extra'
    )
    assert hasattr(meta_review, 'additional_attr')
    assert meta_review.additional_attr == 'extra'
