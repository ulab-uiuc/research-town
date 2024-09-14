from research_town.dbs import (
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


agent_profile_A = Profile(
    name='Jiaxuan You',
    bio='A researcher in the field of machine learning.',
)

agent_profile_B = Profile(
    name='Rex Ying',
    bio='A researcher in the field of GNN.',
)

agent_profile_C = Profile(
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
    abstract='This paper surveys the field of machine learning.',
)

research_proposal_B = Proposal(
    title='A Survey on Graph Neural Networks',
    abstract='This paper surveys the field of graph neural networks.',
)

research_review_A = Review(
    paper_pk=paper_A.pk,
    reviewer_pk=agent_profile_A.pk,
    summary='This paper is well-written.',
    strength='Interesting',
    weakness='None',
    score=5,
)

research_review_B = Review(
    paper_pk=paper_A.pk,
    reviewer_pk=agent_profile_B.pk,
    summary='This paper is well-written.',
    strength='Interesting',
    weakness='None',
    score=5,
)

research_review_C = Review(
    paper_pk=paper_A.pk,
    reviewer_pk=agent_profile_C.pk,
    summary='This paper is well-written.',
    strength='Interesting',
    weakness='None',
    score=5,
)

research_rebuttal_A = Rebuttal(
    paper_pk=paper_A.pk,
    profile_pk=agent_profile_A.pk,
    content='I have revised the paper.',
)

research_rebuttal_B = Rebuttal(
    paper_pk=paper_A.pk,
    profile_pk=agent_profile_B.pk,
    content='I have revised the paper.',
)

research_meta_review_A = MetaReview(
    paper_pk=paper_A.pk,
    profile_pk=agent_profile_A.pk,
    decision=True,
    summary='This paper is well-written.',
    strength='Interesting',
    weakness='None',
)

research_meta_review_B = MetaReview(
    paper_pk=paper_A.pk,
    profile_pk=agent_profile_B.pk,
    decision=True,
    summary='This paper is well-written.',
    strength='Interesting',
    weakness='None',
)

agent_paper_review_log = ReviewWritingLog(
    time_step=0,
    paper_pk=paper_A.pk,
    profile_pk=agent_profile_A.pk,
    review_pk=research_review_A.pk,
)

agent_paper_meta_review_log = MetaReviewWritingLog(
    time_step=0,
    paper_pk=paper_B.pk,
    profile_pk=agent_profile_B.pk,
    meta_review_pk=research_meta_review_B.pk,
)

agent_paper_rebuttal_log = RebuttalWritingLog(
    time_step=0,
    paper_pk=paper_A.pk,
    profile_pk=agent_profile_A.pk,
    rebuttal_pk=research_rebuttal_A.pk,
)
