import argparse
import json
import os

from research_town.dbs import AgentPaperMetaReviewLog  # Meta-Review
from research_town.dbs import AgentPaperReviewLog  # Review
from research_town.dbs import ResearchIdea  # Idea
from research_town.dbs import ResearchInsight  # Trend
from research_town.dbs import ResearchPaperSubmission  # Paper
from research_town.evaluators import (
    IdeaQualityEvaluator,
    PaperQualityEvaluator,
    ReviewQualityEvaluator,
)

from beartype.typing import Dict, List, Optional
from tqdm import tqdm
import re
import uuid
from pydantic import BaseModel, Field, validator
# Function to sanitize the model name
def sanitize_filename(filename: str) -> str:
    # Replace any character that is not a letter, digit, hyphen, or underscore with an underscore
    return re.sub(r'[^a-zA-Z0-9-_]', '_', filename)

class PipelineEval(BaseModel):
    pipeline_pk:str = Field(default_factory=lambda: str(uuid.uuid4()))# use agent name as pipeline_pk
    title: str = Field(default='')
    idea: str = Field(default='')
    trend: str = Field(default='')
    abstract: str = Field(default='')
    authors: List[str] = Field(default=[])
    keywords: List[str] = Field(default=[])
    contents: List[str] = Field(default=[])
    decision: str = Field(default='None')

    idea_overall_score: int = Field(default=-1)
    idea_dimension_scores: List[int] = Field(default=[])
    paper_overall_score: int = Field(default=-1)
    paper_dimension_scores: List[int] = Field(default=[])
    review_overall_score: int = Field(default=-1)
    review_dimension_scores: List[int] = Field(default=[])
    class Config:
        extra = 'ignore'

class pipeline_eval_db(object):
    def __init__(self) -> None:
        self.data: Dict[str, PipelineEval] = {}
        self.selected_logs: Dict[str, PipelineEval] = {}  # save the logs to be evaluated
        self.idea_avg_all_scores:float = 0.0
        self.idea_avg_dimension_scores:List[float] = []
        self.paper_avg_all_scores:float = 0.0
        self.paper_avg_dimension_scores:List[float] = []
        self.review_avg_all_scores:float = 0.0
        self.review_avg_dimension_scores:List[float] = []

        # add varience of the scores
        self.idea_variance_all_scores:float = 0.0
        self.idea_variance_dimension_scores:List[float] = []
        self.idea_sum_variance_dimension_scores:float = 0.0
        self.paper_variance_all_scores:float = 0.0
        self.paper_variance_dimension_scores:List[float] = []
        self.paper_sum_variance_dimension_scores:float = 0.0
        self.review_variance_all_scores:float = 0.0
        self.review_variance_dimension_scores:List[float] = []
        self.review_sum_variance_dimension_scores:float = 0.0

    def load_from_file(self, file_name: str) -> None:
        with open(file_name, 'r') as f:
            raw_data_papers = json.load(f)
            for agent, details in raw_data_papers.items():
                reviews = details.pop('reviews', [])
                if not isinstance(reviews, list):
                    reviews = [reviews] 
                details['abstract'] = details.pop('paper', '') 
                details['contents'] = reviews  # set 'contents' key from 'reviews'
                details['decision'] = details.pop('meta_reviews', 'None')  # set 'decision' key from 'meta_reviews'
                pipeline_eval = PipelineEval(**details)
                self.data[pipeline_eval.pipeline_pk] = pipeline_eval 

    def select_logs(self, log_num: int) -> List[PipelineEval]:
        logs = []
        count = 0
        for log in self.data.values():
            if count >= log_num:
                break
            select = log
            logs.append(select)
            count += 1
            self.selected_logs[select.pipeline_pk] = select # save the selected paperreviews
        return logs 
    
    def eval_research_pipeline( 
        self,
        research_log: PipelineEval,
        model_name: str = 'together_ai/mistralai/Mixtral-8x7B-Instruct-v0.1',)->None:

        # Create Evaluators
        idea_quality_evaluator = IdeaQualityEvaluator(model_name=model_name)
        paper_quality_evaluator = PaperQualityEvaluator(model_name=model_name)
        review_quality_evaluator = ReviewQualityEvaluator(model_name=model_name)
        # Generate Evaluation

        # parse the paper content with title
        paper_serialize = {
            'title': 'See title in reviews',
            'abstract': research_log.abstract,
        }

        # error check
        assert research_log.idea != '', f"Error: no ideas\n"
        assert research_log.abstract != '', f"Error: no papers with abstract\n"
        assert len(research_log.contents)>0, f"Error: no reviews\n"

        idea_quality = idea_quality_evaluator.eval(
            **{'idea': research_log.idea, 'trend': ''}
        )
        paper_quality = paper_quality_evaluator.eval(
            **{
                'idea': research_log.idea,
                'trend': '',
                'paper': paper_serialize,
            }
        )
        review_quality = review_quality_evaluator.eval(
            **{
                'idea': research_log.idea,
                'trend': '',
                'paper': paper_serialize,
                'review': research_log.contents,
                'decision': research_log.decision,
            }
        )

        # save the evaluation results 
        # idea quality
        self.selected_logs[research_log.pipeline_pk].idea_overall_score = idea_quality.overall_score
        self.selected_logs[research_log.pipeline_pk].idea_dimension_scores = idea_quality.dimension_scores
        # paper quality
        self.selected_logs[research_log.pipeline_pk].paper_overall_score = paper_quality.overall_score
        self.selected_logs[research_log.pipeline_pk].paper_dimension_scores = paper_quality.dimension_scores
        # review quality
        self.selected_logs[research_log.pipeline_pk].review_overall_score = review_quality.overall_score
        self.selected_logs[research_log.pipeline_pk].review_dimension_scores = review_quality.dimension_scores


    
    def save_to_file(self, file_name: str) -> None:
        # save the    
        combined_data = {
            'idea_avg_overall_score': self.idea_avg_all_scores,
            'idea_avg_dimension_scores': self.idea_avg_dimension_scores,
            'paper_avg_overall_score': self.paper_avg_all_scores,
            'paper_avg_dimension_scores': self.paper_avg_dimension_scores,
            'review_avg_overall_score': self.review_avg_all_scores,
            'review_avg_dimension_scores': self.review_avg_dimension_scores,
            'idea_variance_overall_score': self.idea_variance_all_scores,
            'idea_variance_dimension_scores': self.idea_variance_dimension_scores,
            # add sum of dimension score variance
            'idea_sum_variance_dimension_scores': self.idea_sum_variance_dimension_scores,
            'paper_variance_overall_score': self.paper_variance_all_scores,
            'paper_variance_dimension_scores': self.paper_variance_dimension_scores,
            # add sum of dimension score variance
            'paper_sum_variance_dimension_scores': self.paper_sum_variance_dimension_scores,
            'review_variance_overall_score': self.review_variance_all_scores,
            'review_variance_dimension_scores': self.review_variance_dimension_scores,
            # add sum of dimension score variance
            'review_sum_variance_dimension_scores': self.review_sum_variance_dimension_scores,
            'pipeline evaluation logs': {
                author: eval_log.dict()
                for author, eval_log in self.selected_logs.items()

            },
        }

        with open(file_name, 'w') as f:
            json.dump(combined_data, f, indent=2)

    def calculate_avg_scores(self)->None:
        # calculate the avg scores of selected logs
        assert len(self.selected_logs) > 0
        selected_logs_list = list(self.selected_logs.values())
        self.idea_avg_all_scores = sum([log.idea_overall_score for log in selected_logs_list]) / len(selected_logs_list)
        self.idea_avg_dimension_scores = [
            sum([log.idea_dimension_scores[i] for log in selected_logs_list]) / len(selected_logs_list)
            for i in range(len(selected_logs_list[0].idea_dimension_scores))
        ]
        self.paper_avg_all_scores = sum([log.paper_overall_score for log in selected_logs_list]) / len(selected_logs_list)
        self.paper_avg_dimension_scores = [
            sum([log.paper_dimension_scores[i] for log in selected_logs_list]) / len(selected_logs_list)
            for i in range(len(selected_logs_list[0].paper_dimension_scores))
        ]
        self.review_avg_all_scores = sum([log.review_overall_score for log in selected_logs_list]) / len(selected_logs_list)
        self.review_avg_dimension_scores = [
            sum([log.review_dimension_scores[i] for log in selected_logs_list]) / len(selected_logs_list)
            for i in range(len(selected_logs_list[0].review_dimension_scores))
        ]

    def calculate_variance_scores(self)->None:
        # calculate the variance scores of selected logs
        assert len(self.selected_logs) > 0
        selected_logs_list = list(self.selected_logs.values())
        self.idea_variance_all_scores = sum([(log.idea_overall_score - self.idea_avg_all_scores)**2 for log in selected_logs_list]) / len(selected_logs_list)
        self.idea_variance_dimension_scores = [
            sum([(log.idea_dimension_scores[i] - self.idea_avg_dimension_scores[i])**2 for log in selected_logs_list]) / len(selected_logs_list)
            for i in range(len(selected_logs_list[0].idea_dimension_scores))
        ]
        self.paper_variance_all_scores = sum([(log.paper_overall_score - self.paper_avg_all_scores)**2 for log in selected_logs_list]) / len(selected_logs_list)
        self.paper_variance_dimension_scores = [
            sum([(log.paper_dimension_scores[i] - self.paper_avg_dimension_scores[i])**2 for log in selected_logs_list]) / len(selected_logs_list)
            for i in range(len(selected_logs_list[0].paper_dimension_scores))
        ]
        self.review_variance_all_scores = sum([(log.review_overall_score - self.review_avg_all_scores)**2 for log in selected_logs_list]) / len(selected_logs_list)
        self.review_variance_dimension_scores = [
            sum([(log.review_dimension_scores[i] - self.review_avg_dimension_scores[i])**2 for log in selected_logs_list]) / len(selected_logs_list)
            for i in range(len(selected_logs_list[0].review_dimension_scores))
        ]
        # add sum of dimension score variance
        self.idea_sum_variance_dimension_scores = sum(self.idea_variance_dimension_scores)
        self.paper_sum_variance_dimension_scores = sum(self.paper_variance_dimension_scores)
        self.review_sum_variance_dimension_scores = sum(self.review_variance_dimension_scores)

def main(data_path: str,
    domain: str,
    evaluator_model_name: str,
    agent_model_name: str,
    eval_log_num: int,) -> None:
    # log file to load
    log_file =  os.path.join(data_path, 'eval_data','pipeline_eval_data',f'{agent_model_name}',f'{domain}.json')

    # select logs to be evaluated
    pipeline_eval = pipeline_eval_db()
    pipeline_eval.load_from_file(log_file)
    logs2eval = pipeline_eval.select_logs(eval_log_num)
    # start evaluation for the pipeline logs
   
    for idx, paper_review in enumerate(
        tqdm(logs2eval, desc='Evaluate pipeline logs', unit='pipeline logs of research town')):
        if idx >= eval_log_num:
            break
        pipeline_eval.eval_research_pipeline(
            research_log=paper_review,
            model_name = evaluator_model_name
        )
        

    # calculate the average scores
    pipeline_eval.calculate_avg_scores()
    # calculate the variance scores
    pipeline_eval.calculate_variance_scores()
    # save the evaluation results
    # Sanitize the model name to avoid file path issues
    sanitized_model_name = sanitize_filename(evaluator_model_name)
    output_file = os.path.join(
        data_path,
        'eval_data',
        'pipeline_eval_data',
        f'{agent_model_name}',
        'output',
        f'output_pipeline_eval_{domain}_agent-model-{agent_model_name}_p{eval_log_num}_eval_by_{sanitized_model_name}.json',
    )
    pipeline_eval.save_to_file(output_file)


if __name__ == '__main__':
    # Get the directory of the current script
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Construct the path to data/ directory
    default_data_path = os.path.abspath(
        os.path.join(current_dir,  '..', '..', 'data')
    )

    parser = argparse.ArgumentParser(description='Args for research content evaluation.')
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
        choices=['graph_neural_networks', 'computer_vision','natural_language_processing','reinforcement_learning','federated_learning'],  
        help='Domain of reviewed papers.',
    )

    # Add argument for models
    parser.add_argument(
        '--evaluator_model_name',
        type=str,
        default='together_ai/mistralai/Mixtral-8x7B-Instruct-v0.1',
        help='Models for LLM evaluators.',
    )

    # Add agument for paper type
    parser.add_argument(
        '--agent_model_name',
        type=str,
        default='mixtral_8_7b',
        choices=['llama3_70b', 'mixtral_8_7b','qwen_32','llama3_8b','gpt_4o'],  # Add more models as needed
        help='Model type of research agents to classify different logs.',
    )
    # Add argument for papers to review
    parser.add_argument(
        '--eval_log_num',
        type=int,
        default=10,
        help='Number of total papers to evaluate.',
    )
    args = parser.parse_args()
    main(args.data_path, args.domain, args.evaluator_model_name, args.agent_model_name, args.eval_log_num)
