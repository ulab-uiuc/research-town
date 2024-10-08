from research_town.data import (
    Idea,
    Insight,
    MetaReview,
    MetaReviewWritingLog,
    Paper,
    Profile,
    Proposal,
    Rebuttal,
    RebuttalWritingLog,
    Review,
    ReviewWritingLog,
)

paper_A = Paper(
    title='A Survey on Machine Learning',
    abstract='This paper surveys the field of machine learning.',
)

paper_B = Paper(
    title='A Survey on Graph Neural Networks',
    abstract='This paper surveys the field of graph neural networks.',
)

paper_C = Paper(
    title='A Survey on Natural Language Processing',
    abstract='This paper surveys the field of natural language processing.',
)


profile_A = Profile(
    name='Jiaxuan You',
    bio='A researcher in the field of machine learning.',
)

profile_B = Profile(
    name='Rex Ying',
    bio='A researcher in the field of GNN.',
)

profile_C = Profile(
    name='Chris Manning',
    bio='A researcher in the field of NLP.',
)

research_idea_A = Idea(
    content='A new idea',
)

research_idea_B = Idea(
    content='Another idea',
)

research_insight_A = Insight(
    content='A new insight',
)

research_insight_B = Insight(
    content='Another insight',
)


research_proposal_A = Proposal(
    title='A Survey on Machine Learning',
    content='This paper surveys the field of machine learning.',
)

research_proposal_B = Proposal(
    title='A Survey on Graph Neural Networks',
    content='This paper surveys the field of graph neural networks.',
)

research_review_A = Review(
    paper_pk=paper_A.pk,
    reviewer_pk=profile_A.pk,
    summary='This paper is well-written.',
    strength='Interesting',
    weakness='None',
    score=5,
)

research_review_B = Review(
    paper_pk=paper_A.pk,
    reviewer_pk=profile_B.pk,
    summary='This paper is well-written.',
    strength='Interesting',
    weakness='None',
    score=5,
)

research_review_C = Review(
    paper_pk=paper_A.pk,
    reviewer_pk=profile_C.pk,
    summary='This paper is well-written.',
    strength='Interesting',
    weakness='None',
    score=5,
)

research_rebuttal_A = Rebuttal(
    paper_pk=paper_A.pk,
    profile_pk=profile_A.pk,
    content='I have revised the paper.',
)

research_rebuttal_B = Rebuttal(
    paper_pk=paper_A.pk,
    profile_pk=profile_B.pk,
    content='I have revised the paper.',
)

research_metareview_A = MetaReview(
    paper_pk=paper_A.pk,
    profile_pk=profile_A.pk,
    decision=True,
    summary='This paper is well-written.',
    strength='Interesting',
    weakness='None',
)

research_metareview_B = MetaReview(
    paper_pk=paper_A.pk,
    profile_pk=profile_B.pk,
    decision=True,
    summary='This paper is well-written.',
    strength='Interesting',
    weakness='None',
)

agent_paper_review_log = ReviewWritingLog(
    time_step=0,
    paper_pk=paper_A.pk,
    profile_pk=profile_A.pk,
    review_pk=research_review_A.pk,
)

agent_paper_metareview_log = MetaReviewWritingLog(
    time_step=0,
    paper_pk=paper_B.pk,
    profile_pk=profile_B.pk,
    metareview_pk=research_metareview_B.pk,
)

agent_paper_rebuttal_log = RebuttalWritingLog(
    time_step=0,
    paper_pk=paper_A.pk,
    profile_pk=profile_A.pk,
    rebuttal_pk=research_rebuttal_A.pk,
)
