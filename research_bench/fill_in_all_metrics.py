import jsonlines
from research_bench.eval import compute_bertscore_per_question
from tqdm import tqdm
from multiprocessing import Pool

def process_file(file_path):
    try:
        # Open the file and load its data
        with jsonlines.open(file_path, 'r') as f:
            dataset = [line for line in f]

        # Process each data entry in the file
        for idx, data in enumerate(tqdm(dataset, desc=f"Processing {file_path}")):
            ref_proposal = data['ref_proposal']
            gen_proposal = data['gen_proposal']
            if 'bertscore_q1' not in data or 'bertscore_q2' not in data or 'bertscore_q3' not in data or 'bertscore_q4' not in data or 'bertscore_q5' not in data:
                bert_score_per_question = compute_bertscore_per_question(ref_proposal, gen_proposal)
                dataset[idx]['bertscore_q1'] = bert_score_per_question[0]
                dataset[idx]['bertscore_q2'] = bert_score_per_question[1]
                dataset[idx]['bertscore_q3'] = bert_score_per_question[2]
                dataset[idx]['bertscore_q4'] = bert_score_per_question[3]
                dataset[idx]['bertscore_q5'] = bert_score_per_question[4]

        # Write the updated data back to the file
        with jsonlines.open(file_path, 'w') as f:
            for data in dataset:
                f.write(data)
        print(f"Finished processing {file_path}")
    except Exception as e:
        print(f"Error processing {file_path}: {e}")

if __name__ == "__main__":
    # List of file paths to process
    file_paths = [
        './results/paper_bench_hard_500_result_4o_mini_fake_research_town.jsonl',
        './results/paper_bench_hard_500_result_4o_mini_citation_only.jsonl',
        './results/paper_bench_mid_500_result_4o_mini_fake_research_town.jsonl',
        './results/paper_bench_mid_500_result_4o_mini_citation_only.jsonl',
        './results/paper_bench_easy_500_result_4o_mini_fake_research_town.jsonl',
        './results/paper_bench_easy_500_result_4o_mini_citation_only.jsonl',
    ]

    # Create a pool of workers and process the files in parallel
    with Pool(processes=len(file_paths)) as pool:
        pool.map(process_file, file_paths)
