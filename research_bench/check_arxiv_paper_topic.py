import arxiv
import json
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor

# Load arXiv IDs
with open('./paper_bench/paper_bench_full.json', 'r') as f:
    paper_bench_full = json.load(f)
    arxiv_ids = list(paper_bench_full.keys())

# Function to process a batch of arXiv IDs
def process_batch(batch):
    updated_papers = {}
    search = arxiv.Search(id_list=batch)
    for result in search.results():
        categories = result.categories
        updated_papers[result.entry_id.split('/')[-1].split('v')[0]] = {"categories": categories}
    return updated_papers

# Batch size
batch_size = 10

# Collect results
updated_results = {}
with ThreadPoolExecutor() as executor:
    for i in tqdm(range(0, len(arxiv_ids), batch_size)):
        batch = arxiv_ids[i:i+batch_size]
        results = executor.submit(process_batch, batch).result()
        updated_results.update(results)

# Update original dictionary
for arxiv_id, data in updated_results.items():
    paper_bench_full[arxiv_id]['paper_data']['categories'] = data['categories']

# Write results to file
with open('./paper_bench/paper_bench_full_with_categories.json', 'w') as f:
    json.dump(paper_bench_full, f, indent=4)
