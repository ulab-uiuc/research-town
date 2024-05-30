
from research_town.dbs.agent_db import AgentProfile, AgentProfileDB
from research_town.dbs.paper_db import PaperProfile
from research_town.dbs.env_db import AgentPaperReviewLog
from research_town.agents.agent_base import BaseResearchAgent
from typing import List


def rank_consistency(reviews: List[AgentPaperReviewLog]) -> float:
     pass

def main() -> None:
    # collect papers from openreview
    PaperProfile()
    Papers2eval:List[PaperProfile] = []
    # generate envs of agents with reviewers
    # 1. how to select reviewers? Retrive the reviewers from the database.
    agent_db = AgentProfileDB()
    domain = "machine_learning_system"
    agent_db.load_from_file(domain + ".json")
    # 2. how to assign reviewers to papers?(jinwei) Hardcode--Select random x=1 reviewers first.
    agent_pk = '101'
    Chris = agent_db.data[agent_pk]
    agent_profiles = [Chris]
    agents: List[BaseResearchAgent] = []
    for agent_profile in agent_profiles:
            agents.append(
                BaseResearchAgent(
                    agent_profile=agent_profile,
                    model_name='together_ai/mistralai/Mixtral-8x7B-Instruct-v0.1',
                )
            )
    
    # review papers
    # 3. how to get the scores of papers? Store to review log lists.
    reviews: List[AgentPaperReviewLog] = []
    for agent in agents:
        reviews.append(agent.write_paper_review(
             paper=Papers2eval[0])
        )
    
    # get ranking consistency
    
    pass


if __name__ == '__main__':
    main()