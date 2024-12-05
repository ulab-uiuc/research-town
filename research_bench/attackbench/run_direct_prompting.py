import os
import argparse
import json
from concurrent.futures import ProcessPoolExecutor, as_completed
from tqdm import tqdm
from research_town.utils.model_prompting import model_prompting

def main():
    parser = argparse.ArgumentParser(description='Process a JSONL file and evaluate task and text.')
    parser.add_argument(
        '--input_file', 
        type=str, 
        default='/home/kunlunz2/research-town/research_bench/attackbench/ethical_result_attacker_agent.jsonl', 
        required=False, 
        help='Input JSONL file path'
    )
    parser.add_argument(
        '--output_file', 
        type=str, 
        default='/home/kunlunz2/research-town/research_bench/attackbench/direct_prompting_result.jsonl', 
        required=False, 
        help='Output JSONL file path'
    )
    parser.add_argument('--num_workers', type=int, default=10, help='Number of parallel workers')
    args = parser.parse_args()

    input_file = args.input_file
    output_file = args.output_file
    num_workers = args.num_workers

    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # Load processed IDs if output file exists
    processed_ids = set()
    if os.path.exists(output_file):
        processed_ids = load_processed_ids(output_file)

    process_file(input_file, output_file, processed_ids, num_workers)

def load_processed_ids(output_file_path: str) -> set:
    processed_ids = set()
    with open(output_file_path, 'r', encoding='utf-8') as f:
        for line in f:
            item = json.loads(line)
            attack_id = item.get('attack_id')
            if attack_id:
                processed_ids.add(attack_id)
    return processed_ids

def process_file(input_file_path: str, output_file_path: str, processed_ids: set, num_workers: int):
    with open(input_file_path, 'r', encoding='utf-8') as f:
        input_items = [json.loads(line) for line in f]

    items_to_process = [item for item in input_items if item.get('attack_id') not in processed_ids]

    if not items_to_process:
        print(f"All items in {input_file_path} have been processed.")
        return

    with open(output_file_path, 'a', encoding='utf-8') as output_file:
        with ProcessPoolExecutor(max_workers=num_workers) as executor:
            futures = {executor.submit(process_item, item): item for item in items_to_process}

            for future in tqdm(as_completed(futures), total=len(futures), desc=f'Processing items in {input_file_path}'):
                item = futures[future]
                try:
                    result_item = future.result()
                    output_file.write(json.dumps(result_item, ensure_ascii=False) + '\n')
                except Exception as e:
                    print(f"Error processing item {item.get('attack_id')}: {e}")

def process_item(item: dict) -> dict:
    task_result = model_prompting_task(item['task'])
    text_result = model_prompting_text(item['text'])

    item['task_result'] = task_result
    item['text_result'] = text_result
    item.pop('gen_proposal', None)  # Remove gen_proposal

    return item

def model_prompting_task(task: str) -> str:
    prompt = [
        {
            'role': 'user',
            'content': f"Run the following task:{task}"
        }
    ]
    response = model_prompting('gpt-4o-mini', prompt, temperature=0.0)
    return response[0] if response else ""

def model_prompting_text(text: str) -> str:
    prompt = [
        {
            'role': 'user',
            'content': f"Run the following task:{text}"
        }
    ]
    response = model_prompting('gpt-4o-mini', prompt, temperature=0.0)
    return response[0] if response else ""

if __name__ == '__main__':
    main()