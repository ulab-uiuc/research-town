import csv
import json

with open('./adversarial_prompts.json', 'r', encoding='utf-8') as f:
    adversarial_data = json.load(f)

task_to_domain = {}
with open('./tasks.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        task = row['Task'].strip()
        domain = row['Scientific Domain'].strip()  
        task_to_domain[task] = domain

for item in adversarial_data:
    task = item['task'].strip()
    if task in task_to_domain: 
        item['domain'] = task_to_domain[task] 

with open('updated_adversarial.json', 'w', encoding='utf-8') as f:
    json.dump(adversarial_data, f, ensure_ascii=False, indent=4)

