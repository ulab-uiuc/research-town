from research_town.kbs import (
    AgentAgentDiscussionLog,
    AgentPaperMetaReviewLog,
    AgentPaperRebuttalLog,
    AgentPaperReviewLog,
    PaperProfile,   
    AgentProfile,
    ResearchOutput,
)
import uuid

paper_profile = PaperProfile(
    paper_id=str(uuid.uuid4()),
    title="A Survey on Machine Learning",
    abstract="This paper surveys the field of machine learning.",
)

agent_profile_A = AgentProfile(
    agent_id=str(uuid.uuid4()),
    name="Jiaxuan You",
    profile="A researcher in the field of machine learning.",
)

agent_profile_B = AgentProfile(
    agent_id=str(uuid.uuid4()),
    name="Rex Ying",
    profile="A researcher in the field of GNN.",
)

research_output = ResearchOutput(
    output_id=str(uuid.uuid4()),
    paper_id=paper_profile.paper_id,
    idea="A new idea",
)

agent_agent_discussion_log = AgentAgentDiscussionLog(
    timestep=0,
    discussion_id=str(uuid.uuid4()),
    agent_from_id=agent_profile_A.agent_id,
    agent_to_id=agent_profile_B.agent_id,
    message="good morning",
)

agent_paper_review_log = AgentPaperReviewLog(
    timestep=0,
    review_id=str(uuid.uuid4()),
    paper_id=paper_profile.paper_id,
    agent_id=agent_profile_A.agent_id,
    review_score=5,
    review_content="This paper is well-written.",
)

agent_paper_meta_review_log = AgentPaperMetaReviewLog(
    timestep=0,
    decision_id=str(uuid.uuid4()),
    paper_id=paper_profile.paper_id,
    agent_id=agent_profile_B.agent_id,
    decision="accept",
    meta_review="This paper is well-written.",
)
