import os
import json
import pandas as pd
from collections import defaultdict

def process_jsonl_file(file_path):
    scores = []
    template_scores = defaultdict(list)
    domain_scores = defaultdict(list)
    score_distribution = defaultdict(int)

    with open(file_path, 'r') as f:
        for line in f:
            item = json.loads(line)
            score = item.get("score", 0)
            template = item.get("template", "Unknown")
            domain = item.get("domain", "Unknown")

            # Collect scores
            scores.append(score)
            template_scores[template].append(score)
            domain_scores[domain].append(score)
            score_distribution[score] += 1

    # Calculate average scores
    print(scores)
    avg_score = sum(scores) / len(scores) if scores else 0
    avg_template_scores = {template: sum(scores) / len(scores) for template, scores in template_scores.items()}
    avg_domain_scores = {domain: sum(scores) / len(scores) for domain, scores in domain_scores.items()}

    # Score distribution (from 1 to 5)
    score_dist = {i: score_distribution.get(i, 0) for i in range(1, 6)}

    return avg_score, avg_template_scores, avg_domain_scores, score_dist

def process_folder(folder_path):
    results = []

    for filename in os.listdir(folder_path):
        if filename.endswith('.jsonl'):
            file_path = os.path.join(folder_path, filename)
            avg_score, avg_template_scores, avg_domain_scores, score_dist = process_jsonl_file(file_path)

            result = {
                'filename': filename,
                'avg_score': avg_score,
            }

            # Add template average scores
            for template, avg in avg_template_scores.items():
                result[f'template_avg_{template}'] = avg

            # Add domain average scores
            for domain, avg in avg_domain_scores.items():
                result[f'domain_avg_{domain}'] = avg

            # Add score distribution
            for score, count in score_dist.items():
                result[f'score_{score}_count'] = count

            results.append(result)

    # Convert results to DataFrame and save to CSV
    df = pd.DataFrame(results)
    df.to_csv('jsonl_analysis_results.csv', index=False)

if __name__ == "__main__":
    folder_path = '/home/kunlunz2/research-town/research_bench/attack_results_2'
    process_folder(folder_path)
    print("Analysis complete. Results saved to 'jsonl_analysis_results.csv'")
