import argparse
import json
import os
import uuid

from beartype.typing import Dict, List, Optional
from pydantic import BaseModel, Field
from tqdm import tqdm
from scipy.stats import spearmanr
from research_town.agents.agent_base import BaseResearchAgent
from research_town.dbs.agent_db import AgentProfile, AgentProfileDB
from research_town.dbs.env_db import AgentPaperReviewLog
from research_town.dbs.paper_db import PaperProfile


class RealPaperWithReview(BaseModel):  # paper review from real reviewers
    paper_pk: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str = Field(default='')
    abstract: Optional[str] = Field(default=None)
    authors: Optional[List[str]] = Field(default=[])
    keywords: Optional[List[str]] = Field(default=None)

    real_avg_scores: float = Field(default=-1)
    real_all_scores: List[int] = Field(default=[])
    real_contents: List[str] = Field(default=[])
    real_rank: int = Field(default=0)
    real_decision: str = Field(default='None')

    sim_avg_scores: float = Field(default=-1)  # from the simulation
    sim_all_scores: List[int] = Field(default=[])
    sim_contents: List[str] = Field(default=[])
    sim_rank: int = Field(default=-1)
    sim_decision: str = Field(default='None')


class RealPaperWithReviewDB(object):
    def __init__(self) -> None:
        self.data: Dict[str, RealPaperWithReview] = {}
        self.sim_ranks: List[int] = []
        self.real_ranks: List[int] = []
        self.absolute_rank_consistency: float = 0.0
        self.spearman_rank_consistency: float = 0.0

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
        combined_data = {
            'absolute_rank_consistency': self.absolute_rank_consistency,
            'spearman_rank_consistency': self.spearman_rank_consistency,
            'sim_ranks': self.sim_ranks,
            'real_ranks': self.real_ranks,
            'papers': {
                title: real_paper.dict() for title, real_paper in self.data.items()
            },
        }

        with open(file_name, 'w') as f:
            json.dump(combined_data, f, indent=2)

    def profile_paper_from_real_review(self) -> List[PaperProfile]:
        papers = []
        for review in self.data.values():
            paper = PaperProfile(
                title=review.title,
                abstract=review.abstract,
                authors=review.authors,
                keywords=review.keywords,
            )
            assert paper.pk is not None
            review.paper_pk = paper.pk  # write back the pk to the review
            papers.append(paper)
        return papers

    def map_agent_reviews_to_real_paper(
        self, agent_reviews: List[AgentPaperReviewLog]
    ) -> None:
        for agent_review in agent_reviews:
            for real_paper in self.data.values():
                if agent_review.paper_pk == real_paper.paper_pk:
                    if agent_review.review_score is not None:
                        real_paper.sim_all_scores.append(agent_review.review_score)
                    if agent_review.review_content is not None:
                        real_paper.sim_contents.append(agent_review.review_content)

        for real_paper in self.data.values():
            assert (
                len(real_paper.real_all_scores) > 0
            ), f'no real review score for paper {real_paper.paper_pk} with title of {real_paper.title}'
            real_paper.real_avg_scores = sum(real_paper.real_all_scores) / len(
                real_paper.real_all_scores
            )
            assert (
                len(real_paper.sim_all_scores) > 0
            ), f'no simulated review score for paper {real_paper.paper_pk} with title of {real_paper.title}'
            real_paper.sim_avg_scores = sum(real_paper.sim_all_scores) / len(
                real_paper.sim_all_scores
            )

        real_papers = list(self.data.values())
        real_papers.sort(key=lambda x: x.real_avg_scores, reverse=True)
        for i, real_paper in enumerate(real_papers):
            real_paper.real_rank = i + 1

        real_papers.sort(key=lambda x: x.sim_avg_scores, reverse=True)
        for i, real_paper in enumerate(real_papers):
            real_paper.sim_rank = i + 1

    def calculate_rank_consistency(self) -> None:
        rank_consistency_float = 0.0
        for real_paper in self.data.values():
            rank_consistency_float += abs(real_paper.real_rank - real_paper.sim_rank)
            self.sim_ranks.append(real_paper.sim_rank)
            self.real_ranks.append(real_paper.real_rank)
        rank_consistency_float = rank_consistency_float / len(self.data)

        self.absolute_rank_consistency = rank_consistency_float
        spearank_consistency, _ = spearmanr(self.real_ranks, self.sim_ranks)
        self.spearman_rank_consistency = spearank_consistency
        


def main(data_path: str, domain: str, model_name:str, review_agent_num: int) -> None:
    print(f'Data path is: {data_path}')
    print(f'Domain is: {domain}')
    # collect papers from openreview
    real_paper_db = RealPaperWithReviewDB()
    paper_file = os.path.join(data_path, f'paper_{domain}.json')
    real_paper_db.load_from_file(paper_file)
    Papers2eval = real_paper_db.profile_paper_from_real_review()
    # generate envs of agents with reviewers
    # 1. how to select reviewers? Retrive the reviewers from the database.
    agent_db = AgentProfileDB()
    agent_file = os.path.join(data_path, f'agent_{domain}.json')
    agent_db.load_from_file(agent_file)
    # 2. how to assign reviewers to papers?
    # Note: we hardcode and select top review_agent_num reviewers in the agent_db to agent_profiles
    agent_profiles: List[AgentProfile] = []
    all_reviewers = list(agent_db.data.values())  # Convert dict_values to a list

    for i in range(review_agent_num):
        agent_profiles.append(all_reviewers[i])
    # create agents
    agents: List[BaseResearchAgent] = []
    for agent_profile in agent_profiles:
        agents.append(
            BaseResearchAgent(
                agent_profile=agent_profile,
                model_name=model_name,
            )
        )

    # review papers
    # 3. how to get the scores of papers? Store to review log lists.
    reviews: List[AgentPaperReviewLog] = []
    # Outer loop (agents) with tqdm
    for agent in tqdm(agents, desc='Agents Review Progress'):
        # Inner loop (papers) with tqdm
        for paper in tqdm(Papers2eval, desc='Paper Review Progress'):
            reviews.append(agent.write_paper_review(paper=paper))

    # get ranking consistency
    real_paper_db.map_agent_reviews_to_real_paper(reviews)
    real_paper_db.calculate_rank_consistency()
    # print rank consistency
    print(f'absoulte_rank_consistency = {real_paper_db.absolute_rank_consistency}\n')
    print(f'spearman_rank_consistency = {real_paper_db.spearman_rank_consistency}\n')
    # save the RealPaperWithReviewDB
    # Construct the output file path
    output_file = os.path.join(data_path, f'output_microbench_review_{domain}_by_{model_name}.json')
    real_paper_db.save_to_file(output_file)


if __name__ == '__main__':
    # Get the directory of the current script
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Construct the path to data/microbench
    default_data_path = os.path.join(current_dir, '..', 'data', 'microbench')

    parser = argparse.ArgumentParser(description='Process folder path of microbench.')
    parser.add_argument(
        '--data_path',
        type=str,
        default=default_data_path,
        help='Path to the data directory for microbenchmark.',
    )
    # Add argument for domain
    parser.add_argument(
        '--domain',
        type=str,
        default='machine_learning_system',
        help='Domain of papers to be reviewed.',
    )

     # Add argument for models
    parser.add_argument(
        "--model_name", 
        type=str, 
        default='together_ai/mistralai/Mixtral-8x7B-Instruct-v0.1', 
        help="Models for reviewers."
    )

    # Add argument for review_agent_num
    parser.add_argument(
        "--review_agent_num", 
        type=int, 
        default=3, 
        help="Number of total reviewers."
    )

    args = parser.parse_args()
    main(args.data_path, args.domain, args.model_name, args.review_agent_num)
