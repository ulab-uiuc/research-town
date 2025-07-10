import json

files = [
    "paper_bench_easy_500_filtered_1205.json",
    "paper_bench_mid_500_filtered_1205.json",
    "paper_bench_hard_500_filtered_1205.json"
]

target_file_data = {}

for file in files:
    with open(file, 'r') as f:
        data = json.load(f)
        for key, value in data.items():
            if key not in target_file_data:
                target_file_data[key] = value
            else:
                raise ValueError(f"Duplicate key found: {key} in file {file}")
            
# Assert that the target file data has 1000 entries
assert len(target_file_data) == 1000, f"Expected 1000 entries, found {len(target_file_data)}"

# Write the combined data to a new JSON file
with open("paper_bench_full_1000_filtered_1205.json", 'w') as f:
    json.dump(target_file_data, f, indent=4)
print("Successfully combined the JSON files into paper_bench_full_1000_filtered_1205.json")