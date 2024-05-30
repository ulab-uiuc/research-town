
from research_town.dbs.agent_db import AgentProfile, AgentProfileDB
from research_town.dbs.paper_db import PaperProfile, PaperProfileDB
from research_town.dbs.env_db import AgentPaperReviewLog
from research_town.agents.agent_base import BaseResearchAgent
from typing import List, Optional, Dict
from pydantic import BaseModel, Field
import os
import json
import argparse

class RealPaperWithReview (BaseModel): # paper review from real reviewers
    paper_pk: Optional[str] = Field(default=None) # primary key to decide after paper profile
    title: Optional[str] = Field(default=None)
    abstract: Optional[str] = Field(default=None)
    authors: Optional[List[str]] = Field(default=[])
    keywords: Optional[List[str]] = Field(default=None)
    # real reviews
    real_avg_scores: Optional[float] = Field(default=None)
    real_all_scores: Optional[List[int]] = Field(default=[])
    real_contents: Optional[List[str]] = Field(default=[])
    real_rank: Optional[int] = Field(default=0)
    real_decision: Optional[str] = Field(default=None)
    # simulated reviews
    sim_avg_scores: Optional[float] = Field(default=None) # from the simulation
    sim_all_scores: Optional[List[int]] = Field(default=[])
    sim_contents: Optional[List[str]] = Field(default=[])
    sim_rank: Optional[int] = Field(default=0)
    sim_decision: Optional[str] = Field(default=None)

class RealPaperWithReviewDB:
    def __init__(self):
        self.data: Dict[str, RealPaperWithReview] = {}
        self.rank_consistency:float = 0.0
    
    def add(self, real_paper: RealPaperWithReview) -> None:
        self.data[real_paper.title] = real_paper

    def load_from_file(self, file_name: str) -> None:
        with open(file_name, 'r') as f:
            raw_data = json.load(f)
            self.data = {
                title: RealPaperWithReview(**details)
                for title, details in raw_data.items()
            }
    
    def save_to_file(self, file_name: str) -> None:
        # Combine data and rank_consistency into one dictionary
        combined_data = {
            "rank_consistency": self.rank_consistency,
            "papers": {title: real_paper.dict() for title, real_paper in self.data.items()}
            
        }
        
        with open(file_name, 'w') as f:
            json.dump(combined_data, f, indent=2)

    def profile_paper_from_real_review(self) -> List[PaperProfile]:
        papers = []
        for review in self.data.values():
            paper = PaperProfile(
                title = review.title,
                abstract = review.abstract,
                authors = review.authors,
                keywords = review.keywords
            )
            review.paper_pk = paper.pk # write back the pk to the review
            papers.append(paper)
        return papers

    def map_agent_reviews_to_real_paper(self, agent_reviews: List[AgentPaperReviewLog]) -> None:
        for agent_review in agent_reviews:
            for real_paper in self.data.values():
                if agent_review.paper_pk == real_paper.paper_pk:
                    real_paper.sim_all_scores.append(agent_review.review_score)
                    real_paper.sim_contents.append(agent_review.review_content)
        # calculate the average score
        for real_paper in self.data.values():
            real_paper.sim_avg_scores = sum(real_paper.sim_all_scores) / len(real_paper.sim_all_scores)
        # calculate the real review rank
        real_papers = list(self.data.values())
        real_papers.sort(key=lambda x: x.real_avg_scores, reverse=True)
        for i, real_paper in enumerate(real_papers):
            real_paper.real_rank = i + 1
        # calculate the simulated review rank
        real_papers.sort(key=lambda x: x.sim_avg_scores, reverse=True)
        for i, real_paper in enumerate(real_papers):
            real_paper.sim_rank = i + 1
        
    def rank_consistency(self) -> float:
        # calculate the rank consistency
        rank_consistency_float = 0
        for real_paper in self.data.values():
            rank_consistency_float += abs(real_paper.real_rank - real_paper.sim_rank)
        rank_consistency_float = rank_consistency_float / len(self.data)
        # store the rank consistency
        self.rank_consistency = rank_consistency_float
        return rank_consistency_float
 





def main(data_path: str, domain:str) -> None:
    print(f"Data path is: {data_path}")
    print(f"Domain is: {domain}")
    # collect papers from openreview
    real_paper_db = RealPaperWithReviewDB()
    paper_file = os.path.join(data_path, f"paper_{domain}.json")
    real_paper_db.load_from_file(paper_file)
    Papers2eval = real_paper_db.profile_paper_from_real_review()
    # generate envs of agents with reviewers
    # 1. how to select reviewers? Retrive the reviewers from the database.
    agent_db = AgentProfileDB()
    agent_db.load_from_file(data_path+"agent_"+ domain + ".json")
    # 2. how to assign reviewers to papers?
    # (jinwei) Hardcode-- select top 3 reviewers in the agent_db to agent_profiles
    agent_profiles: List[AgentProfile] = []
    all_reviewers = agent_db.data.values()
    for i in range(3):
        agent_profiles.append(all_reviewers[i])
    # create agents
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
    real_paper_db.map_agent_reviews_to_real_paper(reviews)
    rank_consistency = real_paper_db.rank_consistency()
    # print rank consistency
    print(f"rank_consistency = {rank_consistency}\n")
    # save the RealPaperWithReviewDB
    # Construct the output file path
    output_file = os.path.join(data_path, f"output_microbench_review_{domain}.json")
    real_paper_db.save_to_file(output_file)
    


if __name__ == '__main__':
    # Get the directory of the current script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Construct the path to data/microbench
    default_data_path = os.path.join(current_dir, '..', 'data', 'microbench')

    parser = argparse.ArgumentParser(description="Process folder path of microbench.")
    parser.add_argument(
        "--data_path", 
        type=str, 
        default=default_data_path, 
        help="Path to the data directory for microbenchmark."
    )
    # Add argument for domain
    parser.add_argument(
        "--domain", 
        type=str, 
        default="machine_learning_system", 
        help="Domain of papers to be reviewed."
    )
    
    args = parser.parse_args()
    main(args.data_path, args.domain)