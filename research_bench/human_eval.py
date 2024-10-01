import json
import csv
import random

def merge_and_randomize_jsonl(file_path1, file_path2, output_csv):
    # Define dictionaries to store data from each file
    data1 = {}
    data2 = {}

    # Read the first file and store relevant data
    with open(file_path1, 'r', encoding='utf-8') as file:
        for line in file:
            item = json.loads(line)
            paper_key = item['paper_key']
            data1[paper_key] = {
                'current_5q': item['current_5q'],
                'proposal_5q': item['proposal_5q']
            }

    # Read the second file and store relevant data
    with open(file_path2, 'r', encoding='utf-8') as file:
        for line in file:
            item = json.loads(line)
            paper_key = item['paper_key']
            data2[paper_key] = {
                'proposal_5q': item['proposal_5q']
            }

    # Open a CSV file to write the merged and randomized data
    with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        # Write the header
        writer.writerow(['paper_key', 'current_5q', 'proposal_5q_0', 'source_5q_0', 'proposal_5q_1', 'source_5q_1'])

        # Merge data based on paper_key and write to CSV
        for paper_key in data1:
            if paper_key in data2:
                proposals = [
                    (data1[paper_key]['proposal_5q'], '0'),
                    (data2[paper_key]['proposal_5q'], '1')
                ]
                random.shuffle(proposals)

                writer.writerow([
                    paper_key,
                    data1[paper_key]['current_5q'],
                    proposals[0][0],
                    proposals[0][1],
                    proposals[1][0],
                    proposals[1][1]
                ])


merge_and_randomize_jsonl('./results/research_bench_result_normal.jsonl', './results/research_bench_result_single_agent.jsonl', './human_eval.csv')