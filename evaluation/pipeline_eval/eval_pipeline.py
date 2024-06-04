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
from pydantic import BaseModel, Field, validator
# Function to sanitize the model name
def sanitize_filename(filename: str) -> str:
    # Replace any character that is not a letter, digit, hyphen, or underscore with an underscore
    return re.sub(r'[^a-zA-Z0-9-_]', '_', filename)

class PipelineEval(BaseModel):
    paper_pk: str = Field(default='0')
    title: str = Field(default='')
    idea: str = Field(default='')
    trend: str = Field(default='')
    abstract: str = Field(default='')
    authors: List[str] = Field(default=[])
    keywords: List[str] = Field(default=[])
    contents: List[str] = Field(default=[])
    decision: str = Field(default='None')
    overall_score: int = Field(default=-1)
    dimension_scores: List[int] = Field(default=[])
    class Config:
        extra = 'ignore'

class review_content_eval_db(object):
    def __init__(self) -> None:
        self.data: Dict[str, ReviewContentEval] = {}
        self.selected_paper_reviews: Dict[str, ReviewContentEval] = {}  # save the paper reviews to be evaluated
        self.avg_all_scores:float = 0.0
        self.avg_dimension_scores:List[float] = []


def run_sync_evaluation(
    insight_list: ResearchInsight,
    idea_list: ResearchIdea,
    paper_list: ResearchPaperSubmission,
    review_list: AgentPaperReviewLog,
    meta_review_list: AgentPaperMetaReviewLog,
    model_name: str = 'together_ai/mistralai/Mixtral-8x7B-Instruct-v0.1',
) -> None:
    # Serialize Logs
    insight_serialize = f'content: {insight_list.content}'
    idea_serialize = f'content: {idea_list.content}'
    paper_serialize = {
        'title': paper_list.title,
        'abstract': paper_list.abstract,
        'conference': paper_list.conference,
    }
    review_serialize = (
        f'score: {review_list.review_score}\ncontent: {review_list.review_content}'
    )
    meta_review_serialize = f'decision: {meta_review_list.decision}\nmeta review:{meta_review_list.meta_review}'
    # Create Evaluators
    idea_quality_evaluator = IdeaQualityEvaluator(model_name=model_name)
    paper_quality_evaluator = PaperQualityEvaluator(model_name=model_name)
    review_quality_evaluator = ReviewQualityEvaluator(model_name=model_name)
    # Generate Evaluation
    idea_quality = idea_quality_evaluator.eval(
        **{'idea': idea_serialize, 'trend': insight_serialize}
    )
    paper_quality = paper_quality_evaluator.eval(
        **{
            'idea': idea_serialize,
            'trend': insight_serialize,
            'paper': paper_serialize,
        }
    )
    review_quality = review_quality_evaluator.eval(
        **{
            'idea': idea_serialize,
            'trend': insight_serialize,
            'paper': paper_serialize,
            'review': review_serialize,
            'decision': meta_review_serialize,
        }
    )
    # Save Logs
    with open('examples/evaluate_log/idea_quality.json', 'w') as file:
        json.dump(idea_quality.dict(), file)
    with open('examples/evaluate_log/paper_quality.json', 'w') as file:
        json.dump(paper_quality.dict(), file)
    with open('examples/evaluate_log/review_quality.json', 'w') as file:
        json.dump(review_quality.dict(), file)


def main(data_path: str,
    domain: str,
    evaluator_model_name: str,
    agent_model_name: str,
    eval_log_num: int,) -> None:
    # log file to load
    log_file =  os.path.join(data_path, 'eval_data','pipeline_eval_data',f'{agent_model_name}',f'{domain}_{agent_model_name}_saved_data.json')
    run_sync_evaluation(
        insight_list=insight_A,
        idea_list=idea_A,
        paper_list=paper_submission_A,
        review_list=paper_review_A,
        meta_review_list=paper_meta_review_A,
    )


if __name__ == '__main__':
    # Get the directory of the current script
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Construct the path to data/ directory
    default_data_path = os.path.abspath(
        os.path.join(current_dir, '..', '..', '..', 'data')
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
        default='Mixtral-8x7B',
        choices=['LLaMA-3_70', 'Mixtral-8x7B','LLaMA-3_8','QWen_32'],  # Add more models as needed
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
