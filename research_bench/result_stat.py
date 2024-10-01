import json

def calculate_averages(file_paths):
    # Iterate through each file path in the list
    for file_path in file_paths:
        # Initialize variables to store the sum of the metrics and count of entries
        total_rouge_l = 0
        total_gpt_metric_score = 0
        total_bert_score = 0
        count = 0

        # Open and read the file
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                # Parse each line as a JSON object
                data = json.loads(line)
                
                # Accumulate the values of each metric
                total_rouge_l += data.get('rouge_l', 0)
                total_gpt_metric_score += data.get('gpt_metric_score', 0)
                total_bert_score += data.get('bert_score', 0)
                
                # Increment the count of entries
                count += 1

        # Calculate the averages
        if count > 0:
            avg_rouge_l = total_rouge_l / count
            avg_gpt_metric_score = total_gpt_metric_score / count
            avg_bert_score = total_bert_score / count
        else:
            avg_rouge_l = avg_gpt_metric_score = avg_bert_score = 0

        # Print the results
        print(f"File: {file_path}")
        print(f"Average ROUGE-L: {avg_rouge_l}")
        print(f"Average GPT Metric Score: {avg_gpt_metric_score}")
        print(f"Average BERT Score: {avg_bert_score}")
        print("-" * 40)

# Example usage
file_paths = ['./results/research_bench_result_normal.jsonl', './results/research_bench_result_single_agent.jsonl']
calculate_averages(file_paths)