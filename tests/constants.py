from research_town.dbs import (
    AgentAgentDiscussionLog,
    AgentPaperMetaReviewLog,
    AgentPaperRebuttalLog,
    AgentPaperReviewLog,
    AgentProfile,
    PaperProfile,
    ResearchIdea,
    ResearchInsight,
    ResearchPaperSubmission,
)

paper_profile_A = PaperProfile(
    title='A Survey on Machine Learning',
    abstract='This paper surveys the field of machine learning.',
)

paper_profile_B = PaperProfile(
    title='A Survey on Graph Neural Networks',
    abstract='This paper surveys the field of graph neural networks.',
)


agent_profile_A = AgentProfile(
    name='Jiaxuan You',
    bio='A researcher in the field of machine learning.',
)

agent_profile_B = AgentProfile(
    name='Rex Ying',
    bio='A researcher in the field of GNN.',
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

research_paper_submission_A = ResearchPaperSubmission(
    title='A Survey on Machine Learning',
    abstract='This paper surveys the field of machine learning.',
)

research_paper_submission_B = ResearchPaperSubmission(
    title='A Survey on Graph Neural Networks',
    abstract='This paper surveys the field of graph neural networks.',
)


agent_paper_review_log = AgentPaperReviewLog(
    timestep=0,
    paper_pk=paper_profile_A.pk,
    agent_pk=agent_profile_A.pk,
    review_score=5,
    review_content='This paper is well-written.',
)

agent_paper_meta_review_log = AgentPaperMetaReviewLog(
    timestep=0,
    paper_pk=paper_profile_B.pk,
    agent_pk=agent_profile_B.pk,
    decision=True,
    meta_review='This paper is well-written.',
)

agent_paper_rebuttal_log = AgentPaperRebuttalLog(
    timestep=0,
    paper_pk=paper_profile_A.pk,
    agent_pk=agent_profile_A.pk,
    rebuttal_content='I have revised the paper.',
)

agent_agent_discussion_log = AgentAgentDiscussionLog(
    timestep=0,
    agent_from_pk=agent_profile_A.pk,
    agent_from_name=agent_profile_A.name,
    agent_to_pk=agent_profile_B.pk,
    agent_to_name=agent_profile_B.name,
    message='How about the idea of building a research town with language agents?',
)
