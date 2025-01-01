import json
import numpy as np
from scipy.stats import ttest_rel
import matplotlib.pyplot as plt

def convert_aligned_to_metrics(aligned_metrics):
    metrics = {
        'bleu': [], 
        'rouge_l': [],
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
        'nvscore_q1': [],
        'nvscore_q2': [],
        'nvscore_q3': [],
        'nvscore_q4': [],
        'nvscore_q5': [],
        'openai_sim_q1_per_agent_avg': [],
        'openai_sim_q2_per_agent_avg': [],
        'openai_sim_q3_per_agent_avg': [],
        'openai_sim_q4_per_agent_avg': [],
        'openai_sim_q5_per_agent_avg': [],
        'voyageai_sim_q1_per_agent_avg': [],
        'voyageai_sim_q2_per_agent_avg': [],
        'voyageai_sim_q3_per_agent_avg': [],
        'voyageai_sim_q4_per_agent_avg': [],
        'voyageai_sim_q5_per_agent_avg': [],
    }
    for metric in aligned_metrics:
        for key in metrics:
            if 'per_agent' not in key:
                metrics[key].append(metric[key])
            else:
                #ms = []
                #for m in metric[key.replace('_avg', '')]:
                #    if m is not None and m != 0:
                #        ms.append(m)
                #metrics[key].append(np.mean(ms))
                #metrics[key].append(min(metric[key.replace('_avg', '')]))
                metrics[key].append(0)
    return metrics

def get_shared_ids(file1_path, file2_path):
    with open(file1_path, 'r') as f1, open(file2_path, 'r') as f2:
        ids_file1 = {json.loads(line)['paper_id'] for line in f1}
        ids_file2 = {json.loads(line)['paper_id'] for line in f2}
    return ids_file1.intersection(ids_file2)

def load_metrics_shared_as_dict(file_path, shared_ids):
    metrics_dict = {}
    with open(file_path, 'r') as f:
        for line in f:
            obj = json.loads(line)
            if obj['paper_id'] in shared_ids:
                metrics_dict[obj['paper_id']] = obj
    return metrics_dict

def compute_weighted_metric(metrics):
    weights = [0.2] * 5
    openai_metric = np.dot(weights, [np.mean(metrics[f'openai_sim_q{i}']) for i in range(1, 6)])
    voyageai_metric = np.dot(weights, [np.mean(metrics[f'voyageai_sim_q{i}']) for i in range(1, 6)])
    nvscore_metric = np.dot(weights, [np.mean(metrics[f'nvscore_q{i}']) for i in range(1, 6)])
    bleu = np.dot(weights, [np.mean(metrics[f'bleu']) for i in range(1, 6)])
    rouge_l = np.dot(weights, [np.mean(metrics[f'rouge_l']) for i in range(1, 6)])
    return openai_metric, voyageai_metric, nvscore_metric, bleu, rouge_l

def plot_sorted_metrics(metric1, metric2):
    sorted_indices = np.argsort(metric2)
    plt.plot(np.array(metric1)[sorted_indices], label='Metric 1 (sorted by Metric 2)', marker='o')
    plt.plot(np.array(metric2)[sorted_indices], label='Metric 2 (sorted)', marker='x')
    plt.legend()
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    # Uncomment the desired file paths
    # file1_path = './results/mlbench_result_4o_mini_fake_research_town_full_author.jsonl'
    # file2_path = './results/mlbench_result_4o_mini_citation_only.jsonl'

    file1_path = './results/paper_bench_mid_500_result_4o_mini_author_only_with_nv_filtered.jsonl'
    file2_path = './results/paper_bench_mid_500_result_4o_mini_fake_research_town_with_nv_filtered.jsonl'

    #file1_path = './results/paper_bench_easy_500_result_4o_mini_citation_only_with_nv_filtered.jsonl'
    #file2_path = './results/paper_bench_easy_500_result_4o_mini_fake_research_town_with_nv_filtered.jsonl'

    #file1_path = './results/paper_bench_mid_500_result_4o_mini_fake_research_town.jsonl'
    #file2_path = './results/paper_bench_mid_500_result_4o_mini_citation_only.jsonl'

    #file1_path = './results/paper_bench_easy_500_result_4o_mini_fake_research_town.jsonl'
    #file2_path = './results/paper_bench_easy_500_result_4o_mini_citation_only.jsonl'

    # file1_path = './results/mlbench_use_all_citations_result_4o_mini_fake_research_town.jsonl'
    # file2_path = './results/mlbench_use_all_citations_result_4o_mini_citation_only.jsonl'

    # file1_path = './results/mlbench_use_only_related_work_result_4o_mini_fake_research_town.jsonl'
    # file2_path = './results/mlbench_use_only_related_work_result_4o_mini_citation_only.jsonl'

    # file1_path = './results/crossbench_result_4o_mini_fake_research_town_first_and_last_author.jsonl'
    # file2_path = './results/crossbench_result_4o_mini_citation_only.jsonl'

    # file1_path = './results/mlbench_result_4o_mini_citation_only.jsonl'
    # file2_path = './results/mlbench_use_only_related_work_result_4o_mini_citation_only.jsonl'

    # file1_path = './results/mlbench_full_filtered_use_all_citations_result_4o_mini_fake_research_town.jsonl'
    # file2_path = './results/mlbench_full_filtered_use_all_citations_result_4o_mini_citation_only.jsonl'

    # file1_path = './results/paper_bench_result_4o_mini_fake_research_town.jsonl'
    # file2_path = './results/paper_bench_result_4o_mini_citation_only_part1.jsonl'

    #file1_path = './results/cross_bench_1202_result_4o_mini_fake_research_town.jsonl'
    #file2_path = './results/cross_bench_1202_result_4o_mini_fake_research_town_twice.jsonl'

    #file1_path = './results/paper_bench_mid_500_result_4o_mini_fake_research_town.jsonl'
    #file2_path = './results/paper_bench_mid_500_result_4o_mini_fake_research_town_twice.jsonl'

    #file1_path = './results/paper_bench_hard_500_result_4o_mini_swarm_with_related_work.jsonl'
    #file2_path = './results/paper_bench_hard_500_result_4o_mini_swarm.jsonl'

    #file1_path = './results/oodbench_1203_filtered_result_4o_mini_fake_research_town.jsonl'
    #file2_path = './results/oodbench_1203_filtered_result_4o_mini_citation_only.jsonl'

    file1_path = './results/crossbench_1205_filtered_result_4o_mini_fake_research_town.jsonl'
    file2_path = './results/crossbench_1205_filtered_result_4o_mini_fake_research_town.jsonl'

    #file1_path ='./results/oodbench_1203_filtered_result_4o_mini_fake_research_town.jsonl'
    #file2_path = './results/oodbench_1203_filtered_result_4o_mini_fake_research_town.jsonl'

    #file1_path = './results/agent_number_ablation_paper_bench_author_1_result_4o_mini_fake_research_town.jsonl'
    #file2_path = './results/agent_number_ablation_paper_bench_author_5_result_4o_mini_fake_research_town.jsonl'

    #file1_path = './results/paper_number_ablation_paper_bench_all_references_result_4o_mini_fake_research_town.jsonl'
    #file2_path = './results/paper_number_ablation_paper_bench_introduction_only_result_4o_mini_fake_research_town.jsonl'

    file1_path = './results/paper_bench_hard_500_result_4o_mini_citation_only_with_nv_filtered.jsonl'
    file2_path = './results/agent_number_ablation_record_each_agent_output_paper_bench_last_author_result_4o_mini_fake_research_town.jsonl'

    file1_path = './results/agent_number_ablation_record_each_agent_output_paper_bench_without_bio_sample_3_result_4o_mini_fake_research_town.jsonl'
    file2_path = './results/agent_number_ablation_record_each_agent_output_paper_bench_without_bio_sample_1_result_4o_mini_fake_research_town.jsonl'

    file1_path = './results/agent_number_ablation_record_each_agent_output_paper_bench_author_5_result_4o_mini_fake_research_town_filtered.jsonl'
    file2_path = './results/agent_number_ablation_record_each_agent_output_paper_bench_author_1_result_4o_mini_fake_research_town_filtered.jsonl'

    file1_path = './results/agent_number_ablation_record_each_agent_output_paper_bench_with_bio_sample_1_result_4o_mini_fake_research_town.jsonl'
    file2_path = './results/agent_number_ablation_record_each_agent_output_paper_bench_with_bio_sample_5_result_4o_mini_fake_research_town.jsonl'

    file1_path = './results/paper_number_ablation_all_papers_result_4o_mini_citation_only.jsonl'
    file2_path = './results/paper_number_ablation_other_only_result_4o_mini_citation_only.jsonl'

    #file1_path = './results/agent_number_ablation_two_author_result_4o_mini_author_only.jsonl'
    #file2_path = './results/agent_number_ablation_five_author_result_4o_mini_author_only.jsonl'

    file1_path = './results/paper_bench_hard_500_result_4o_mini_zero_shot_resplit.jsonl'
    file2_path = './results/paper_bench_hard_500_result_4o_mini_author_only_resplit.jsonl'

    print("Finding shared paper_ids...")
    shared_ids = get_shared_ids(file1_path, file2_path)
    print(f"Number of shared paper_ids: {len(shared_ids)}")

    print("Loading metrics...")
    metrics_file1_dict = load_metrics_shared_as_dict(file1_path, shared_ids)
    metrics_file2_dict = load_metrics_shared_as_dict(file2_path, shared_ids)

    aligned_metrics_file1 = [metrics_file1_dict[pid] for pid in shared_ids]
    aligned_metrics_file2 = [metrics_file2_dict[pid] for pid in shared_ids]

    metrics_file1 = convert_aligned_to_metrics(aligned_metrics_file1)
    metrics_file2 = convert_aligned_to_metrics(aligned_metrics_file2)

    print("Computing weighted metrics...")
    metric1_openai, metric1_voyageai, metric1_nvscore, metric1_bleu, metric1_rougel = compute_weighted_metric(metrics_file1)
    metric2_openai, metric2_voyageai, metric2_nvscore, metric2_bleu, metric2_rougel = compute_weighted_metric(metrics_file2)

    print(f"File 1 - OpenAI metric: {metric1_openai}, VoyageAI metric: {metric1_voyageai}, NVScore metric: {metric1_nvscore}")
    print(f"File 2 - OpenAI metric: {metric2_openai}, VoyageAI metric: {metric2_voyageai}, NVScore metric: {metric2_nvscore}")
    print(f"File 1 - BLEU metric: {metric1_bleu}, ROUGE-L metric: {metric1_rougel}")
    print(f"File 2 - BLEU metric: {metric2_bleu}, ROUGE-L metric: {metric2_rougel}")

    print("Performing paired t-tests on openai...")
    t_stat, p_value = ttest_rel(
        [np.dot([0.2] * 5, [metrics_file1[f'openai_sim_q{i}'][j] for i in range(1, 6)]) for j in range(len(shared_ids))],
        [np.dot([0.2] * 5, [metrics_file2[f'openai_sim_q{i}'][j] for i in range(1, 6)]) for j in range(len(shared_ids))]
    )

    # print average of q1 to q5 separately
    for i in range(1, 6):
        t_stat, p_value = ttest_rel(
            [metrics_file1[f'openai_sim_q{i}'][j] for j in range(len(shared_ids))],
            [metrics_file2[f'openai_sim_q{i}'][j] for j in range(len(shared_ids))]
        )
        print(f"average score for q{i} in file1: {np.mean([metrics_file1[f'openai_sim_q{i}'][j] for j in range(len(shared_ids))])}")
        print(f"average score for q{i} in file2: {np.mean([metrics_file2[f'openai_sim_q{i}'][j] for j in range(len(shared_ids))])}")
        print(f"Paired t-test for q{i}: t-statistic = {t_stat}, p-value = {p_value}")

    # average score for average of q1 to q5
    print('====')
    print(f"average score for average of q1 to q5 in file1: {np.mean([np.dot([0.2] * 5, [metrics_file1[f'openai_sim_q{i}'][j] for i in range(1, 6)]) for j in range(len(shared_ids))])}")
    print(f"std score for average of q1 to q5 in file1: {np.std([np.dot([0.2] * 5, [metrics_file1[f'openai_sim_q{i}'][j] for i in range(1, 6)]) for j in range(len(shared_ids))])}")
    print('====')
    print(f"average score for average of q1 to q5 in file2: {np.mean([np.dot([0.2] * 5, [metrics_file2[f'openai_sim_q{i}'][j] for i in range(1, 6)]) for j in range(len(shared_ids))])}")
    print(f"std score for average of q1 to q5 in file2: {np.std([np.dot([0.2] * 5, [metrics_file2[f'openai_sim_q{i}'][j] for i in range(1, 6)]) for j in range(len(shared_ids))])}")
    print('====')

    for i in range(1, 6):
        print(f"average per agent score for q{i} in file1: {np.mean([metrics_file1[f'openai_sim_q{i}_per_agent_avg'][j] for j in range(len(shared_ids))])}")
        print(f"std per agent score for q{i} in file1: {np.std([metrics_file1[f'openai_sim_q{i}_per_agent_avg'][j] for j in range(len(shared_ids))])}")
        print(f"average per agent score for q{i} in file2: {np.mean([metrics_file2[f'openai_sim_q{i}_per_agent_avg'][j] for j in range(len(shared_ids))])}")
        print(f"std per agent score for q{i} in file2: {np.std([metrics_file2[f'openai_sim_q{i}_per_agent_avg'][j] for j in range(len(shared_ids))])}")


    print("Performing paired t-tests on voyageai...")
    t_stat, p_value = ttest_rel(
        [np.dot([0.2] * 5, [metrics_file1[f'voyageai_sim_q{i}'][j] for i in range(1, 6)]) for j in range(len(shared_ids))],
        [np.dot([0.2] * 5, [metrics_file2[f'voyageai_sim_q{i}'][j] for i in range(1, 6)]) for j in range(len(shared_ids))]
    )



    for i in range(1, 6):
        t_stat, p_value = ttest_rel(
            [metrics_file1[f'voyageai_sim_q{i}'][j] for j in range(len(shared_ids))],
            [metrics_file2[f'voyageai_sim_q{i}'][j] for j in range(len(shared_ids))]
        )
        print(f"average score for q{i} in file1: {np.mean([metrics_file1[f'voyageai_sim_q{i}'][j] for j in range(len(shared_ids))])}")
        print(f"average score for q{i} in file2: {np.mean([metrics_file2[f'voyageai_sim_q{i}'][j] for j in range(len(shared_ids))])}")
        print(f"Paired t-test for q{i}: t-statistic = {t_stat}, p-value = {p_value}")

    print("Performing paired t-tests on nvscore...")
    t_stat, p_value = ttest_rel(
        [np.dot([0.2] * 5, [metrics_file1[f'nvscore_q{i}'][j] for i in range(1, 6)]) for j in range(len(shared_ids))],
        [np.dot([0.2] * 5, [metrics_file2[f'nvscore_q{i}'][j] for i in range(1, 6)]) for j in range(len(shared_ids))]
    )

    for i in range(1, 6):
        t_stat, p_value = ttest_rel(
            [metrics_file1[f'nvscore_q{i}'][j] for j in range(len(shared_ids))],
            [metrics_file2[f'nvscore_q{i}'][j] for j in range(len(shared_ids))]
        )
        print(f"average score for q{i} in file1: {np.mean([metrics_file1[f'nvscore_q{i}'][j] for j in range(len(shared_ids))])}")
        print(f"average score for q{i} in file2: {np.mean([metrics_file2[f'nvscore_q{i}'][j] for j in range(len(shared_ids))])}")
        print(f"Paired t-test for q{i}: t-statistic = {t_stat}, p-value = {p_value}")

    for i in range(1, 6):
        print(f"average per agent score for q{i} in file1: {np.mean([metrics_file1[f'voyageai_sim_q{i}_per_agent_avg'][j] for j in range(len(shared_ids))])}")
        print(f"std per agent score for q{i} in file1: {np.std([metrics_file1[f'voyageai_sim_q{i}_per_agent_avg'][j] for j in range(len(shared_ids))])}")
        print(f"average per agent score for q{i} in file2: {np.mean([metrics_file2[f'voyageai_sim_q{i}_per_agent_avg'][j] for j in range(len(shared_ids))])}")
        print(f"std per agent score for q{i} in file2: {np.std([metrics_file2[f'voyageai_sim_q{i}_per_agent_avg'][j] for j in range(len(shared_ids))])}")


    plot_sorted_metrics(metrics_file1['openai_sim_q5'], metrics_file2['openai_sim_q5'])
