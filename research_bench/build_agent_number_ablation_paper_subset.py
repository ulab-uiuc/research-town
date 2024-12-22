import json

with open('./paper_bench/paper_bench_hard_500_filtered_1205.json', 'r') as f:
    dataset_hard = json.load(f)

with open('./paper_bench/paper_bench_mid_500_filtered_1205.json', 'r') as f:
    dataset_mid = json.load(f)

with open('./paper_bench/paper_bench_easy_500_filtered_1205.json', 'r') as f:
    dataset_easy = json.load(f)

dataset = {**dataset_hard}


agent_number_ablation_dataset = {}
for key, value in dataset.items():
    author_num = len(value['paper_data']['authors'])
    if author_num >= 5:
        agent_number_ablation_dataset[key] = value

print(len(agent_number_ablation_dataset))
with open('./paper_bench/agent_number_ablation_paper_bench.json', 'w') as f:
    json.dump(agent_number_ablation_dataset, f, indent=4)

'''
paper_number_ablation_dataset = {}
for key, value in dataset.items():
    reference = value['paper_data']['references'][0]
    if 'reference_section' in reference:
        references = value['paper_data']['references']
        section_names = []

        for ref in references:
            if 'reference_section' in ref.keys():
                if ref['reference_section'] is not None:
                    for section_name in ref['reference_section']:
                        section_names.append(section_name.lower())
            
        if 'related work' in section_names and 'introduction' in section_names:
            paper_number_ablation_dataset[key] = value

with open('./paper_bench/paper_number_ablation_paper_bench.json', 'w') as f:
    json.dump(paper_number_ablation_dataset, f, indent=4)
'''