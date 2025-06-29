import json
from typing import List

import numpy as np
from voyageai import Client


def extract_qs_from_proposal(proposal):
    """Extract the full text of the 5 questions from the proposal."""
    # Return the proposal as is since it already contains the 5 questions
    return proposal


class SimilarityCalculator:
    def __init__(self, api_key):
        """Initialize Voyage AI client."""
        self.voyage_client = Client(api_key=api_key)

    def get_embedding(self, text: str) -> List[float]:
        """
        Get embedding vector for text using Voyage AI.

        Args:
            text: Text to embed

        Returns:
            Embedding vector
        """
        try:
            response = self.voyage_client.embed(
                text, model='voyage-large-2', input_type='document'
            )
            return response.embeddings[0]
        except Exception as e:
            print(f'Error getting embedding: {e}')
            # Return empty embedding if there's an error
            return [0.0] * 1024

    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors.

        Args:
            vec1: First vector
            vec2: Second vector

        Returns:
            Cosine similarity value
        """
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))


def main():
    # Initialize Voyage AI client
    # Replace 'your_voyage_api_key' with actual API key
    import os

    similarity_calculator = SimilarityCalculator(
        api_key=os.environ.get('VOYAGE_API_KEY')
    )

    # Read the input JSON file
    with open('paper_bench_hard_500_filtered_1205_trim.json', 'r') as f:
        paper_data = json.load(f)

    # Read the generated proposals
    proposals = {}
    with open(
        'paperbench_gnn_v2_result_baseline_4o_mini_author_citation.jsonl', 'r'
    ) as f:
        for line in f:
            try:
                data = json.loads(line)
                paper_id = data.get('paper_id')
                gen_proposal = data.get('gen_proposal')
                if paper_id and gen_proposal:
                    proposals[paper_id] = gen_proposal
            except json.JSONDecodeError:
                print(f'Failed to parse line: {line}')
                continue

    # Cache for embeddings to avoid redundant computation
    embedding_cache = {}

    # Extend the references for each paper in the paper_data
    for paper_id, paper_info in paper_data.items():
        if 'references' not in paper_info['paper_data']:
            paper_info['paper_data']['references'] = []

        paper_title = paper_info['paper_data']['title']
        paper_abstract = paper_info['paper_data']['abstract']
        paper_text = f'{paper_title} {paper_abstract}'

        # Get embedding for the paper abstract
        if paper_abstract not in embedding_cache:
            embedding_cache[paper_abstract] = similarity_calculator.get_embedding(
                paper_text
            )
        paper_embedding = embedding_cache[paper_abstract]
        print(f'Processing paper ID: {paper_id}')

        # Find most similar proposal
        max_similarity = -1
        best_proposal = None

        for prop_id, proposal in proposals.items():
            if (
                prop_id == paper_id
                or prop_id.startswith(paper_id)
                or paper_id.startswith(prop_id)
            ):
                continue

            proposal_text = f'Generated Proposal {proposal}'
            # Get embedding for proposal_text
            if proposal_text not in embedding_cache:
                embedding_cache[proposal_text] = similarity_calculator.get_embedding(
                    proposal_text
                )
            proposal_embedding = embedding_cache[proposal_text]

            # Calculate similarity
            similarity = similarity_calculator.cosine_similarity(
                paper_embedding, proposal_embedding
            )

            if similarity > max_similarity:
                max_similarity = similarity
                best_proposal = proposal

        # Generate a new reference ID
        existing_ids = {
            ref.get('id', '')
            for ref in paper_info['paper_data'].get('references', [])
            if isinstance(ref, dict) and 'id' in ref
        }
        ref_id = 1
        while f'gen_ref_{ref_id}' in existing_ids:
            ref_id += 1

        # Use the most similar proposal or the paper's own proposal as fallback
        gen_proposal = (
            best_proposal
            if best_proposal
            else proposals.get(
                paper_id, 'No generated proposal available for this paper.'
            )
        )

        # Create a new reference with the generated proposal

        new_reference = {
            'title': 'Generated Proposal',
            'abstract': extract_qs_from_proposal(gen_proposal),
            'similarity': max_similarity,
        }

        # Add the new reference to the paper's references
        paper_info['paper_data']['references'].append(new_reference)

    # Save the updated JSON file
    with open('paper_bench_hard_500_filtered_1205_trim_extended.json', 'w') as f:
        json.dump(paper_data, f, indent=4)

    print(
        'References extended successfully. Output saved to paper_bench_hard_500_filtered_1205_trim_extended.json'
    )


if __name__ == '__main__':
    main()
