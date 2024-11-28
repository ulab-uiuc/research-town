import json
import re
from typing import List
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
from research_town.utils.model_prompting import model_prompting
from threading import Lock
import os

def extract_and_clean_question_content(text: str, question_prompts: List[str]) -> List[str]:
    question_contents = []
    for i, prompt in enumerate(question_prompts):
        start = text.find(prompt)
        end = (
            text.find(question_prompts[i + 1])
            if i + 1 < len(question_prompts)
            else len(text)
        )

        if start != -1:
            content = text[start + len(prompt) : end].strip()
            content = re.sub(r'[\*\#]+', '', content).strip()
            content = content.split('\n', 1)[0].strip()
            question_contents.append(content)
        else:
            question_contents.append('')
    return question_contents

def compute_proposal_gpt_metric(reference: str, generation: str, question_num: int) -> float:
    prompt = [
        {
            'role': 'user',
            'content': (
                f'Evaluate the alignment between the following two question responses (Question {question_num}):\n\n'
                f'Reference: {reference}\n\n'
                f'Generated: {generation}\n\n'
                'Scoring Guidelines:\n'
                '1: Very low alignment - Responses have completely different focuses.\n'
                '2: Low alignment - Responses have some overlaps, but largely differ in focus.\n'
                '3: Moderate alignment - Some commonalities, but significant differences exist.\n'
                '4: High alignment - Mostly aligned, with minor differences.\n'
                '5: Very high alignment - Fully aligned in terms of focus and content.\n\n'
                'Based on the above scoring criteria, please provide a similarity score between 1 and 5: Only output the score without any additional information.'
            ),
        }
    ]
    response = model_prompting('gpt-4o', prompt, temperature=0.0)[0]
    score = float(response.strip())
    return max(0.0, min(5, score))

def process_item(item: dict, questions: List[str], outfile, lock: Lock) -> None:
    ref_questions = extract_and_clean_question_content(item['ref_proposal'], questions)
    hyp_questions = extract_and_clean_question_content(item['gen_proposal'], questions)

    # Calculating scores for each question
    scores = []
    for i in range(5):
        score = compute_proposal_gpt_metric(ref_questions[i], hyp_questions[i], i + 1)
        item[f'q{i + 1}_gpt_score'] = score
        scores.append(score)

    # Calculating average of all question scores
    gpt_score_average = sum(scores) / len(scores)
    item['gpt_score_average'] = gpt_score_average

    # Write updated item to output file with lock to prevent race conditions
    with lock:
        outfile.write(json.dumps(item) + '\n')

def parse_jsonl_files(input_folder: str, output_folder: str):
    questions = [
        'What is the problem?',
        'Why is it interesting and important?',
        'Why is it hard?',
        "Why hasn't it been solved before?",
        'What are the key components of my approach and results?',
    ]

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    input_files = [f for f in os.listdir(input_folder) if f.endswith('.jsonl')]

    for input_file in input_files:
        input_file_path = os.path.join(input_folder, input_file)
        output_file_path = os.path.join(output_folder, input_file)

        with open(input_file_path, 'r') as infile, open(output_file_path, 'w') as outfile:
            items = [json.loads(line) for line in infile]

            q1_total, q2_total, q3_total, q4_total, q5_total = 0, 0, 0, 0, 0
            item_count = len(items)
            lock = Lock()

            with ThreadPoolExecutor(max_workers=4) as executor:
                list(tqdm(executor.map(lambda item: process_item(item, questions, outfile, lock), items), total=item_count))

            # Printing average of each question and the total average
            for item in items:
                q1_total += item['q1_gpt_score']
                q2_total += item['q2_gpt_score']
                q3_total += item['q3_gpt_score']
                q4_total += item['q4_gpt_score']
                q5_total += item['q5_gpt_score']

            print(f'Processed file: {input_file}')
            print(f'Q1 Average Score: {q1_total / item_count}')
            print(f'Q2 Average Score: {q2_total / item_count}')
            print(f'Q3 Average Score: {q3_total / item_count}')
            print(f'Q4 Average Score: {q4_total / item_count}')
            print(f'Q5 Average Score: {q5_total / item_count}')
            overall_average = (0.1 * q1_total + 0.1 * q2_total + 0.1 * q3_total + 0.1 * q4_total + 0.6 * q5_total) /  item_count
            print(f'Overall Average Score: {overall_average}')

def main():
    input_folder = '/Users/zhukunlun/Documents/GitHub/research-town/research_bench/result_data/sakana'
    output_folder = '/Users/zhukunlun/Documents/GitHub/research-town/research_bench/result_data_gptscore/'
    os.makedirs(output_folder, exist_ok=True)
    parse_jsonl_files(input_folder, output_folder)

# Example usage:
if __name__ == "__main__":
    main()
