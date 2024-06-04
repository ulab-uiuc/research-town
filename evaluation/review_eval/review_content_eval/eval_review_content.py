import argparse
import json
import os
import uuid
from pydantic import BaseModel, Field, validator
from beartype.typing import Dict, List, Optional
from research_town.dbs import AgentPaperMetaReviewLog  # Meta-Review
from research_town.dbs import AgentPaperReviewLog  # Review
from research_town.dbs import ResearchIdea  # Idea
from research_town.dbs import ResearchInsight  # Trend
from research_town.dbs import ResearchPaperSubmission  # Paper
from research_town.evaluators import ReviewQualityEvaluator,ReviewEvalOutput
from tqdm import tqdm
import re

# Function to sanitize the model name
def sanitize_filename(filename: str) -> str:
    # Replace any character that is not a letter, digit, hyphen, or underscore with an underscore
    return re.sub(r'[^a-zA-Z0-9-_]', '_', filename)

class ReviewContentEval(BaseModel):
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

    def load_from_file(self, file_name: str, paper_type:str) -> None:
        with open(file_name, 'r') as f:
            raw_data = json.load(f)
            
            if paper_type == 'openreview':
                raw_data_papers = raw_data['papers']  # hardcode for openreview
                for title, details in raw_data_papers.items():
                    details['contents'] = details.pop('sim_contents', [])  # set 'contents' key from 'sim_contents'
            else:
                raw_data_papers = raw_data
            
            self.data = {
                title: ReviewContentEval(**details)
                for title, details in raw_data_papers.items()
            }
    def select_paper_reviews(self, paperreview_num: int) -> List[ReviewContentEval]:
        paperreviews = []
        count = 0
        for paperreview in self.data.values():
            if count >= paperreview_num:
                break
            select = paperreview
            paperreviews.append(select)
            count += 1
            self.selected_paper_reviews[select.title] = select # save the selected paperreviews
        return paperreviews
    
    def calculate_avg_scores(self, evals: List[ReviewEvalOutput]) -> None:
        assert len(evals) > 0
        self.avg_all_scores = sum([eval.overall_score for eval in evals]) / len(evals)
        self.avg_dimension_scores = [
            sum([eval.dimension_scores[i] for eval in evals]) / len(evals)
            for i in range(len(evals[0].dimension_scores))
        ]

    
    def save_to_file(self, file_name: str) -> None:
        # append the evaluation results to the original data    
        combined_data = {
            'avg_overall_score': self.avg_all_scores,
            'avg_dimension_scores': self.avg_dimension_scores,
            'review content evaluations': {
                title: paper_review.dict()
                for title, paper_review in self.selected_paper_reviews.items()

            },
        }

        with open(file_name, 'w') as f:
            json.dump(combined_data, f, indent=2)
    
    def eval_research_content( 
        self,
        review: ReviewContentEval,
        model_name: str = 'together_ai/mistralai/Mixtral-8x7B-Instruct-v0.1',)->ReviewEvalOutput:

        # Create Evaluators
        review_quality_evaluator = ReviewQualityEvaluator(model_name=model_name)
        paper_serialize = {
            'title': review.title,
            'abstract': review.abstract,
        }
        assert len(review.contents)>0, f"Error: no reviews\n"
        review_quality = review_quality_evaluator.eval(
            **{
                'idea': review.idea,
                'trend': review.trend,
                'paper': paper_serialize,
                'review': review.contents,
                'decision': review.decision,
            }
        )
        # save the evaluation results to the review itself
        self.selected_paper_reviews[review.title].overall_score = review_quality.overall_score
        self.selected_paper_reviews[review.title].dimension_scores = review_quality.dimension_scores

        return review_quality

def main(
    data_path: str,
    domain: str,
    model_name: str,
    paper_type: str,
    review_paper_num: int,
) -> None:
    review_file = os.path.join(data_path, 'eval_data','review_eval_data', 'review_content_eval_data',f'{paper_type}',f'review_{domain}.json')
    review_content_eval = review_content_eval_db()
    review_content_eval.load_from_file(review_file, paper_type)

    # select paper reviews to be evaluated
    PaperReview2eval = review_content_eval.select_paper_reviews(review_paper_num)
    # start evaluation for 'review_paper_num' papers
    eval_quality:List[ReviewEvalOutput] = []
    for idx, paper_review in enumerate(
        tqdm(PaperReview2eval, desc='Evaluate Paper Reviews', unit='paper reviews')
    ):
        if idx >= review_paper_num:
            break
        eval = review_content_eval.eval_research_content(
            review=paper_review,
            model_name = model_name
        )
        eval_quality.append(eval)
    
    # calculate the average scores
    review_content_eval.calculate_avg_scores(eval_quality)
    # save the evaluation results
    # Sanitize the model name to avoid file path issues
    sanitized_model_name = sanitize_filename(model_name)
    output_file = os.path.join(
        data_path,
        'eval_data',
        'review_eval_data',
        'review_content_eval_data',
        f'{paper_type}',
        'output',
        f'output_review_eval_content_{domain}_p{review_paper_num}_by_{sanitized_model_name}.json',
    )
    review_content_eval.save_to_file(output_file)

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
        help='Domain of reviewed papers.',
    )

    # Add argument for models
    parser.add_argument(
        '--model_name',
        type=str,
        default='together_ai/mistralai/Mixtral-8x7B-Instruct-v0.1',
        help='Models for LLM evaluators.',
    )

    # Add agument for paper type
    parser.add_argument(
        '--paper_type',
        type=str,
        default='openreview', # 'openreview' or 'arxiv'
        help='Type of reviewed papers.',
    )
    # Add argument for papers to review
    parser.add_argument(
        '--review_paper_num',
        type=int,
        default=10,
        help='Number of total papers to evaluate.',
    )

    args = parser.parse_args()
    main(args.data_path, args.domain, args.model_name, args.paper_type, args.review_paper_num)