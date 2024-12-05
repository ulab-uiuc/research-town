import json

with open('./crossbench/crossbench.json') as f:
    dataset = json.load(f)

filtered_dataset = {}
for key, value in dataset.items():
    filtered_dataset[key] = value
    if len(filtered_dataset) > 500:
        break


new_dataset = {}
for key, data in filtered_dataset.items():
    authors = data['paper_data']['authors']
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

print(len(new_dataset))