import json
import csv

# 读取 adversarial.json 文件
with open('./adversarial_prompts.json', 'r', encoding='utf-8') as f:
    adversarial_data = json.load(f)

# 读取 task.csv 文件并构建 task 到 domain 的映射
task_to_domain = {}
with open('./tasks.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        task = row['Task'].strip()  # 获取任务名称并去除多余空格
        domain = row['Scientific Domain'].strip()  # 获取对应的领域并去除多余空格
        task_to_domain[task] = domain

# 遍历 adversarial.json 数据并为每个 item 添加 domain
for item in adversarial_data:
    task = item['task'].strip()  # 获取 adversarial.json 中的 task
    if task in task_to_domain:  # 如果 task 在 task.csv 中存在
        item['domain'] = task_to_domain[task]  # 添加 domain 键

# 将更新后的数据写入新的 JSON 文件
with open('updated_adversarial.json', 'w', encoding='utf-8') as f:
    json.dump(adversarial_data, f, ensure_ascii=False, indent=4)

print("新的 JSON 文件已生成：updated_adversarial.json")