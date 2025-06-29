import json
import numpy as np
from litellm import embedding
from voyageai.client import Client
vo = Client()

main_file = 'mlbench_result_4o_mini_sakana_ai_scientist_100.jsonl'
file_a = 'paper_bench_mid_500_result_4o_mini_fake_research_town.jsonl'
file_b = 'paper_bench_easy_500_result_4o_mini_fake_research_town_resplit.jsonl'
file_c = 'paper_bench_hard_500_result_4o_mini_fake_research_town.jsonl'

with open(main_file, 'r', encoding='utf-8') as f:
    main_data = [json.loads(line) for line in f]
    main_keys = [item["paper_id"] for item in main_data]
    main_data_dict = {item["paper_id"]: item for item in main_data}

keys_common = []

with open(file_a, 'r', encoding='utf-8') as f:
    data_a = [json.loads(line) for line in f]

with open(file_b, 'r', encoding='utf-8') as f:
    data_b = [json.loads(line) for line in f]

with open(file_c, 'r', encoding='utf-8') as f:
    data_c = [json.loads(line) for line in f]
    data_c = data_a + data_b + data_c
    data_c_trim_dict = {}
    data_c_dict = {item["paper_id"]: item for item in data_c}
    for key in main_keys:
        if key in data_c_dict:
            data_c_trim_dict[key] = data_c_dict[key]
            keys_common.append(key)
        else:
            print(f"Key {key} not found in file_c")

keys_common = list(set(keys_common))

main_proposals = []
c_proposals = []

for key in keys_common:
    main_proposals.append(main_data_dict[key]['gen_proposal'])
    c_proposals.append(data_c_trim_dict[key]['gen_proposal'])

print(f"Number of main keys: {len(main_keys)}")
print(f"Number of common keys: {len(keys_common)}")

def openai_sim(str_a, str_b):
    """
    Calculate cosine similarity between two strings using OpenAI embeddings.
    """

    # Get embeddings for both strings
    response_a = embedding(model='text-embedding-3-large', input=[str_a])
    response_b = embedding(model='text-embedding-3-large', input=[str_b])

    embedding_a = response_a['data'][0]['embedding']
    embedding_b = response_b['data'][0]['embedding']

    cosine_sim = np.dot(embedding_a, embedding_b) / (
        np.linalg.norm(embedding_a) * np.linalg.norm(embedding_b)
    )
    
    return cosine_sim

def voyageai_sim(str_a, str_b):
    """
    Calculate cosine similarity between two strings using VoyageAI embeddings.
    """

    # Get embeddings for both strings
    response_a = vo.embed(model='voyage-3', texts=[str_a], input_type='document')
    response_b = vo.embed(model='voyage-3', texts=[str_b], input_type='document')

    embedding_a = response_a.embeddings[0]
    embedding_b = response_b.embeddings[0]

    cosine_sim = np.dot(embedding_a, embedding_b) / (
        np.linalg.norm(embedding_a) * np.linalg.norm(embedding_b)
    )
    
    return cosine_sim

openai_sims_c = []
voyageai_sims_c = []

# for main_p, c_p in zip(main_proposals, c_proposals):
# from tqdm import tqdm
# for main_p, c_p in tqdm(zip(main_proposals, c_proposals), total=len(main_proposals)):
#     openai_sim_c = openai_sim(main_p, c_p)

#     voyageai_sim_c = voyageai_sim(main_p, c_p)

#     # print(f"OpenAI Similarity: {openai_sim_c}")
#     # print(f"VoyageAI Similarity: {voyageai_sim_c}")

#     openai_sims_c.append(openai_sim_c)
#     voyageai_sims_c.append(voyageai_sim_c)

# # Save the results to a file
# with open('similarity_results.json', 'w') as f:
#     json.dump({
#         'openai_sims_c': openai_sims_c,
#         'voyageai_sims_c': voyageai_sims_c,
#     }, f, indent=4)

# # print overall - avg
# avg_openai_sim_c = np.mean(openai_sims_c)
# avg_voyageai_sim_c = np.mean(voyageai_sims_c)

# print()
# print(f"Average OpenAI Similarity: {avg_openai_sim_c}")
# print(f"Average VoyageAI Similarity: {avg_voyageai_sim_c}")

# average the "openai_sim" key in main_data_dict, data_c_dict, under 70 common keys
openai_sim_sakana_ai_scientist = []
openai_sim_research_town = []

for key in keys_common:
    sakana_score = np.mean([main_data_dict[key]['embedding_similarity_q1'], 
                            main_data_dict[key]['embedding_similarity_q2'], 
                            main_data_dict[key]['embedding_similarity_q3'],
                            main_data_dict[key]['embedding_similarity_q4'],
                            main_data_dict[key]['embedding_similarity_q5']])
    openai_sim_sakana_ai_scientist.append(sakana_score)
    town_score = np.mean([data_c_trim_dict[key]['openai_sim_q1'],
                          data_c_trim_dict[key]['openai_sim_q2'],
                          data_c_trim_dict[key]['openai_sim_q3'],
                          data_c_trim_dict[key]['openai_sim_q4'],
                          data_c_trim_dict[key]['openai_sim_q5']])
    openai_sim_research_town.append(town_score)

# assert len(openai_sim_sakana_ai_scientist) == len(openai_sim_research_town)
assert len(openai_sim_sakana_ai_scientist) == len(keys_common)
assert len(openai_sim_research_town) == len(keys_common)

print(f"Number of common keys: {len(keys_common)}")
print(f"Number of openai_sim_sakana_ai_scientist: {len(openai_sim_sakana_ai_scientist)}")
print(f"Number of openai_sim_research_town: {len(openai_sim_research_town)}")
# print the average of openai_sim_sakana_ai_scientist
avg_openai_sim_sakana_ai_scientist = np.mean(openai_sim_sakana_ai_scientist)
avg_openai_sim_research_town = np.mean(openai_sim_research_town)
print(f"Average OpenAI Similarity Sakana AI Scientist: {avg_openai_sim_sakana_ai_scientist}")
print(f"Average OpenAI Similarity Research Town: {avg_openai_sim_research_town}")

# save the results to a file
with open('openai_similarity_results_2.json', 'w') as f:
    json.dump({
        'openai_sim_sakana_ai_scientist': openai_sim_sakana_ai_scientist,
        'openai_sim_research_town': openai_sim_research_town,
    }, f, indent=4)