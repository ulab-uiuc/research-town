import json

with open('./mlbench/mlbench_full.json', 'r') as f:
    mlbench_full = json.load(f)

with open('./mlbench/mlbench.json', 'r') as f:
    mlbench = json.load(f)

import pdb; pdb.set_trace()
assert list(mlbench_full.keys()) == list(mlbench.keys())

for key in mlbench_full.keys():
    full_data = mlbench_full[key]
    data = mlbench[key]
    assert full_data['paper_data'] == data['paper_data']
    #assert full_data['author_data'] == data['author_data']
    assert full_data['reference_proposal'] == data['reference_proposal']
