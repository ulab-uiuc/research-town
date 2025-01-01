import json

with open('./paper_bench/agent_number_ablation_paper_bench.json', 'r') as f:
    dataset = json.load(f)

for i in range(1, 6):

    with open(f'./results/agent_number_ablation_record_each_agent_output_paper_bench_author_{i}_result_4o_mini_fake_research_town.jsonl', 'r') as f:
        results = [json.loads(line) for line in f]

    filtered_results = [data for data in results if data['paper_id'] in dataset]

    with open(f'./results/agent_number_ablation_record_each_agent_output_paper_bench_author_{i}_result_4o_mini_fake_research_town_filtered.jsonl', 'w') as f:
        for result in filtered_results:
            json.dump(result, f)
            f.write('\n')