import json

import numpy as np
from voyageai.client import Client

input_file = 'iclrbench_reviewers_filtered_bullets_100.json'

# OPENAI
from litellm import embedding

# VOYAGEAI
vo = Client()

# for strength in strengths:
#     response = embedding(model='text-embedding-3-large', input=[strength])
#     embedding_strength = response['data'][0]['embedding']
#     all_strength_openai_embeddings.append(embedding_strength)

#     response = vo.embed(model='voyage-3', texts=[strength], input_type='document')
#     embedding_strength = response.embeddings[0]
#     all_strength_voyageai_embeddings.append(embedding_strength)

# for weakness in weaknesses:
#     response = embedding(model='text-embedding-3-large', input=[weakness])
#     embedding_weakness = response['data'][0]['embedding']
#     all_weakness_openai_embeddings.append(embedding_weakness)

#     response = vo.embed(model='voyage-3', texts=[weakness], input_type='document')
#     embedding_weakness = response.embeddings[0]
#     all_weakness_voyageai_embeddings.append(embedding_weakness)


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


a = 'Large Language Models (LLMs) have shown remarkable capabilities in reasoning, exemplified by the success of OpenAI-o1 and DeepSeek-R1. However, integrating reasoning with external search processes remains challenging, especially for complex multi-hop questions requiring multiple retrieval steps. We propose ReSearch, a novel framework that trains LLMs to Reason with Search via reinforcement learning without using any supervised data on reasoning steps. Our approach treats search operations as integral components of the reasoning chain, where when and how to perform searches is guided by text-based thinking, and search results subsequently influence further reasoning. We train ReSearch on Qwen2.5-7B(-Instruct) and Qwen2.5-32B(-Instruct) models and conduct extensive experiments. Despite being trained on only one dataset, our models demonstrate strong generalizability across various benchmarks. Analysis reveals that ReSearch naturally elicits advanced reasoning capabilities such as reflection and self-correction during the reinforcement learning process.'
b = 'Efficiently acquiring external knowledge and up-to-date information is essential for effective reasoning and text generation in large language models (LLMs). Prompting advanced LLMs with reasoning capabilities during inference to use search engines is not optimal, since the LLM does not learn how to optimally interact with the search engine. This paper introduces Search-R1, an extension of the DeepSeek-R1 model where the LLM learns -- solely through reinforcement learning (RL) -- to autonomously generate (multiple) search queries during step-by-step reasoning with real-time retrieval. Search-R1 optimizes LLM rollouts with multi-turn search interactions, leveraging retrieved token masking for stable RL training and a simple outcome-based reward function. Experiments on seven question-answering datasets show that Search-R1 improves performance by 26% (Qwen2.5-7B), 21% (Qwen2.5-3B), and 10% (LLaMA3.2-3B) over strong baselines. This paper further provides empirical insights into RL optimization methods, LLM choices, and response length dynamics in retrieval-augmented reasoning. The code and model checkpoints are available at this https URL.'

# calculate similarities

openai_sim_val = openai_sim(a, b)
voyageai_sim_val = voyageai_sim(a, b)

print(f'OpenAI Similarity: {openai_sim_val:.4f}')
print(f'VoyageAI Similarity: {voyageai_sim_val:.4f}')

exit(0)

with open(input_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

    dict_to_save = {}

    # trim
    limit = 50
    keys = data.keys()
    keys = list(keys)  # Convert keys to a list to slice
    keys = keys[:limit]  # Limit the number of keys to 'limit' items
    data = {key: data[key] for key in keys}  # Trim the data to the first 'limit' items

    avg_strength_sim_openai_paper = []
    avg_strength_sim_voyageai_paper = []
    avg_weakness_sim_openai_paper = []
    avg_weakness_sim_voyageai_paper = []

    # for key in data:
    from tqdm import tqdm

    for key in tqdm(data.keys(), desc='Processing papers'):
        item = data[key]
        paper_id = key
        item_reviews = item['reviews']
        strengths = []
        weaknesses = []
        for review in item_reviews:
            strengths.append(review['strengths'])
            weaknesses.append(review['weaknesses'])

        assert (
            len(strengths) == len(weaknesses)
        ), f'Mismatch in number of strengths and weaknesses for paper {paper_id}. Strengths: {len(strengths)}, Weaknesses: {len(weaknesses)}'

        strength_sims_openai = []
        strength_sims_voyageai = []
        weakness_sims_openai = []
        weakness_sims_voyageai = []
        for i in range(len(strengths)):
            for j in range(i + 1, len(strengths)):
                # Calculate similarity using OpenAI
                sim_openai = openai_sim(strengths[i], strengths[j])
                strength_sims_openai.append(sim_openai)

                # Calculate similarity using VoyageAI
                sim_voyageai = voyageai_sim(strengths[i], strengths[j])
                strength_sims_voyageai.append(sim_voyageai)

        for i in range(len(weaknesses)):
            for j in range(i + 1, len(weaknesses)):
                # Calculate similarity using OpenAI
                sim_openai = openai_sim(weaknesses[i], weaknesses[j])
                weakness_sims_openai.append(sim_openai)

                # Calculate similarity using VoyageAI
                sim_voyageai = voyageai_sim(weaknesses[i], weaknesses[j])
                weakness_sims_voyageai.append(sim_voyageai)

        assert (
            len(strength_sims_openai) == len(strengths) * (len(strengths) - 1) / 2
        ), f'Mismatch in strength similarity count for paper {paper_id}'
        assert (
            len(strength_sims_voyageai) == len(strengths) * (len(strengths) - 1) / 2
        ), f'Mismatch in strength similarity count for paper {paper_id}'

        assert (
            len(weakness_sims_openai) == len(weaknesses) * (len(weaknesses) - 1) / 2
        ), f'Mismatch in weakness similarity count for paper {paper_id}'
        assert (
            len(weakness_sims_voyageai) == len(weaknesses) * (len(weaknesses) - 1) / 2
        ), f'Mismatch in weakness similarity count for paper {paper_id}'

        avg_strength_sim_openai = (
            np.mean(strength_sims_openai) if strength_sims_openai else 0
        )
        avg_strength_sim_voyageai = (
            np.mean(strength_sims_voyageai) if strength_sims_voyageai else 0
        )
        avg_weakness_sim_openai = (
            np.mean(weakness_sims_openai) if weakness_sims_openai else 0
        )
        avg_weakness_sim_voyageai = (
            np.mean(weakness_sims_voyageai) if weakness_sims_voyageai else 0
        )

        avg_strength_sim_openai_paper.append(avg_strength_sim_openai)
        avg_strength_sim_voyageai_paper.append(avg_strength_sim_voyageai)
        avg_weakness_sim_openai_paper.append(avg_weakness_sim_openai)
        avg_weakness_sim_voyageai_paper.append(avg_weakness_sim_voyageai)

        dict_to_save[paper_id] = {
            'avg_strength_sim_openai': avg_strength_sim_openai,
            'avg_strength_sim_voyageai': avg_strength_sim_voyageai,
            'avg_weakness_sim_openai': avg_weakness_sim_openai,
            'avg_weakness_sim_voyageai': avg_weakness_sim_voyageai,
            'strength_sims_openai': strength_sims_openai,
            'strength_sims_voyageai': strength_sims_voyageai,
            'weakness_sims_openai': weakness_sims_openai,
            'weakness_sims_voyageai': weakness_sims_voyageai,
        }

    # Calculate overall averages
    overall_avg_strength_sim_openai = (
        np.mean(avg_strength_sim_openai_paper) if avg_strength_sim_openai_paper else 0
    )
    overall_avg_strength_sim_voyageai = (
        np.mean(avg_strength_sim_voyageai_paper)
        if avg_strength_sim_voyageai_paper
        else 0
    )
    overall_avg_weakness_sim_openai = (
        np.mean(avg_weakness_sim_openai_paper) if avg_weakness_sim_openai_paper else 0
    )
    overall_avg_weakness_sim_voyageai = (
        np.mean(avg_weakness_sim_voyageai_paper)
        if avg_weakness_sim_voyageai_paper
        else 0
    )

    # print the results
    print(f'AVG AVG STRENGTH SIMILARITY OPENAI: {overall_avg_strength_sim_openai:.4f}')
    print(
        f'AVG AVG STRENGTH SIMILARITY VOYAGEAI: {overall_avg_strength_sim_voyageai:.4f}'
    )
    print(f'AVG AVG WEAKNESS SIMILARITY OPENAI: {overall_avg_weakness_sim_openai:.4f}')
    print(
        f'AVG AVG WEAKNESS SIMILARITY VOYAGEAI: {overall_avg_weakness_sim_voyageai:.4f}'
    )

    # Save the results to a JSON file
    output_file = 'iclrbench_human_review_similarities_50.json'
    with open(output_file, 'w', encoding='utf-8') as out_f:
        json.dump(dict_to_save, out_f, indent=4)
