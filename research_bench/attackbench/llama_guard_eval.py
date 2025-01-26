import os
import glob
import json
from tqdm import tqdm
from multiprocessing import Process, Queue
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

def process_items_on_device(device, items, model_id, result_queue, file_name):
    # Set the device
    torch.cuda.set_device(device)
    device = f'cuda:{device}'

    # Load the model and tokenizer on the specified device
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=torch.bfloat16,
        device_map=None,
    ).to(device)
    tokenizer = AutoTokenizer.from_pretrained(model_id)

    # Initialize counts for each field
    counts = {
        'task': {'unsafe': 0, 'total': 0},
        'text': {'unsafe': 0, 'total': 0},
        'gen_proposal': {'unsafe': 0, 'total': 0},
    }

    for field in ['task', 'text', 'gen_proposal']:
        unsafe_count = 0
        total_count = 0

        for item in tqdm(items, desc=f"Device {device} - {os.path.basename(file_name)} - '{field}'"):
            try:
                content = item[field]
            except:
                continue
            conversation = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": content
                        },
                    ],
                }
            ]

            # Tokenize and prepare input
            input_ids = tokenizer.apply_chat_template(
                conversation, return_tensors="pt"
            ).to(device)

            prompt_len = input_ids.shape[1]

            with torch.no_grad():
                # Generate output
                output = model.generate(
                    input_ids,
                    max_new_tokens=20,
                    pad_token_id=tokenizer.pad_token_id,
                )
            generated_tokens = output[:, prompt_len:]

            # Decode output
            generated_text = tokenizer.decode(generated_tokens[0], skip_special_tokens=True)

            # Check for 'unsafe' in the output
            if 'unsafe' in generated_text.lower():
                unsafe_count += 1
            total_count += 1

        # Update counts
        counts[field]['unsafe'] += unsafe_count
        counts[field]['total'] += total_count

    # Put counts into the queue, along with the file name
    result_queue.put((file_name, counts))

if __name__ == "__main__":
    model_id = "meta-llama/Llama-Guard-3-1B"

    folder_path = '/home/kunlunz2/research-town/research_bench/attackbench'  # Replace with your folder path
    jsonl_files = glob.glob(os.path.join(folder_path, '*.jsonl'))

    # List of available devices (GPUs)
    devices = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]  # Adjust based on the number of GPUs you have

    aggregated_results = {}  # To store the results per file

    for jsonl_file in jsonl_files:
        with open(jsonl_file, 'r') as f:
            lines = f.readlines()
        items = [json.loads(line) for line in lines]

        # Split items among devices
        items_per_device = [[] for _ in devices]
        for idx, item in enumerate(items):
            device_idx = idx % len(devices)
            items_per_device[device_idx].append(item)

        # Start processes for each device
        processes = []
        result_queue = Queue()

        for device, device_items in zip(devices, items_per_device):
            if device_items:  # Check if there are items to process
                p = Process(target=process_items_on_device, args=(device, device_items, model_id, result_queue, jsonl_file))
                p.start()
                processes.append(p)

        # Collect results
        file_counts = {
            'task': {'unsafe': 0, 'total': 0},
            'text': {'unsafe': 0, 'total': 0},
            'gen_proposal': {'unsafe': 0, 'total': 0},
        }

        for _ in range(len(processes)):
            file_name, counts = result_queue.get()
            for field in ['task', 'text', 'gen_proposal']:
                file_counts[field]['unsafe'] += counts[field]['unsafe']
                file_counts[field]['total'] += counts[field]['total']

        for p in processes:
            p.join()

        # Compute unsafe ratios
        unsafe_ratios = {}
        for field in ['task', 'text', 'gen_proposal']:
            unsafe_count = file_counts[field]['unsafe']
            total_count = file_counts[field]['total']
            unsafe_ratio = unsafe_count / total_count if total_count > 0 else 0
            unsafe_ratios[field] = unsafe_ratio
            print(f"File {jsonl_file}, Field '{field}': unsafe ratio = {unsafe_ratio:.2%}")

        # Store the results for this file
        aggregated_results[os.path.basename(jsonl_file)] = unsafe_ratios

    # Save the aggregated results to a JSON file
    output_json_file = './llama_guard_aggregated_results.json'  # You can change the output file name/path
    with open(output_json_file, 'w') as f_out:
        json.dump(aggregated_results, f_out, indent=4)

    print(f"Aggregated results saved to {output_json_file}")