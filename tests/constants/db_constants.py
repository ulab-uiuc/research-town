from research_town.dbs import LogDB, PaperDB, ProfileDB, ProgressDB

from .data_constants import (
    agent_paper_metareview_log,
    agent_paper_rebuttal_log,
    agent_paper_review_log,
    paper_A,
    paper_B,
    paper_C,
    profile_A,
    profile_B,
    profile_C,
    research_idea_A,
    research_idea_B,
    research_insight_A,
    research_insight_B,
    research_proposal_A,
    research_proposal_B,
)

example_profile_db = ProfileDB()
example_profile_db.add(profile_A)
example_profile_db.add(profile_B)
example_profile_db.add(profile_C)

example_paper_db = PaperDB()
example_paper_db.add(paper_A)
example_paper_db.add(paper_B)
example_paper_db.add(paper_C)

example_progress_db = ProgressDB()
example_progress_db.add(research_idea_A)
example_progress_db.add(research_idea_B)
example_progress_db.add(research_insight_A)
example_progress_db.add(research_insight_B)
example_progress_db.add(research_proposal_A)
example_progress_db.add(research_proposal_B)

example_log_db = LogDB()
example_log_db.add(agent_paper_review_log)
example_log_db.add(agent_paper_rebuttal_log)
example_log_db.add(agent_paper_metareview_log)
