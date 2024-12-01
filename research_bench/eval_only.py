import json
import numpy as np
from scipy.stats import ttest_rel, wilcoxon
from tqdm import tqdm
import matplotlib.pyplot as plt


def load_metrics(file_path, limit=None):
    """
    Load metrics from a JSONL file, with an optional limit on the number of datapoints.
    """
    metrics = {
        'openai_sim': [],
        'voyageai_sim': [],
        'openai_sim_q1': [],
        'openai_sim_q2': [],
        'openai_sim_q3': [],
        'openai_sim_q4': [],
        'openai_sim_q5': [],
        'voyageai_sim_q1': [],
        'voyageai_sim_q2': [],
        'voyageai_sim_q3': [],
        'voyageai_sim_q4': [],
        'voyageai_sim_q5': [],
    }

    with open('./mlbench/mlbench_full_filtered.json', 'r') as f:
        mlbench_full_filtered = json.load(f)
        ids = list(mlbench_full_filtered.keys())

    with open(file_path, 'r') as f:
        for line_num, line in enumerate(f, 1):
            if limit and line_num > limit:
                break
            try:
                obj = json.loads(line)
                if obj['paper_id'] not in ids:
                    continue
                for key in metrics.keys():
                    metrics[key].append(obj[key])
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON on line {line_num}: {e}")
                continue
    return metrics

def compute_weighted_metric(metrics):
    """
    Compute the weighted metrics for OpenAI and VoyageAI.
    """
    openai_metric = (
        0.2 * np.mean(metrics['openai_sim_q1']) +
        0.2 * np.mean(metrics['openai_sim_q2']) +
        0.2 * np.mean(metrics['openai_sim_q3']) +
        0.2 * np.mean(metrics['openai_sim_q4']) +
        0.2 * np.mean(metrics['openai_sim_q5'])
    )
    voyageai_metric = (
        0.2 * np.mean(metrics['voyageai_sim_q1']) +
        0.2 * np.mean(metrics['voyageai_sim_q2']) +
        0.2 * np.mean(metrics['voyageai_sim_q3']) +
        0.2 * np.mean(metrics['voyageai_sim_q4']) +
        0.2 * np.mean(metrics['voyageai_sim_q5'])
    )

    openai_metrics = [
        0.2 * metrics['openai_sim_q1'][i] +
        0.2 * metrics['openai_sim_q2'][i] +
        0.2 * metrics['openai_sim_q3'][i] +
        0.2 * metrics['openai_sim_q4'][i] +
        0.2 * metrics['openai_sim_q5'][i]
        for i in range(len(metrics['openai_sim_q1']))
    ]
    voyageai_metrics = [
        0.2 * metrics['voyageai_sim_q1'][i] +
        0.2 * metrics['voyageai_sim_q2'][i] +
        0.2 * metrics['voyageai_sim_q3'][i] +
        0.2 * metrics['voyageai_sim_q4'][i] +
        0.2 * metrics['voyageai_sim_q5'][i]
        for i in range(len(metrics['voyageai_sim_q1']))
    ]

    return openai_metric, voyageai_metric, openai_metrics, voyageai_metrics

def perform_statistical_tests(metrics1, metrics2):
    """
    Perform statistical tests on the metrics.
    """
    # Perform paired t-test
    t_stat, p_value = ttest_rel(metrics1, metrics2)
    print(f"Paired t-test: t-statistic = {t_stat}, p-value = {p_value}")


def plot_sorted_metrics(metric1, metric2):
    """
    Plot sorted metrics for comparison.
    """
    # Sort by metric1
    sorted_indices = np.argsort(metric2)
    sorted_metric1 = np.array(metric1)[sorted_indices]
    sorted_metric2 = np.array(metric2)[sorted_indices]

    # Plot
    plt.figure(figsize=(12, 6))
    plt.plot(sorted_metric1, label='File 1 - OpenAI Sim (Sorted)', marker='o', linestyle='-')
    plt.plot(sorted_metric2, label='File 2 - OpenAI Sim (Sorted by File 1)', marker='x', linestyle='--')
    plt.title('Comparison of OpenAI Similarity Scores Sorted by Metric 1')
    plt.xlabel('Data Point Index (Sorted by Metric 1)')
    plt.ylabel('Similarity Score')
    plt.legend()
    plt.grid(True)
    plt.show()


if __name__ == "__main__":
    # File paths for the two JSONL files
    #file1_path = './results/mlbench_result_4o_mini_fake_research_town_full_author.jsonl'
    #file2_path = './results/mlbench_result_4o_mini_citation_only.jsonl'

    #file1_path = './results/mlbench_use_all_citations_result_4o_mini_fake_research_town.jsonl'
    #file2_path = './results/mlbench_use_all_citations_result_4o_mini_citation_only.jsonl'

    file1_path = './results/mlbench_use_only_related_work_result_4o_mini_fake_research_town.jsonl'
    file2_path = './results/mlbench_use_only_related_work_result_4o_mini_citation_only.jsonl'

    #file1_path = './results/crossbench_result_4o_mini_fake_research_town_first_and_last_author.jsonl'
    #file2_path = './results/crossbench_result_4o_mini_citation_only.jsonl'

    #file1_path = './results/mlbench_result_4o_mini_citation_only.jsonl'
    #file2_path = './results/mlbench_use_only_related_work_result_4o_mini_citation_only.jsonl'

    #file1_path = './results/mlbench_full_filtered_use_all_citations_result_4o_mini_fake_research_town.jsonl'
    #file2_path = './results/mlbench_full_filtered_use_all_citations_result_4o_mini_citation_only.jsonl'

    # Determine the size of each dataset
    print("Loading file 1 to determine size...")
    with open(file1_path, 'r') as f1:
        size_file1 = sum(1 for _ in f1)
    print(f"File 1 contains {size_file1} datapoints.")

    print("Loading file 2 to determine size...")
    with open(file2_path, 'r') as f2:
        size_file2 = sum(1 for _ in f2)
    print(f"File 2 contains {size_file2} datapoints.")

    # Limit the number of datapoints to the size of the smaller dataset
    limit = min(size_file1, size_file2)
    print(f"Limiting both datasets to {limit} datapoints.")

    # Load metrics with the limit
    print("Loading metrics from file 1...")
    metrics_file1 = load_metrics(file1_path, limit=limit)

    print("Loading metrics from file 2...")
    metrics_file2 = load_metrics(file2_path, limit=limit)

    #metrics_file2['openai_sim_q1'] = [metrics_file2['openai_sim_q1'][i] - 2 for i in range(len(metrics_file2['openai_sim_q1']))]
    # Plot metrics
    print("Plotting metrics...")
    plot_sorted_metrics(metrics_file1['openai_sim_q5'], metrics_file2['openai_sim_q5'])

    for i in range(1, 6):
        print(f"Question {i}:")
        print(np.mean(metrics_file1[f'openai_sim_q{i}']))
        print(np.mean(metrics_file2[f'openai_sim_q{i}']))

    # Compute weighted metrics
    print("Computing weighted metrics...")
    metric1_openai, metric1_voyageai, metrics1_openai, metrics1_voyageai = compute_weighted_metric(metrics_file1)
    metric2_openai, metric2_voyageai, metrics2_openai, metrics2_voyageai = compute_weighted_metric(metrics_file2)

    print(f"File 1 - OpenAI metric: {metric1_openai}, VoyageAI metric: {metric1_voyageai}")
    print(f"File 2 - OpenAI metric: {metric2_openai}, VoyageAI metric: {metric2_voyageai}")

    # Perform statistical tests
    print("Performing statistical tests...")
    perform_statistical_tests(metrics1_openai, metrics2_openai)
    perform_statistical_tests(metrics1_voyageai, metrics2_voyageai)
