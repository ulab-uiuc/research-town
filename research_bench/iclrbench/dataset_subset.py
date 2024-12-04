import json

file_to_get_ids = 'iclrbench_filtered.json'

with open(file_to_get_ids, 'r', encoding='utf-8') as f:
    data = json.load(f)
    paper_ids = [id for id in data]

file_to_filter = 'iclrbench_reviewers_full_content.json'

with open(file_to_filter, 'r', encoding='utf-8') as f:
    data = json.load(f)
    data_keys = [key for key in data]
    for id in data_keys:
        if id not in paper_ids:
            del data[id]

# file_save = 'iclrbench_reviewers_filtered.json'

# with open(file_save, 'w', encoding='utf-8') as f:
#     json.dump(data, f, indent=4)

file_save = 'iclrbench_filtered_ids.json'

with open(file_save, 'w', encoding='utf-8') as f:
    json.dump(paper_ids, f, indent=4)