class AgentPaperReviewLog(object):
    timestep: int
    review_id: str
    paper_id: str
    agent_id: str
    review_score: int
    review_content: str

class AgentPaperRebuttalLog(object):
    timestep: int
    rebuttal_id: str
    paper_id: str
    agent_id: str
    rebuttal_content: str

class AgentPaperMetaReviewLog(object):
    timestep: int
    decision_id: str
    paper_id: str
    agent_id: str
    decision: str
    meta_review: str

class AgentAgentDiscussionLog(object):
    timestep: int
    discussion_id: str
    agent_from_id: str
    agent_to_id: str
    message: str
