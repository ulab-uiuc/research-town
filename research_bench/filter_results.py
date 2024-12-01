import json

with open('./mlbench/mlbench_full.json', 'r') as f:
    mlbench_full = json.load(f)


filtered_data = {}
for key, value in mlbench_full.items():
    count = 0
    references = value['paper_data']['references']
    for ref in references:
        ref_sections = ref['reference_section']
        if not ref_sections:
            continue
        for section in ref_sections:
            if 'related work' in section.lower():
                count += 1
                break
    if count >= 5:
        filtered_data[key] = value
print(len(mlbench_full))
print(len(filtered_data))


with open('./mlbench/mlbench_full_filtered.json', 'w') as f:
    json.dump(filtered_data, f)