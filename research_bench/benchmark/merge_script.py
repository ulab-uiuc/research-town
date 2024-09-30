import json
from collections import defaultdict

def load_json(file_path):
    """加载JSON文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(data, file_path):
    """保存JSON文件"""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def merge_json(file1, file2, output_file, max_entries=100):
    # 加载第一个JSON文件
    data1 = load_json(file1)
    # 加载第二个JSON文件
    data2 = load_json(file2)
    
    # 记录初始键的集合
    keys1 = set(data1.keys())
    
    # 开始合并
    merged_data = data1.copy()
    for key, value in data2.items():
        if key not in keys1:
            merged_data[key] = value
            keys1.add(key)
            # 检查是否达到最大条目数
            if len(merged_data) >= max_entries:
                break
    
    # 如果合并后总条目数超过最大值，截取前max_entries条
    if len(merged_data) > max_entries:
        merged_data = dict(list(merged_data.items())[:max_entries])
    
    # 保存合并后的JSON
    save_json(merged_data, output_file)
    
    # 统计关键词
    keyword_counts = defaultdict(int)
    for item in merged_data.values():
        keyword = item.get('keyword', '').strip()
        if keyword:
            keyword_counts[keyword] += 1
    
    # 打印关键词统计
    print("关键词统计如下：")
    for keyword, count in keyword_counts.items():
        print(f"{keyword}: {count} 项")

if __name__ == "__main__":
    file1 = './benchmark.json'       # 第一个JSON文件路径
    file2 = './benchmark_0930_2.json'       # 第二个JSON文件路径
    output_file = './benchmark_merged.json'  # 输出的合并后的JSON文件路径
    max_entries = 100          # 合并后的最大条目数
    
    merge_json(file1, file2, output_file, max_entries)