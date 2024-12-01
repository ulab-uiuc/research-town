import json

with open('./mlbench/mlbench_full.json', 'r') as f:
    mlbench_full = json.load(f)

import pdb; pdb.set_trace()

links = []
for key, value in mlbench_full.items():
    links.append(value['paper_data']['url'])

with open('./mlbench/links.txt', 'w') as f:
    for link in links:
        f.write(f'{link}\n')