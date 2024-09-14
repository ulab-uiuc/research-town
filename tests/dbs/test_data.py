from research_town.dbs import Idea, Insight, MetaReview, Proposal, Rebuttal, Review


def test_researchprogress_class_extra_args() -> None:
    idea = Idea(content='Idea for a new AI algorithm', additional_attr='extra')
    assert hasattr(idea, 'additional_attr')
    assert idea.additional_attr == 'extra'

    insight = Insight(content='Insight for a new AI algorithm', additional_attr='extra')
    assert hasattr(insight, 'additional_attr')
    assert insight.additional_attr == 'extra'

    paper = Proposal(
        title='title', content='Paper for a new AI algorithm', additional_attr='extra'
    )
    assert hasattr(paper, 'additional_attr')
    assert paper.additional_attr == 'extra'

    review = Review(content='Review for a new AI algorithm', additional_attr='extra')
    assert hasattr(review, 'additional_attr')
    assert review.additional_attr == 'extra'

    rebuttal = Rebuttal(
        content='Rebuttal for a new AI algorithm', additional_attr='extra'
    )
    assert hasattr(rebuttal, 'additional_attr')
    assert rebuttal.additional_attr == 'extra'

    metareview = MetaReview(
        content='Meta Review for a new AI algorithm', additional_attr='extra'
    )
    assert hasattr(metareview, 'additional_attr')
    assert metareview.additional_attr == 'extra'
