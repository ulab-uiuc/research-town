import os
import json
import argparse
import glob
from statistics import mean

def compute_averages(file_path):
    bleu_scores = []
    rouge_l_scores = []
    gpt_scores = []
    bert_scores = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line_number, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue  # 跳过空行
            try:
                data = json.loads(line)
                bleu = data.get('bleu')
                rouge_l = data.get('rouge_l')
                gpt_score = data.get('gpt_metric_score')
                bert_score = data.get('bert_score')
                
                # 确保所有指标都存在且为数值类型
                if all(isinstance(value, (int, float)) for value in [bleu, rouge_l, gpt_score, bert_score]):
                    bleu_scores.append(bleu)
                    rouge_l_scores.append(rouge_l)
                    gpt_scores.append(gpt_score)
                    bert_scores.append(bert_score)
                else:
                    print(f"警告: 文件 {file_path} 第 {line_number} 行的某些指标缺失或类型不正确，已跳过该行。")
            except json.JSONDecodeError as e:
                print(f"错误: 无法解析文件 {file_path} 第 {line_number} 行的JSON。错误信息: {e}")
    
    if bleu_scores:
        return {
            'Avg BLEU': mean(bleu_scores),
            'Avg ROUGE_L': mean(rouge_l_scores),
            'Avg GPT Score': mean(gpt_scores),
            'Avg BERT Score': mean(bert_scores)
        }
    else:
        return {
            'Avg BLEU': None,
            'Avg ROUGE_L': None,
            'Avg GPT Score': None,
            'Avg BERT Score': None
        }

def main(folder_path):
    # 查找所有.jsonl文件
    pattern = os.path.join(folder_path, '*.jsonl')
    files = glob.glob(pattern)
    
    if not files:
        print(f"在文件夹 '{folder_path}' 中未找到任何.jsonl文件。")
        return
    
    # 打印表头
    header = f"{'Filename':<50} | {'Avg BLEU':>10} | {'Avg ROUGE_L':>12} | {'Avg GPT Score':>14} | {'Avg BERT Score':>15}"
    separator = "-" * len(header)
    print(header)
    print(separator)
    
    for file_path in files:
        averages = compute_averages(file_path)
        filename = os.path.basename(file_path)
        avg_bleu = f"{averages['Avg BLEU']:.4f}" if averages['Avg BLEU'] is not None else "N/A"
        avg_rouge_l = f"{averages['Avg ROUGE_L']:.4f}" if averages['Avg ROUGE_L'] is not None else "N/A"
        avg_gpt = f"{averages['Avg GPT Score']:.4f}" if averages['Avg GPT Score'] is not None else "N/A"
        avg_bert = f"{averages['Avg BERT Score']:.4f}" if averages['Avg BERT Score'] is not None else "N/A"
        
        print(f"{filename:<50} | {avg_bleu:>10} | {avg_rouge_l:>12} | {avg_gpt:>14} | {avg_bert:>15}")

if __name__ == "__main__":

    folder_path = "./results_combine/interdisplinary_compute"
    
    if not os.path.isdir(folder_path):
        print(f"错误: '{folder_path}' 不是一个有效的文件夹路径。")
    else:
        main(folder_path)