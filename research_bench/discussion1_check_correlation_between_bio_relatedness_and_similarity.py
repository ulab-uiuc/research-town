import json
import jsonlines
import numpy as np


def load_json(filepath):
    """
    Load a JSON file.
    """
    with open(filepath, 'r') as f:
        return json.load(f)


def load_jsonlines(filepath):
    """
    Load a JSONL file and return a list of records.
    """
    with jsonlines.open(filepath, 'r') as f:
        return [line for line in f]


def calculate_mean_scores(results, prefix, num_questions=5):
    """
    Calculate mean scores for each paper ID based on given results.
    """
    sim_dict = {}
    for result in results:
        sim_dict[result['paper_id']] = np.mean(
            [result[f'{prefix}_sim_q{i}'] for i in range(1, num_questions + 1)]
        )
    return sim_dict

if __name__ == '__main__':
    # Load datasets
    dataset = load_json('./paper_bench/agent_number_ablation_paper_bench_with_relatedness.json')
    
    first_author_results = load_jsonlines(
        './results/agent_number_ablation_record_each_agent_output_paper_bench_first_author_result_4o_mini_fake_research_town.jsonl'
    )
    second_author_results = load_jsonlines(
        './results/agent_number_ablation_record_each_agent_output_paper_bench_second_author_result_4o_mini_fake_research_town.jsonl'
    )
    third_author_results = load_jsonlines(
        './results/agent_number_ablation_record_each_agent_output_paper_bench_third_author_result_4o_mini_fake_research_town.jsonl'
    )
    fourth_author_results = load_jsonlines(
        './results/agent_number_ablation_record_each_agent_output_paper_bench_fourth_author_result_4o_mini_fake_research_town.jsonl'
    )
    fifth_author_results = load_jsonlines(
        './results/agent_number_ablation_record_each_agent_output_paper_bench_fifth_author_result_4o_mini_fake_research_town.jsonl'
    )

    # Calculate similarity scores for first author
    first_author_openai_sim_dict = calculate_mean_scores(first_author_results, 'openai')
    first_author_voyageai_sim_dict = calculate_mean_scores(first_author_results, 'voyageai')

    # Example: Process other authors' results if needed
    second_author_openai_sim_dict = calculate_mean_scores(second_author_results, 'openai')
    second_author_voyageai_sim_dict = calculate_mean_scores(second_author_results, 'voyageai')

    third_author_openai_sim_dict = calculate_mean_scores(third_author_results, 'openai')
    third_author_voyageai_sim_dict = calculate_mean_scores(third_author_results, 'voyageai')

    fourth_author_openai_sim_dict = calculate_mean_scores(fourth_author_results, 'openai')
    fourth_author_voyageai_sim_dict = calculate_mean_scores(fourth_author_results, 'voyageai')

    fifth_author_openai_sim_dict = calculate_mean_scores(fifth_author_results, 'openai')
    fifth_author_voyageai_sim_dict = calculate_mean_scores(fifth_author_results, 'voyageai')

    import numpy as np
    from scipy.stats import pearsonr

    all_bio = []
    all_openai = []
    all_voyageai = []

    for paper_id, data in dataset.items():
        author_data = data['author_data']
        # Extract bio-relatedness from first five authors
        bio_relatedness = [author_info['bio_relatedness_with_abstract'] for author_info in author_data.values()][:5]
        
        # Extract similarity scores for the same five authors
        openai_sims = [
            first_author_openai_sim_dict[paper_id],
            second_author_openai_sim_dict[paper_id],
            third_author_openai_sim_dict[paper_id],
            fourth_author_openai_sim_dict[paper_id],
            fifth_author_openai_sim_dict[paper_id]
        ]

        voyageai_sims = [
            first_author_voyageai_sim_dict[paper_id],
            second_author_voyageai_sim_dict[paper_id],
            third_author_voyageai_sim_dict[paper_id],
            fourth_author_voyageai_sim_dict[paper_id],
            fifth_author_voyageai_sim_dict[paper_id]
        ]

        bio_array = np.array(bio_relatedness)
        openai_array = np.array(openai_sims)
        voyageai_array = np.array(voyageai_sims)

        # if bio array has one much higher than the rest, calculate
        # correlation between the two lower ones
        sorted_bio_array = np.sort(bio_array)
        if sorted_bio_array[-1] - sorted_bio_array[-2] < 0.1:
            continue


        # Compute Pearson correlation coefficients
        bio_openai_corr, bio_openai_p = pearsonr(bio_array, openai_array)
        bio_voyageai_corr, bio_voyageai_p = pearsonr(bio_array, voyageai_array)
        openai_voyageai_corr, openai_voyageai_p = pearsonr(openai_array, voyageai_array)

        print(f"Paper ID: {paper_id}")
        print(f"Bio vs OpenAI: Correlation={bio_openai_corr:.3f}, p-value={bio_openai_p:.3f}")
        print(f"Bio vs VoyageAI: Correlation={bio_voyageai_corr:.3f}, p-value={bio_voyageai_p:.3f}")
        print(f"OpenAI vs VoyageAI: Correlation={openai_voyageai_corr:.3f}, p-value={openai_voyageai_p:.3f}\n")

        print(bio_array)
        print(openai_array)
        print(voyageai_array)
        print('\n\n')

# average bio_relatedness and similarity scores for each paper
