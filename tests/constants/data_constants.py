from research_town.dbs import (
    AgentAgentIdeaDiscussionLog,
    AgentPaperMetaReviewWritingLog,
    AgentPaperRebuttalWritingLog,
    AgentPaperReviewWritingLog,
    AgentProfile,
    PaperProfile,
    ResearchIdea,
    ResearchInsight,
    ResearchMetaReview,
    ResearchProposal,
    ResearchRebuttal,
    ResearchReview,
)

paper_profile_A = PaperProfile(
    title='A Survey on Machine Learning',
    abstract='This paper surveys the field of machine learning.',
)

paper_profile_B = PaperProfile(
    title='A Survey on Graph Neural Networks',
    abstract='This paper surveys the field of graph neural networks.',
)

paper_profile_C = PaperProfile(
    title='A Survey on Natural Language Processing',
    abstract='This paper surveys the field of natural language processing.',
)


agent_profile_A = AgentProfile(
    name='Jiaxuan You',
    bio='A researcher in the field of machine learning.',
)

agent_profile_B = AgentProfile(
    name='Rex Ying',
    bio='A researcher in the field of GNN.',
)

agent_profile_C = AgentProfile(
    name='Chris Manning',
    bio='A researcher in the field of NLP.',
)

research_idea_A = ResearchIdea(
    content='A new idea',
)

research_idea_B = ResearchIdea(
    content='Another idea',
)

research_insight_A = ResearchInsight(
    content='A new insight',
)

research_insight_B = ResearchInsight(
    content='Another insight',
)


research_paper_submission_A = ResearchProposal(
    title='A Survey on Machine Learning',
    abstract='This paper surveys the field of machine learning.',
)

research_paper_submission_B = ResearchProposal(
    title='A Survey on Graph Neural Networks',
    abstract='This paper surveys the field of graph neural networks.',
)

research_review_A = ResearchReview(
    paper_pk=paper_profile_A.pk,
    reviewer_pk=agent_profile_A.pk,
    summary='This paper is well-written.',
    strength='Interesting',
    weakness='None',
    score=5,
)

research_review_B = ResearchReview(
    paper_pk=paper_profile_A.pk,
    reviewer_pk=agent_profile_B.pk,
    summary='This paper is well-written.',
    strength='Interesting',
    weakness='None',
    score=5,
)

research_review_C = ResearchReview(
    paper_pk=paper_profile_A.pk,
    reviewer_pk=agent_profile_C.pk,
    summary='This paper is well-written.',
    strength='Interesting',
    weakness='None',
    score=5,
)

research_rebuttal_A = ResearchRebuttal(
    paper_pk=paper_profile_A.pk,
    agent_pk=agent_profile_A.pk,
    content='I have revised the paper.',
)

research_rebuttal_B = ResearchRebuttal(
    paper_pk=paper_profile_A.pk,
    agent_pk=agent_profile_B.pk,
    content='I have revised the paper.',
)

research_meta_review_A = ResearchMetaReview(
    paper_pk=paper_profile_A.pk,
    agent_pk=agent_profile_A.pk,
    decision=True,
    summary='This paper is well-written.',
    strength='Interesting',
    weakness='None',
)

research_meta_review_B = ResearchMetaReview(
    paper_pk=paper_profile_A.pk,
    agent_pk=agent_profile_B.pk,
    decision=True,
    summary='This paper is well-written.',
    strength='Interesting',
    weakness='None',
)

agent_paper_review_log = AgentPaperReviewWritingLog(
    time_step=0,
    paper_pk=paper_profile_A.pk,
    agent_pk=agent_profile_A.pk,
    score=5,
    summary='This paper is well-written.',
    strength='Interesting',
    weakness='None',
)

agent_paper_meta_review_log = AgentPaperMetaReviewWritingLog(
    time_step=0,
    paper_pk=paper_profile_B.pk,
    agent_pk=agent_profile_B.pk,
    decision=True,
    summary='This paper is well-written.',
    strength='Interesting',
    weakness='None',
)

agent_paper_rebuttal_log = AgentPaperRebuttalWritingLog(
    time_step=0,
    paper_pk=paper_profile_A.pk,
    agent_pk=agent_profile_A.pk,
    rebuttal_content='I have revised the paper.',
)

agent_agent_idea_discussion_log = AgentAgentIdeaDiscussionLog(
    time_step=0,
    agent_from_pk=agent_profile_A.pk,
    agent_from_name=agent_profile_A.name,
    agent_to_pk=agent_profile_B.pk,
    agent_to_name=agent_profile_B.name,
    message='How about the idea of building a research town with language agents?',
)
