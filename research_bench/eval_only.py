import jsonlines
from research_bench.eval import compute_proposal_metrics
from tqdm import tqdm
import json

dataset = []
with open('./results/mlbench_result_4o_mini_citation_only.jsonl', 'r') as f:
    for line_num, line in enumerate(f, 1):
        try:
            obj = json.loads(line)
            dataset.append(obj)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON on line {line_num}: {e}")
            continue

overall_metrics = {
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

dataset = dataset[:70]
for data in tqdm(dataset):
    ref_proposal = data['ref_proposal']
    gen_proposal = data['gen_proposal']
    if 'openai_sim' not in data.keys():
        print(data['paper_id'])
    #metrics = compute_proposal_metrics(ref_proposal, gen_proposal)
    #print(metrics)
    for key in overall_metrics.keys():
        overall_metrics[key].append(data[key])

for key, values in overall_metrics.items():
    print(f'{key}: {sum(values) / len(values)}')