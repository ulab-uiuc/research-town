import json
from research_town.utils.paper_collector import get_paper_content_from_pdf, get_paper_content_from_html
from tqdm import tqdm
import time

file_name_from = "iclrbench_reviewers.json"
file_name_to = "iclrbench_reviewers_full_content_2.json"

with open(file_name_from, "r", encoding="utf-8") as f:
    dataset = json.load(f)
    # for paper_id in dataset:
    for paper_id in tqdm(dataset):
        
        paper_html_url = f'https://export.arxiv.org/html/{paper_id}' # for frequent access
        paper_pdf_url = f'https://export.arxiv.org/pdf/{paper_id}' # 2nd choice

        paper_full_text = get_paper_content_from_pdf(paper_pdf_url)
        
        if paper_full_text is None:
            print(f"Failed to get full content for paper {paper_id}, redo once more")
            time.sleep(4)
            paper_full_text = get_paper_content_from_pdf(paper_pdf_url)
            if paper_full_text is None:
                print(f"Failed to get full content for paper {paper_id} again, skip")
            
        dataset[paper_id]['full_content'] = paper_full_text

# with open(file_name_to, "w", encoding="utf-8") as f:
#     json.dump(dataset, f, indent=4)

