import voyageai
import json
import numpy as np
from tqdm import tqdm

# embed 

with open('./paper_bench/agent_number_ablation_paper_bench.json', 'r') as f:
    dataset = json.load(f)

for key, data in tqdm(dataset.items()):
    author_data = data['author_data']
    bios = []
    pks = []
    for author in author_data.values():
        bios.append(author['bio'])
    
    for author_pk in author_data.keys():
        pks.append(author_pk)
    
    abstract = data['paper_data']['abstract']

    abstract_embed = voyageai.get_embedding(abstract, model='voyage-3', input_type='document')

    for pk, bio in zip(pks, bios):
        bio_embed = voyageai.get_embedding(bio, model='voyage-3', input_type='document')
        similarity = np.dot(abstract_embed, bio_embed) / (np.linalg.norm(abstract_embed) * np.linalg.norm(bio_embed))
        print(similarity)
        dataset[key]['author_data'][pk]['bio_relatedness_with_abstract'] = similarity

with open('./paper_bench/agent_number_ablation_paper_bench_with_relatedness.json', 'w') as f:
    json.dump(dataset, f, indent=4)