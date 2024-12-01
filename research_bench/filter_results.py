import json

with open('./mlbench/mlbench_full.json', 'r') as f:
    mlbench_full = json.load(f)

with open('./iclrbench/iclrbench.json', 'r') as f:
    iclrbench_full = json.load(f)

filtered_data = {}
for key, value in mlbench_full.items():
    count = 0
    references = value['paper_data']['references']
    for ref in references:
        abstract = ref['abstract']
        if not abstract:
            continue
        count += 1
    if count >= 20:
        filtered_data[key] = value

for key, value in iclrbench_full.items():
    count = 0
    references = value['paper_data']['references']
    for ref in references:
        abstract = ref['abstract']
        if not abstract:
            continue
        count += 1
    if count >= 20:
        filtered_data[key] = value


print(len(mlbench_full))
print(len(iclrbench_full))
print(len(filtered_data))

import pdb; pdb.set_trace()


with open('./paper_bench/paper_bench_full.json', 'w') as f:
    json.dump(filtered_data, f)