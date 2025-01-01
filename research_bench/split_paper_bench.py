import json
import jsonlines
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import pearsonr
from collections import defaultdict
import random
random.seed(42)

def load_paper_bench(filepath):
    with open(filepath, 'r') as f:
        dataset = json.load(f)
    return dataset

def load_filtered_dataset(filepaths, paper_ids):
    dataset = []
    for file_path in filepaths:
        with jsonlines.open(file_path, 'r') as f:
            dataset.extend([obj for obj in f if obj['paper_id'] in paper_ids])
    return dataset

def calculate_openai_similarity(data):
    return (
        0.2 * data['openai_sim_q1'] +
        0.2 * data['openai_sim_q2'] +
        0.2 * data['openai_sim_q3'] +
        0.2 * data['openai_sim_q4'] +
        0.2 * data['openai_sim_q5']
    )

def add_openai_sim_to_dataset(dataset):
    for data in dataset:
        data['openai_sim_5q_avg'] = calculate_openai_similarity(data)

def sort_dataset_by_similarity(dataset):
    return sorted(dataset, key=lambda x: x['openai_sim_5q_avg'])

def analyze_categories(dataset, paper_bench_data):
    category_openai_sim_5q_avg = defaultdict(list)
    for data in dataset:
        paper_data = paper_bench_data[data['paper_id']]
        for category in paper_data['paper_data']['categories']:
            category_openai_sim_5q_avg[category].append(data['openai_sim_5q_avg'])
    return category_openai_sim_5q_avg

def calculate_category_stats(category_data):
    category_avg = {}
    category_num = {}
    for category, sim_values in category_data.items():
        category_avg[category] = np.mean(sim_values)
        category_num[category] = len(sim_values)
    return category_avg, category_num

def print_category_stats(category_avg, category_num, min_papers=10):
    sorted_categories = sorted(category_avg.items(), key=lambda x: x[1])
    for category, avg in sorted_categories:
        if category_num[category] > min_papers:
            print(f"{category}: {avg:.2f} ({category_num[category]} papers)")

def extract_ratings(dataset, paper_bench_data):
    checks = []
    for data in dataset:
        if 'reviews' in paper_bench_data[data['paper_id']]:
            reviews = paper_bench_data[data['paper_id']]['reviews']
            rating = sum(int(review['rating'].split(':')[0]) for review in reviews) / len(reviews)
            checks.append({
                'rating': rating,
                'paper_id': data['paper_id'],
                'openai_sim_5q_avg': data['openai_sim_5q_avg']
            })
    return checks

def calculate_correlation(ratings, similarities):
    return pearsonr(ratings, similarities)

def save_dataset(entries, paper_bench_data, output_path):
    saved_data = {entry['paper_id']: paper_bench_data[entry['paper_id']] for entry in entries}
    with open(output_path, 'w') as f:
        json.dump(saved_data, f, indent=4)
    print(f"Saved entries to {output_path}")

def main():
    paper_bench_file = './paper_bench/paper_bench_full.json'
    result_files = [
        './results/paper_bench_result_4o_mini_citation_only_part1.jsonl',
        './results/paper_bench_result_4o_mini_citation_only_part2.jsonl'
    ]
    paper_bench_full = load_paper_bench(paper_bench_file)



    paper_ids = list(paper_bench_full.keys())
    
    dataset = load_filtered_dataset(result_files, paper_ids)
    add_openai_sim_to_dataset(dataset)

    filtered_dataset = []
    for data in dataset:
        if data['paper_id'] in paper_ids:
            filtered_dataset.append(data)
            paper_ids.remove(data['paper_id'])
    
    filtered_dataset_sorted = sort_dataset_by_similarity(filtered_dataset)

    bottom_500 = filtered_dataset_sorted[:500]
    top_500 = filtered_dataset_sorted[-500:]
    mid_500 = random.sample(filtered_dataset_sorted[500:-500], 500)
    
    category_data = analyze_categories(filtered_dataset, paper_bench_full)
    category_avg, category_num = calculate_category_stats(category_data)
    print_category_stats(category_avg, category_num)
    
    checks = extract_ratings(filtered_dataset, paper_bench_full)
    ratings = [entry['rating'] for entry in checks]
    similarities = [entry['openai_sim_5q_avg'] for entry in checks]
    
    corr_coefficient, p_value = calculate_correlation(ratings, similarities)
    print(f"Pearson Correlation Coefficient: {corr_coefficient:.2f}")
    print(f"P-value: {p_value:.4f}")
    
    plt.figure(figsize=(8, 6))
    plt.scatter(similarities, ratings, alpha=0.7)
    plt.title('Correlation between Rating and OpenAI Similarity')
    plt.xlabel('OpenAI Similarity (5Q Avg)')
    plt.ylabel('Rating')
    plt.grid(True)
    plt.show()
    
    for key, data in paper_bench_full.items():
        if 'paper_data' not in data.keys():
            import pdb; pdb.set_trace()
    #save_dataset(bottom_500, paper_bench_full, './paper_bench/paper_bench_hard_500.json')
    #save_dataset(top_500, paper_bench_full, './paper_bench/paper_bench_easy_500.json')
    #save_dataset(mid_500, paper_bench_full, './paper_bench/paper_bench_mid_500.json')

if __name__ == "__main__":
    main()
