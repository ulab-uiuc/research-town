# parse the evaluation output of the pipeline evaluation and generate a csv file
import re
import os
import json
import pandas as pd

# Function to sanitize the model name
def sanitize_filename(filename: str) -> str:
    # Replace any character that is not a letter, digit, hyphen, or underscore with an underscore
    return re.sub(r'[^a-zA-Z0-9-_]', '_', filename)





def main():
    agent_model_options = ["llama3_70b", "mixtral_8_7b", "qwen_32", "llama3_8b",  "gpt_4o"]
    evaluator_model_options = ["together_ai/meta-llama/Llama-3-70b-chat-hf", "together_ai/mistralai/Mixtral-8x22B-Instruct-v0.1",  "gpt-4o"]
    domain_options = ["natural_language_processing", "computer_vision", "graph_neural_networks", "federated_learning", "reinforcement_learning"]
    eval_log_num = 10
    
    # Get the directory of the current script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.abspath(os.path.join(current_dir, '..', '..', 'data'))
    
    # Data containers for storing the results
    idea_data = {domain: [] for domain in domain_options}
    paper_data = {domain: [] for domain in domain_options}
    review_data = {domain: [] for domain in domain_options}
    
    # Load the pipeline evaluation output for each domain with each agent model and evaluator model
    for domain in domain_options:
        for agent_model_name in agent_model_options:
            for evaluator_model_name in evaluator_model_options:
                sanitized_model_name = sanitize_filename(evaluator_model_name)
                raw_output_file = os.path.join(
                    data_path,
                    'eval_data',
                    'pipeline_eval_data',
                    f'{agent_model_name}',
                    'output',
                    f'output_pipeline_eval_{domain}_agent-model-{agent_model_name}_p{eval_log_num}_eval_by_{sanitized_model_name}.json',
                )
                # Load by json and collect the required data
                try:
                    # Load by json and collect the required data
                    with open(raw_output_file, 'r') as f:
                        raw_data = json.load(f)
                        idea_data[domain].append({
                            "domain": domain,
                            "agent_model_name": agent_model_name,
                            "evaluator_model_name": evaluator_model_name,
                            "idea_avg_overall_score": raw_data["idea_avg_overall_score"],
                            "idea_variance_overall_score": raw_data["idea_variance_overall_score"],
                            "idea_sum_variance_dimension_scores": raw_data["idea_sum_variance_dimension_scores"]
                        })
                        paper_data[domain].append({
                            "domain": domain,
                            "agent_model_name": agent_model_name,
                            "evaluator_model_name": evaluator_model_name,
                            "paper_avg_overall_score": raw_data["paper_avg_overall_score"],
                            "paper_variance_overall_score": raw_data["paper_variance_overall_score"],
                            "paper_sum_variance_dimension_scores": raw_data["paper_sum_variance_dimension_scores"]
                        })
                        review_data[domain].append({
                            "domain": domain,
                            "agent_model_name": agent_model_name,
                            "evaluator_model_name": evaluator_model_name,
                            "review_avg_overall_score": raw_data["review_avg_overall_score"],
                            "review_variance_overall_score": raw_data["review_variance_overall_score"],
                            "review_sum_variance_dimension_scores": raw_data["review_sum_variance_dimension_scores"]
                        })
                except FileNotFoundError:
                    print(f"File not found: {raw_output_file}")
                    continue
        # For each domain, save the results of idea, paper, review to a csv file respectively
        parsed_idea_file_name = f'{domain}_idea.csv'
        parsed_paper_file_name = f'{domain}_paper.csv'
        parsed_review_file_name = f'{domain}_review.csv'
        
        parsed_idea_file_path = os.path.join(data_path, 'eval_data', 'pipeline_eval_data', 'parsed_output', parsed_idea_file_name)
        parsed_paper_file_path = os.path.join(data_path, 'eval_data', 'pipeline_eval_data', 'parsed_output', parsed_paper_file_name)
        parsed_review_file_path = os.path.join(data_path, 'eval_data', 'pipeline_eval_data', 'parsed_output', parsed_review_file_name)
        
        # Convert data to DataFrame and save as CSV
        pd.DataFrame(idea_data[domain]).to_csv(parsed_idea_file_path, index=False)
        pd.DataFrame(paper_data[domain]).to_csv(parsed_paper_file_path, index=False)
        pd.DataFrame(review_data[domain]).to_csv(parsed_review_file_path, index=False)
        




if __name__ == '__main__':
    main()