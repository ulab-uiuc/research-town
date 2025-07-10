import json
import argparse
import os
import requests
import time
from typing import Dict, List, Any, Optional, Tuple
import numpy as np

# You'll need these installed:
# pip install voyageai arxiv

import voyageai
import arxiv

class ArxivReferenceExtender:
    def __init__(self, voyage_api_key: str, max_references: int = 10):
        """
        Initialize the reference extender with API keys and configuration.
        
        Args:
            voyage_api_key: API key for Voyage AI embeddings
            max_references: Maximum number of references to add (default: 10)
        """
        self.voyage_client = voyageai.Client(api_key=voyage_api_key)
        self.max_references = max_references
        
    def load_paper_data(self, filepath: str) -> Dict[str, Any]:
        """
        Load paper data from JSON file.
        
        Args:
            filepath: Path to the JSON file containing paper data
            
        Returns:
            Dictionary containing the paper data
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    
    def save_paper_data(self, data: Dict[str, Any], output_path: str) -> None:
        """
        Save updated paper data to JSON file.
        
        Args:
            data: Updated paper data dictionary
            output_path: Path where the updated JSON will be saved
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        
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
                text,
                model="voyage-large-2",
                input_type="document"
            )
            return response.embeddings[0]
        except Exception as e:
            print(f"Error getting embedding: {e}")
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
    
    def search_arxiv(self, query: str, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Search arXiv for papers related to the query.
        
        Args:
            query: Search query
            max_results: Maximum number of results to retrieve
            
        Returns:
            List of dictionaries containing paper information
        """
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance
        )
        
        results = []
        for paper in search.results():
            results.append({
                "title": paper.title,
                "abstract": paper.summary,
                "authors": [author.name for author in paper.authors],
                "arxiv_id": paper.entry_id.split('/')[-1],
                "url": paper.entry_id
            })
            
        return results
    
    def find_similar_papers(self, paper_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Find papers similar to the given paper using embeddings.
        
        Args:
            paper_data: Dictionary containing paper data
            
        Returns:
            List of similar papers
        """
        # Extract source paper information
        arxiv_id = list(paper_data.keys())[0]
        paper_info = paper_data[arxiv_id]["paper_data"]
        
        # Create search queries based on title and abstract
        title = paper_info["title"]
        abstract = paper_info["abstract"]
        combined_query = f"{title} {abstract}"
        
        # Get embedding for the source paper
        source_embedding = self.get_embedding(combined_query)
        print(f"Processing paper ID: {arxiv_id}")
        
        # Search arXiv for related papers
        search_results = self.search_arxiv(title, max_results=50)
        
        # Get embeddings for search results and calculate similarity
        papers_with_similarity = []
        for paper in search_results:
            # Skip the original paper if it appears in search results
            if paper["arxiv_id"] == arxiv_id:
                continue
                
            # if one id is the beginning of the other, skip it to avoid self-comparison
            if arxiv_id.startswith(paper["arxiv_id"]) or paper["arxiv_id"].startswith(arxiv_id):
                # Skip self-comparison or prefix matches to avoid redundancy
                continue
            # this is to skip all 'v2' or 'v3' papers
                
            paper_text = f"{paper['title']} {paper['abstract']}"
            paper_embedding = self.get_embedding(paper_text)
            similarity = self.cosine_similarity(source_embedding, paper_embedding)
            
            paper["similarity"] = similarity
            papers_with_similarity.append(paper)
            
            # Add a small delay to avoid rate limits
            time.sleep(0.5)
        
        # Sort by similarity and get top results
        similar_papers = sorted(papers_with_similarity, key=lambda x: x["similarity"], reverse=True)
        return similar_papers[:self.max_references]
    
    def extend_references(self, paper_data: Dict[str, Any], similar_papers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Extend the references section with similar papers.
        
        Args:
            paper_data: Original paper data
            similar_papers: List of similar papers to add as references
            
        Returns:
            Updated paper data with extended references
        """
        # Create a deep copy to avoid modifying the original
        # updated_data = json.loads(json.dumps(paper_data))
        import copy
        updated_data = copy.deepcopy(paper_data)
        
        # Get the first key (arxiv_id)
        # arxiv_id = list(updated_data.keys())[0]
        for arxiv_id in updated_data.keys():

            print(f"Adding references to paper ID: {arxiv_id}")
            
            # Check if references already exist, if not create an empty list
            if "references" not in updated_data[arxiv_id]["paper_data"]:
                updated_data[arxiv_id]["paper_data"]["references"] = []
            
            # Add similar papers to references
            for paper in similar_papers:
                new_reference = {
                    "title": paper["title"],
                    "abstract": paper["abstract"],
                    "authors": paper["authors"],
                    "arxiv_id": paper["arxiv_id"],
                    "url": paper["url"],
                    "similarity_score": paper["similarity"]
                }
                updated_data[arxiv_id]["paper_data"]["references"].append(new_reference)
        
        return updated_data
    
    def process_file(self, input_file: str, output_file: str) -> None:
        """
        Process a paper file to extend references.
        
        Args:
            input_file: Path to the input JSON file
            output_file: Path to save the output JSON file
        """
        # Load data
        paper_data = self.load_paper_data(input_file)
        
        # Find similar papers
        similar_papers = self.find_similar_papers(paper_data)
        
        # Extend references
        updated_data = self.extend_references(paper_data, similar_papers)
        
        # Save updated data
        self.save_paper_data(updated_data, output_file)
        
        print(f"Added {len(similar_papers)} references to {output_file}")


def main():
    """Main function to run the reference extender from command line."""
    parser = argparse.ArgumentParser(description="Extend arXiv paper references using Voyage AI embeddings")
    parser.add_argument("--input_file", help="Path to input JSON file containing paper data", default="paper_bench_hard_500_filtered_1205.json")
    parser.add_argument("--output_file", help="Path to save the output JSON file (default: input_file with '_extended' suffix)")
    parser.add_argument("--voyage_api_key", help="Voyage AI API key")
    parser.add_argument("--max_refs", type=int, default=10, help="Maximum number of references to add (default: 10)")
    
    args = parser.parse_args()
    
    # Set output file path if not provided
    if not args.output_file:
        filename, ext = os.path.splitext(args.input_file)
        args.output_file = f"{filename}_extended{ext}"
    
    # Get API key from arguments or environment variable
    voyage_api_key = args.voyage_api_key or os.environ.get("VOYAGE_API_KEY")
    if not voyage_api_key:
        raise ValueError("Voyage AI API key must be provided via --voyage_api_key argument or VOYAGE_API_KEY environment variable")
    
    # Initialize and run the reference extender
    extender = ArxivReferenceExtender(
        voyage_api_key=voyage_api_key,
        max_references=args.max_refs
    )
    
    extender.process_file(args.input_file, args.output_file)
    

if __name__ == "__main__":
    main()