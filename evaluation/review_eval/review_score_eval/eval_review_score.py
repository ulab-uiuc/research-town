import argparse
import json
import os
import uuid
import re
from beartype.typing import Dict, List, Optional
from pydantic import BaseModel, Field, validator
from scipy.stats import kendalltau, spearmanr
from tqdm import tqdm

from research_town.agents.agent_base import BaseResearchAgent
from research_town.configs import Config
from research_town.dbs.agent_db import AgentProfile, AgentProfileDB
from research_town.dbs.env_db import AgentPaperReviewLog
from research_town.dbs.paper_db import PaperProfile
# Function to sanitize the model name
def sanitize_filename(filename: str) -> str:
    # Replace any character that is not a letter, digit, hyphen, or underscore with an underscore
    return re.sub(r'[^a-zA-Z0-9-_]', '_', filename)

class RealPaperWithReview(BaseModel):  # paper review from real reviewers
    paper_pk: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str = Field(default='')
    abstract: Optional[str] = Field(default=None)
    authors: Optional[List[str]] = Field(default=[])
    keywords: Optional[List[str]] = Field(default=None)

    real_avg_scores: float = Field(default=-1)
    real_all_scores: List[int] = Field(default=[])
    
    real_confidences: List[int] = Field(default=[])
    real_contents: List[str] = Field(default=[])
    real_rank: int = Field(default=0)
    real_decision: str = Field(default='None')

    sim_avg_scores: float = Field(default=-1)  # from the simulation
    sim_all_scores: List[int] = Field(default=[])
    
    sim_contents: List[str] = Field(default=[])
    sim_rank: int = Field(default=-1)
    sim_decision: str = Field(default='None')

    @validator('paper_pk', pre=True, always=True)
    def set_paper_pk(cls, v)->str:
        return v or str(uuid.uuid4())


class RealPaperWithReviewDB(object):
    def __init__(self) -> None:
        self.data: Dict[str, RealPaperWithReview] = {}
        self.selected_papers: Dict[
            str, RealPaperWithReview
        ] = {}  # save the papers to be reviewed
        self.sim_ranks: List[int] = []
        self.real_ranks: List[int] = []
        self.absolute_rank_consistency: float = 0.0
        self.spearman_rank_consistency: float = 0.0
        self.kendall_rank_consistency: float = 0.0
        self.real_avg_score_variance:float = 0.0
        self.sim_avg_score_variance:float = 0.0
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
            'kendall_rank_consistency': self.kendall_rank_consistency,
            'sim_ranks': self.sim_ranks,
            'real_ranks': self.real_ranks,
            'sim_avg_score_variance': self.sim_avg_score_variance,
            'real_avg_score_variance': self.real_avg_score_variance,
            'papers': {
                title: real_paper.dict()
                for title, real_paper in self.selected_papers.items()
            },
        }

        with open(file_name, 'w') as f:
            json.dump(combined_data, f, indent=2)

    def profile_paper_from_real_review(self, paper_num: int) -> List[PaperProfile]:
        papers = []
        count = 0
        for review in self.data.values():
            if count >= paper_num:
                break
            paper = PaperProfile(
                title=review.title,
                abstract=review.abstract,
                authors=review.authors,
                keywords=review.keywords,
            )
            assert paper.pk is not None
            review.paper_pk = paper.pk  # write back the pk to the review
            papers.append(paper)
            count += 1
            self.selected_papers[review.title] = review  # save the selected papers
        return papers

    def map_agent_reviews_to_real_paper(
        self, agent_reviews: List[AgentPaperReviewLog]
    ) -> None:
        for agent_review in agent_reviews:
            for real_paper in self.selected_papers.values():
                if agent_review.paper_pk == real_paper.paper_pk:
                    if agent_review.review_score is not None:
                        real_paper.sim_all_scores.append(agent_review.review_score)
                    if agent_review.review_content is not None:
                        real_paper.sim_contents.append(agent_review.review_content)

        for real_paper in self.selected_papers.values():
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
        # calculate the variance of the average scores
        real_papers = list(self.selected_papers.values())
        self.real_avg_score_variance = sum([(real_paper.real_avg_scores - sum([paper.real_avg_scores for paper in real_papers])/len(real_papers))**2 for real_paper in real_papers])/len(real_papers)
        self.sim_avg_score_variance = sum([(real_paper.sim_avg_scores - sum([paper.sim_avg_scores for paper in real_papers])/len(real_papers))**2 for real_paper in real_papers])/len(real_papers)

        # calculate the rank of the papers
        real_papers.sort(key=lambda x: x.sim_avg_scores, reverse=True)
        for i, real_paper in enumerate(real_papers):
            real_paper.sim_rank = i + 1

        real_papers = list(self.selected_papers.values())
        real_papers.sort(key=lambda x: x.real_avg_scores, reverse=True)
        for i, real_paper in enumerate(real_papers):
            real_paper.real_rank = i + 1



    def calculate_rank_consistency(self) -> None:
        rank_consistency_float = 0.0
        for real_paper in self.selected_papers.values():
            rank_consistency_float += abs(real_paper.real_rank - real_paper.sim_rank)
            self.sim_ranks.append(real_paper.sim_rank)
            self.real_ranks.append(real_paper.real_rank)
        rank_consistency_float = rank_consistency_float / len(self.selected_papers)

        self.absolute_rank_consistency = rank_consistency_float
        spearank_consistency, _ = spearmanr(self.real_ranks, self.sim_ranks)
        self.spearman_rank_consistency = spearank_consistency
        kendall_rank_consistency, _ = kendalltau(self.real_ranks, self.sim_ranks)
        self.kendall_rank_consistency = kendall_rank_consistency


def main(
    data_path: str,
    domain: str,
    model_name: str,
    review_agent_num: int,
    review_paper_num: int,
) -> None:
    print(f'Data path is: {data_path}')
    print(f'Domain is: {domain}')
    # collect papers from openreview
    real_paper_db = RealPaperWithReviewDB()
    paper_file = os.path.join(
        data_path,
        'eval_data',
        'review_eval_data',
        'review_score_eval_data',
        f'paper_{domain}.json',
    )
    real_paper_db.load_from_file(paper_file)
    Papers2eval = real_paper_db.profile_paper_from_real_review(
        paper_num=review_paper_num
    )

    # Step1: generate envs of agents with reviewers
    agent_db = AgentProfileDB()
    agent_file = os.path.join(data_path, 'agent_data', f'{domain}.json')
    agent_db.load_from_file(agent_file)
    # Step2: start simulated review process for each paper. Total number of to papers to review is 'review_paper_num'.
    reviews: List[AgentPaperReviewLog] = []
    agent_profiles_list: List[AgentProfile] = list(agent_db.data.values())
    eval_config = Config()
    for idx, paper in enumerate(
        tqdm(Papers2eval, desc='Review Papers by Agents', unit='paper')
    ):
        if idx >= review_paper_num:
            break
        # 1. select reviewers. Retrive the reviewers from the database.
        selected_review_pks = agent_db.match(
            idea=paper.abstract,
            agent_profiles=agent_profiles_list,
            num=review_agent_num,
        )
        select_reviewers = [agent_db.data[pk] for pk in selected_review_pks]
        # 2. create the review agents
        review_agents: List[BaseResearchAgent] = []
        for agent_profile in select_reviewers:
            review_agents.append(
                BaseResearchAgent(
                    agent_profile=agent_profile,
                    model_name=model_name,
                )
            )
        # 3. review the paper
        for agent in review_agents:
            reviews.append(agent.write_paper_review(paper=paper, config=eval_config))

    # Step 3: get ranking consistency
    real_paper_db.map_agent_reviews_to_real_paper(reviews)
    real_paper_db.calculate_rank_consistency()
    # print real and sim ranks
    print(f'real_ranks = {real_paper_db.real_ranks}\n')
    print(f'sim_ranks = {real_paper_db.sim_ranks}\n')
    # print rank consistency
    print(f'absoulte_rank_consistency = {real_paper_db.absolute_rank_consistency}\n')
    print(f'spearman_rank_consistency = {real_paper_db.spearman_rank_consistency}\n')
    print(f'kendall_rank_consistency = {real_paper_db.kendall_rank_consistency}\n')

    # Step 4: save the RealPaperWithReviewDB
    sanitized_modelname=sanitize_filename(model_name)
    # Construct the output file path
    output_file = os.path.join(
        data_path,
        'eval_data',
        'review_eval_data',
        'review_score_eval_data',
        'output',
        f'output_review_eval_score_{domain}_p{review_paper_num}_r{review_agent_num}_by_{sanitized_modelname}.json',
    )
    real_paper_db.save_to_file(output_file)


if __name__ == '__main__':
    # Get the directory of the current script
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Construct the path to data/ directory
    default_data_path = os.path.abspath(
        os.path.join(current_dir, '..', '..', '..', 'data')
    )

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
        default='graph_neural_networks',
        help='Domain of papers to be reviewed.',
    )

    # Add argument for models
    parser.add_argument(
        '--model_name',
        type=str,
        default='together_ai/mistralai/Mixtral-8x7B-Instruct-v0.1',
        help='Models for reviewers.',
    )

    # Add argument for review_agent_num for each paper
    parser.add_argument(
        '--review_agent_num',
        type=int,
        default=3,
        help='Number of reviewers for each paper.',
    )

    # Add argument for papers to review
    parser.add_argument(
        '--review_paper_num',
        type=int,
        default=10,
        help='Number of total papers to review.',
    )

    args = parser.parse_args()
    main(
        args.data_path,
        args.domain,
        args.model_name,
        args.review_agent_num,
        args.review_paper_num,
    )
