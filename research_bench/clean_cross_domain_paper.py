import json

with open('./oodbench/oodbench_1203.json', 'r') as f:
    dataset = json.load(f)

with open('./oodbench/oodbench_ml_1203.json', 'r') as f:
    ml_dataset = json.load(f)

dataset = {**dataset, **ml_dataset}

#with open('./oodbench/oodbench_paper_titles.txt') as f:
#    paper_titles = f.read().splitlines()

#filtered_dataset = {}
#for key, value in dataset.items():
#    filtered_dataset[key] = value


new_dataset = {}
for key, data in dataset.items():
    authors = data['paper_data']['authors']
    title = data['paper_data']['title']
    author_info_dict = data['author_data']
    valid_references = [ref for ref in data['paper_data']['references'] if ref['abstract'] is not None]
    if len(authors) != len(author_info_dict):
        print(len(authors), len(author_info_dict))
        continue
    if len(valid_references) < 5:
        continue
    if data['paper_data']['abstract'] is None or len(data['paper_data']['abstract']) < 5:
        continue
    if data['paper_data']['introduction'] is None or len(data['paper_data']['introduction']) < 5:
        continue
    new_dataset[key] = data

# select 100 papers in new_dataset
new_dataset = dict(list(new_dataset.items())[:100])
print(len(new_dataset))

with open('./oodbench/oodbench_1203_filtered.json', 'w') as f:
    json.dump(new_dataset, f, indent=4)