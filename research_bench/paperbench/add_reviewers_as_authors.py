import argparse
import json
import os
from typing import Any, Dict, Tuple


def load_json_file(file_path: str) -> Dict[str, Any]:
    """
    Load JSON data from file.

    Args:
        file_path: Path to the JSON file

    Returns:
        Dictionary containing the JSON data
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data


def save_json_file(data: Dict[str, Any], file_path: str) -> None:
    """
    Save JSON data to file.

    Args:
        data: Dictionary to save
        file_path: Path where the JSON will be saved
    """
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)


def extend_paper_data(
    base_file: str, aux_file: str, output_file: str
) -> Tuple[int, int]:
    """
    Extend paper data with reviewer information from auxiliary file.

    Args:
        base_file: Path to the base JSON file (paper_bench_hard_500_filtered_1205_extended.json)
        aux_file: Path to the auxiliary JSON file (iclrbench_reviewers_filtered_bullets.json)
        output_file: Path to save the extended data

    Returns:
        Tuple of (processed_count, skipped_count)
    """
    # Load data from both files
    base_data = load_json_file(base_file)
    aux_data = load_json_file(aux_file)

    processed_count = 0
    skipped_count = 0

    # Create a new dictionary for the result
    # This helps preserve the original structure and key order
    extended_data = {}

    # Process each paper in the base data
    for paper_id, paper_info in base_data.items():
        # Check if the paper_id exists in the auxiliary data
        if paper_id in aux_data:
            # Copy the paper info from base data
            extended_data[paper_id] = paper_info.copy()

            # Initialize author_data if it doesn't exist
            if 'author_data' not in extended_data[paper_id]:
                extended_data[paper_id]['author_data'] = {}

            # Copy reviewer_data to author_data
            if 'reviewer_data' in aux_data[paper_id]:
                reviewer_data = aux_data[paper_id]['reviewer_data']
                extended_data[paper_id]['author_data'].update(reviewer_data)

                # Add reviewer names to authors list
                for reviewer_id, reviewer_info in reviewer_data.items():
                    if 'name' in reviewer_info and reviewer_info['name']:
                        if 'paper_data' not in extended_data[paper_id]:
                            extended_data[paper_id]['paper_data'] = {}

                        if 'authors' not in extended_data[paper_id]['paper_data']:
                            extended_data[paper_id]['paper_data']['authors'] = []

                        extended_data[paper_id]['paper_data']['authors'].append(
                            reviewer_info['name']
                        )

            processed_count += 1
        else:
            # Keep the original data for papers not in the auxiliary file
            # extended_data[paper_id] = base_data[paper_id]
            # drop that entry instead  # Ensure we do not include the original entry in the output
            extended_data.pop(
                paper_id, None
            )  # Remove the entry from the extended data if it doesn't exist in aux_data
            skipped_count += 1

    # Save the extended data
    save_json_file(extended_data, output_file)

    return processed_count, skipped_count


def main():
    """Main function to run the paper data extension script."""
    parser = argparse.ArgumentParser(
        description='Extend paper data with reviewer information'
    )
    parser.add_argument(
        '--base_file',
        help='Path to base JSON file',
        default='paper_bench_hard_500_filtered_1205_extended.json',
    )
    parser.add_argument(
        '--aux_file',
        help='Path to auxiliary JSON file with reviewer data',
        default='iclrbench_reviewers_filtered_bullets.json',
    )
    parser.add_argument('--output_file', help='Path to save the output JSON file')

    args = parser.parse_args()

    # Set output file path if not provided
    if not args.output_file:
        base_filename, ext = os.path.splitext(args.base_file)
        args.output_file = f'{base_filename}_with_reviewers{ext}'

    # Extend paper data
    processed, skipped = extend_paper_data(
        args.base_file, args.aux_file, args.output_file
    )

    print('Extension complete!')
    print(f'Processed papers: {processed}')
    print(f'Skipped papers (key not in aux file): {skipped}')
    print(f'Output saved to: {args.output_file}')


if __name__ == '__main__':
    main()
