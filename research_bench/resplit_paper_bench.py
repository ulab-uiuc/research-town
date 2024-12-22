import json
import jsonlines

def process_value(value, with_reviews=False):
    value['paper_data']['evaluation_format'] = {
        'model': 'gpt-4o-mini',
        'content': value['reference_proposal']
    }
    del value['reference_proposal']
    if with_reviews is False:
        if 'reviews' in value:
            del value['reviews']
    filtered_references = []
    for reference in value['paper_data']['references']:
        if 'reference_section' in reference:
            del reference['reference_section']
        if reference['abstract'] is not None:
            filtered_references.append(reference)

    value['paper_data']['references'] = filtered_references

    for author_id, author_data in value['author_data'].items():
        del value['author_data'][author_id]['project_name']
        del value['author_data'][author_id]['bio']
        for pub_title, pub_abstract in zip(author_data['pub_titles'], author_data['pub_abstracts']):
            if pub_abstract is None:
                continue
                
            if 'publications' not in value['author_data'][author_id]:
                value['author_data'][author_id]['publications'] = []
            value['author_data'][author_id]['publications'].append({
                'title': pub_title,
                'abstract': pub_abstract
            })
        del value['author_data'][author_id]['pub_titles']
        del value['author_data'][author_id]['pub_abstracts']
        del value['author_data'][author_id]['institute']
        del value['author_data'][author_id]['embed']
        del value['author_data'][author_id]['is_leader_candidate']
        del value['author_data'][author_id]['is_member_candidate']
        del value['author_data'][author_id]['is_reviewer_candidate']
        del value['author_data'][author_id]['is_chair_candidate']
    return value


def process_review_bench_value(value):
    value['paper_data']['evaluation_format'] = {
        'model': 'gpt-4o-mini',
        'content': value['reference_proposal']
    }
    del value['reference_proposal']
    filtered_references = []
    for reference in value['paper_data']['references']:
        if 'reference_section' in reference:
            del reference['reference_section']
        if reference['abstract'] is not None:
            filtered_references.append(reference)

    value['paper_data']['references'] = filtered_references

    # change a key name
    value['review_data'] = value.pop('reviews')
    for key in ['author_data', 'reviewer_data']:
        for author_id, author_data in value[key].items():
            del value[key][author_id]['project_name']
            del value[key][author_id]['bio']
            for pub_title, pub_abstract in zip(author_data['pub_titles'], author_data['pub_abstracts']):
                if pub_abstract is None:
                    continue
                    
                if 'publications' not in value[key][author_id]:
                    value[key][author_id]['publications'] = []
                value[key][author_id]['publications'].append({
                    'title': pub_title,
                    'abstract': pub_abstract
                })
            del value[key][author_id]['pub_titles']
            del value[key][author_id]['pub_abstracts']
            del value[key][author_id]['institute']
            del value[key][author_id]['embed']
            del value[key][author_id]['is_leader_candidate']
            del value[key][author_id]['is_member_candidate']
            del value[key][author_id]['is_reviewer_candidate']
            del value[key][author_id]['is_chair_candidate']

    value['paper_data']['full_content'] = value.pop('full_content')
    reviewer_assign_similarity = value.pop('reviewer_assign_similarity')
    for reviewer_id, reviewer_data in value['reviewer_data'].items():
        value['reviewer_data'][reviewer_id]['reviewer_match_similarity'] = reviewer_assign_similarity[reviewer_id]

    for idx, review in enumerate(value['review_data']):
        value['review_data'][idx]['strength_evaluation_format'] = review['strengths_bullet']
        value['review_data'][idx]['weakness_evaluation_format'] = review['weaknesses_bullet']
        value['review_data'][idx].pop('strengths_bullet')
        value['review_data'][idx].pop('weaknesses_bullet')
    return value

##########################
# 1. Load the citation-only dataset
##########################

with jsonlines.open('./results/paper_bench_mid_500_result_4o_mini_citation_only_with_nv_filtered.jsonl', 'r') as reader:
    mid_dataset_citation = list(reader)

with jsonlines.open('./results/paper_bench_hard_500_result_4o_mini_citation_only_with_nv_filtered.jsonl', 'r') as reader:
    hard_dataset_citation = list(reader)

with jsonlines.open('./results/paper_bench_easy_500_result_4o_mini_citation_only_with_nv_filtered.jsonl', 'r') as reader:
    easy_dataset_citation = list(reader)

citation_dataset = mid_dataset_citation + hard_dataset_citation + easy_dataset_citation

##########################
# 2. Compute the avg_openai_sim and sort
##########################

for data in citation_dataset:
    avg_openai_sim = sum(data[f'openai_sim_q{i}'] for i in range(1, 6)) / 5
    data['avg_openai_sim'] = avg_openai_sim

citation_dataset.sort(key=lambda x: x['avg_openai_sim'], reverse=True)

##########################
# 3. Split citation-only into easy/mid/hard
##########################

new_easy_dataset_citation = citation_dataset[:333]
new_mid_dataset_citation  = citation_dataset[333:667]    # next 334
new_hard_dataset_citation = citation_dataset[667:]

with jsonlines.open('./results/paper_bench_easy_500_result_4o_mini_citation_only_resplit.jsonl', 'w') as writer:
    writer.write_all(new_easy_dataset_citation)

with jsonlines.open('./results/paper_bench_mid_500_result_4o_mini_citation_only_resplit.jsonl', 'w') as writer:
    writer.write_all(new_mid_dataset_citation)

with jsonlines.open('./results/paper_bench_hard_500_result_4o_mini_citation_only_resplit.jsonl', 'w') as writer:
    writer.write_all(new_hard_dataset_citation)

# Show average similarity for sanity check:
print("Citation-only splits:")
print("Easy avg:", sum(d['avg_openai_sim'] for d in new_easy_dataset_citation)/len(new_easy_dataset_citation))
print("Mid avg:",  sum(d['avg_openai_sim'] for d in new_mid_dataset_citation)/len(new_mid_dataset_citation))
print("Hard avg:", sum(d['avg_openai_sim'] for d in new_hard_dataset_citation)/len(new_hard_dataset_citation))

##########################
# 4. Get ID-based membership in each split
##########################

easy_ids = [d["paper_id"] for d in new_easy_dataset_citation]
mid_ids  = [d["paper_id"] for d in new_mid_dataset_citation]
hard_ids = [d["paper_id"] for d in new_hard_dataset_citation]

##########################
# 5. Create a reusable function
#    to split a dataset by the above IDs
##########################

def resplit_dataset_by_ids(dataset, easy_ids, mid_ids, hard_ids):
    """
    dataset: a list of dicts, each containing "paper_id"
    easy_ids, mid_ids, hard_ids: IDs used to form new splits
    returns: (easy_list, mid_list, hard_list)
    """
    # Create a dictionary for quick lookup
    by_id = {d["paper_id"]: d for d in dataset}
    
    # Build each new split by ID
    easy_data = [by_id[i] for i in easy_ids if i in by_id]
    mid_data  = [by_id[i] for i in mid_ids  if i in by_id]
    hard_data = [by_id[i] for i in hard_ids if i in by_id]
    
    return easy_data, mid_data, hard_data

##########################
# 6. For each other mode, 
#    load + re-split using the above function
##########################

# 6.1. fake_research_town
with jsonlines.open('./results/paper_bench_mid_500_result_4o_mini_fake_research_town_with_nv_filtered.jsonl', 'r') as reader:
    mid_fake = list(reader)
with jsonlines.open('./results/paper_bench_hard_500_result_4o_mini_fake_research_town_with_nv_filtered.jsonl', 'r') as reader:
    hard_fake = list(reader)
with jsonlines.open('./results/paper_bench_easy_500_result_4o_mini_fake_research_town_with_nv_filtered.jsonl', 'r') as reader:
    easy_fake = list(reader)

fake_dataset = mid_fake + hard_fake + easy_fake

new_easy_fake, new_mid_fake, new_hard_fake = resplit_dataset_by_ids(
    fake_dataset, easy_ids, mid_ids, hard_ids
)

with jsonlines.open('./results/paper_bench_easy_500_result_4o_mini_fake_research_town_resplit.jsonl', 'w') as writer:
    writer.write_all(new_easy_fake)
with jsonlines.open('./results/paper_bench_mid_500_result_4o_mini_fake_research_town_resplit.jsonl', 'w') as writer:
    writer.write_all(new_mid_fake)
with jsonlines.open('./results/paper_bench_hard_500_result_4o_mini_fake_research_town_resplit.jsonl', 'w') as writer:
    writer.write_all(new_hard_fake)

# 6.2. author_only
with jsonlines.open('./results/paper_bench_mid_500_result_4o_mini_author_only_with_nv_filtered.jsonl', 'r') as reader:
    mid_author = list(reader)
with jsonlines.open('./results/paper_bench_hard_500_result_4o_mini_author_only_with_nv_filtered.jsonl', 'r') as reader:
    hard_author = list(reader)
with jsonlines.open('./results/paper_bench_easy_500_result_4o_mini_author_only_with_nv_filtered.jsonl', 'r') as reader:
    easy_author = list(reader)

author_dataset = mid_author + hard_author + easy_author

new_easy_author, new_mid_author, new_hard_author = resplit_dataset_by_ids(
    author_dataset, easy_ids, mid_ids, hard_ids
)

with jsonlines.open('./results/paper_bench_easy_500_result_4o_mini_author_only_resplit.jsonl', 'w') as writer:
    writer.write_all(new_easy_author)
with jsonlines.open('./results/paper_bench_mid_500_result_4o_mini_author_only_resplit.jsonl', 'w') as writer:
    writer.write_all(new_mid_author)
with jsonlines.open('./results/paper_bench_hard_500_result_4o_mini_author_only_resplit.jsonl', 'w') as writer:
    writer.write_all(new_hard_author)

# 6.3. zero_shot
with jsonlines.open('./results/paper_bench_mid_500_result_4o_mini_zero_shot_with_nv_filtered.jsonl', 'r') as reader:
    mid_zero = list(reader)
with jsonlines.open('./results/paper_bench_hard_500_result_4o_mini_zero_shot_with_nv_filtered.jsonl', 'r') as reader:
    hard_zero = list(reader)
with jsonlines.open('./results/paper_bench_easy_500_result_4o_mini_zero_shot_with_nv_filtered.jsonl', 'r') as reader:
    easy_zero = list(reader)

zero_dataset = mid_zero + hard_zero + easy_zero

new_easy_zero, new_mid_zero, new_hard_zero = resplit_dataset_by_ids(
    zero_dataset, easy_ids, mid_ids, hard_ids
)

with jsonlines.open('./results/paper_bench_easy_500_result_4o_mini_zero_shot_resplit.jsonl', 'w') as writer:
    writer.write_all(new_easy_zero)
with jsonlines.open('./results/paper_bench_mid_500_result_4o_mini_zero_shot_resplit.jsonl', 'w') as writer:
    writer.write_all(new_mid_zero)
with jsonlines.open('./results/paper_bench_hard_500_result_4o_mini_zero_shot_resplit.jsonl', 'w') as writer:
    writer.write_all(new_hard_zero)


with open('./paper_bench/paper_bench_easy_500_filtered_1205.json', 'r') as f:
    easy_data = json.load(f)

with open('./paper_bench/paper_bench_mid_500_filtered_1205.json', 'r') as f:
    mid_data = json.load(f)

with open('./paper_bench/paper_bench_hard_500_filtered_1205.json', 'r') as f:
    hard_data = json.load(f)

data = {**easy_data, **mid_data, **hard_data}

new_easy_dataset_citation = {}
new_mid_dataset_citation = {}
new_hard_dataset_citation = {}

for paper_id, value in data.items():
    value = process_value(value)
    if paper_id in easy_ids:
        new_easy_dataset_citation[paper_id] = value
    elif paper_id in mid_ids:
        new_mid_dataset_citation[paper_id] = value
    elif paper_id in hard_ids:
        new_hard_dataset_citation[paper_id] = value

with open('./paper_bench/paper_bench_easy.json', 'w') as f:
    json.dump(new_easy_dataset_citation, f, indent=4)

with open('./paper_bench/paper_bench_mid.json', 'w') as f:
    json.dump(new_mid_dataset_citation, f, indent=4)

with open('./paper_bench/paper_bench_hard.json', 'w') as f:
    json.dump(new_hard_dataset_citation, f, indent=4)


with open('./oodbench/oodbench_1203_filtered.json', 'r') as f:
    high_impact_data = json.load(f)

new_high_impact_data = {}

for paper_id, value in high_impact_data.items():
    value = process_value(value)
    new_high_impact_data[paper_id] = value

with open('./oodbench/high_impact_paper_bench.json', 'w') as f:
    json.dump(new_high_impact_data, f, indent=4)


with open('./iclrbench/iclrbench_reviewers_filtered_bullets.json', 'r') as f:
    iclr_data = json.load(f)

new_iclr_data = {}

for paper_id, value in iclr_data.items():
    value = process_review_bench_value(value)
    new_iclr_data[paper_id] = value

with open('./iclrbench/review_bench.json', 'w') as f:
    json.dump(new_iclr_data, f, indent=4)

import pdb; pdb.set_trace()