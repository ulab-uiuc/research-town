import json
from voyageai.client import Client

file_name_from = "iclrbench.json"
file_name_to = "iclrbench_reviewers.json"

def cosine_similarity(vec1, vec2):
    return sum(a * b for a, b in zip(vec1, vec2)) / (
        (sum(a * a for a in vec1) ** 0.5) * (sum(b * b for b in vec2) ** 0.5)
    )


with open(file_name_from, "r", encoding="utf-8") as f:
    dataset = json.load(f)
    # prepare profile dataset to keep track of all author data
    author_data_dict = {}
    for paper_id in dataset:
        paper_data = dataset[paper_id]
        author_datas = paper_data['author_data']
        for author_pk in author_datas:
            author_data = author_datas[author_pk]
            author_data_dict[author_pk] = author_data

    top_k = 20

    # prepare the client, use voyage-3
    client = Client()
    author_keys = list(author_data_dict.keys())
    # profile_embeddings = client.embed([author_data_dict[author_pk]['bio'] for author_pk in author_keys], input_type='document')
    profile_embeddings = {}
    batch_size = 128
    for i in range(0, len(author_keys), batch_size):
        author_keys_batch = author_keys[i:i+batch_size]
        author_bios = [author_data_dict[author_pk]['bio'] for author_pk in author_keys_batch]
        profile_embeddings_batch = client.embed(author_bios, input_type='document', model='voyage-3')
        for author_pk, embedding in zip(author_keys_batch, profile_embeddings_batch.embeddings):
            profile_embeddings[author_pk] = embedding

    all_papers_count = len(dataset)
    processed_papers_count = 0
    dropped_papers_count = 0

    for paper_id in dataset:
        print(f"Processing paper {processed_papers_count:8d}/{all_papers_count:8d}; Dropped papers: {dropped_papers_count:8d}", end="\r")
        paper_data = dataset[paper_id]

        author_datas = paper_data['author_data']

        intro = paper_data['paper_data']['abstract']
        # print(paper_data['paper_data']['title'])

        #if paper_data['paper_data']['title'] == "SOTOPIA: Interactive Evaluation for Social Intelligence in Language Agents":
        #    # print all author names
        #    print("Authors:")
        #    for author_pk in author_datas:
        #        # pk, name
        #        print(f"{author_datas[author_pk]['name']} ({author_datas[author_pk]['pk']})")
        #    import pdb; pdb.set_trace()
        
        processed_papers_count += 1
        
        query_embedding = client.embed([intro], input_type='query', model='voyage-3').embeddings[0]

        # get current paper author pks
        author_names = [author_datas[author_pk]['name'] for author_pk in author_datas]
        
        profile_similarities = [
            (author_pk, cosine_similarity(query_embedding, embedding))
            for author_pk, embedding in profile_embeddings.items() if author_data_dict[author_pk]['name'] not in author_names
        ]

        profile_similarities.sort(key=lambda x: x[1], reverse=True)

        top_reviewer_pks = [author_pk for author_pk, _ in profile_similarities[:top_k]]

        paper_data['reviewer_assign_similarity'] = {
            author_pk: similarity
            for author_pk, similarity in profile_similarities[:top_k]
        }
        paper_data['reviewer_data'] = {
            author_pk: author_data_dict[author_pk]
            for author_pk in top_reviewer_pks
        }

        # print all matched reviewer names
        # print("Matched reviewers:")
        # for i in range(top_k):
        #     author_pk, similarity = profile_similarities[i]
        #     print(f"{i+1:2d}. {author_data_dict[author_pk]['name']} (similarity: {similarity:.4f})")
    
    # drop all papers without introduction
    
    with open(file_name_to, "w", encoding="utf-8") as f:
        json.dump(dataset, f, indent=4)
    
    print(f"Processing paper {processed_papers_count:8d}/{all_papers_count:8d}; Dropped papers: {dropped_papers_count:8d}", end="\r")
