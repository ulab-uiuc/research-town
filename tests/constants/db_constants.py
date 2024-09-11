from research_town.dbs import LogDB, PaperDB, ProgressDB, AgentDB

from .data_constants import (
    agent_agent_idea_discussion_log,
    agent_paper_meta_review_log,
    agent_paper_rebuttal_log,
    agent_paper_review_log,
    agent_profile_A,
    agent_profile_B,
    agent_profile_C,
    paper_profile_A,
    paper_profile_B,
    paper_profile_C,
    research_idea_A,
    research_idea_B,
    research_insight_A,
    research_insight_B,
    research_paper_submission_A,
    research_paper_submission_B,
)

example_agent_db = AgentDB()
example_agent_db.add(agent_profile_A)
example_agent_db.add(agent_profile_B)
example_agent_db.add(agent_profile_C)

example_paper_db = PaperDB()
example_paper_db.add(paper_profile_A)
example_paper_db.add(paper_profile_B)
example_paper_db.add(paper_profile_C)

example_progress_db = ProgressDB()
example_progress_db.add(research_idea_A)
example_progress_db.add(research_idea_B)
example_progress_db.add(research_insight_A)
example_progress_db.add(research_insight_B)
example_progress_db.add(research_paper_submission_A)
example_progress_db.add(research_paper_submission_B)

example_env_db = LogDB()
example_env_db.add(agent_paper_review_log)
example_env_db.add(agent_paper_rebuttal_log)
example_env_db.add(agent_paper_meta_review_log)
example_env_db.add(agent_agent_idea_discussion_log)
