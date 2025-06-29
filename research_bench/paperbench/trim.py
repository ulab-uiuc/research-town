import json
import argparse

def trim_json(a_file, b_file, output_file):
    # Load the JSON data from both files
    with open(a_file, 'r') as f:
        a_data = json.load(f)
    
    with open(b_file, 'r') as f:
        b_data = json.load(f)
    
    # Find common keys
    a_keys = list(a_data.keys())
    b_keys = list(b_data.keys())
    
    
    trimmed_b_data = {key: b_data[key] for key in b_keys if key in a_keys}
    
    # Save the trimmed data to a new JSON file
    with open(output_file, 'w') as f:
        json.dump(trimmed_b_data, f, indent=4)

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Trim b.json by keys present in a.json.")
    parser.add_argument('--a', type=str, default="paper_bench_hard_500_filtered_1205_extended_with_reviewers.json", help="Path to file a.")
    parser.add_argument('--b', type=str, default="paper_bench_hard_500_filtered_1205.json", help="Path to file b.")
    parser.add_argument('--output', type=str, help="Output file name (optional).")
    
    args = parser.parse_args()

    # Default output filename if not provided
    if not args.output:
        output_file = f"{args.b.split('.')[0]}_trim.json"
    else:
        output_file = args.output

    # Trim the JSON files
    trim_json(args.a, args.b, output_file)
    print(f"Trimmed JSON saved to {output_file}")

if __name__ == '__main__':
    main()
