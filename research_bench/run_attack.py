import argparse
import json
import os
from typing import Any, Dict
from concurrent.futures import ProcessPoolExecutor, as_completed

from tqdm import tqdm

from research_bench.proposal_writing import write_proposal
from research_town.configs import Config
from research_town.data import Profile
from research_town.utils.logger import logger


def load_adversarial_data(
    adversarial_path: str, output_path: str
) -> Dict[str, Dict[str, Any]]:
    """
    Load adversarial data from a JSON file and skip already processed entries based on the output_path.
    Assign a unique attack_id to each entry.

    :param adversarial_path: Path to adversarial.json
    :param output_path: Path to existing output JSONL file
    :return: Dictionary mapping attack_id to data
    """
    with open(adversarial_path, 'r', encoding='utf-8') as f:
        adversarial_list = json.load(f)

    # Assign unique attack_id, e.g., "attack_0", "attack_1", ...
    dataset = {f'attack_{idx}': entry for idx, entry in enumerate(adversarial_list)}

    if os.path.exists(output_path):
        with open(output_path, 'r', encoding='utf-8') as f:
            processed_ids = {json.loads(line)['attack_id'] for line in f}
        dataset = {k: v for k, v in dataset.items() if k not in processed_ids}

    return dataset


def load_profiles(profile_path: str) -> Dict[str, Any]:
    """
    Load profiles from profile.json.

    :param profile_path: Path to profile.json
    :return: Dictionary mapping domain to scientists' profiles
    """
    with open(profile_path, 'r', encoding='utf-8') as f:
        profiles: Dict[str, Any] = json.load(f)
    return profiles


def save_result(result: Dict[str, Any], output_path: str) -> None:
    """
    Append a single JSON object to the output JSONL file.

    :param result: Result dictionary to save
    :param output_path: Path to the output JSONL file
    """
    with open(output_path, 'a', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False)
        f.write('\n')


def process_attack(attack_id: str, data: Dict[str, Any], profiles_dict: Dict[str, Any], config: Config, mode: str) -> Dict[str, Any]:
    template = data.get('template', '')
    task = data.get('task', '')
    text = data.get('text', '')
    domain = data.get('domain', '')

    text_list = [text]

    # Get profiles for the domain
    domain_profiles = profiles_dict.get(domain, {})
    profiles = [
        Profile(name=scientist, bio=info.get('bio', ''))
        for scientist, info in domain_profiles.items()
    ]

    # Generate proposal
    gen_proposal = write_proposal(mode, profiles, text_list, config)

    # Prepare result
    result = {
        'attack_id': attack_id,
        'template': template,
        'task': task,
        'domain': domain,
        'gen_proposal': gen_proposal,
    }

    return result


def main() -> None:
    parser = argparse.ArgumentParser(description='Research Proposal Attack Script')
    parser.add_argument(
        '--adversarial_path',
        type=str,
        required=False,
        default='./attackbench/adversarial.json',
        help='Input adversarial JSON file path',
    )
    parser.add_argument(
        '--profile_path',
        type=str,
        required=False,
        default='./attackbench/profiles.json',
        help='Input profile JSON file path',
    )
    parser.add_argument(
        '--output_path',
        type=str,
        required=False,
        default='./attackbench/attack_results.jsonl',
        help='Output JSONL file path',
    )
    parser.add_argument(
        '--mode',
        type=str,
        required=False,
        default='textgnn_nodb',
        choices=[
            'author_only',
            'citation_only',
            'author_citation',
            'textgnn',
            'sakana_ai_scientist',
        ],
        help='Processing mode',
    )
    parser.add_argument(
        '--config_path',
        type=str,
        default='../configs',
        help='Path to the configuration directory',
    )
    parser.add_argument(
        '--num_workers',
        type=int,
        default=4,
        help='Number of parallel workers to use',
    )
    args = parser.parse_args()

    config = Config(args.config_path)
    dataset = load_adversarial_data(args.adversarial_path, args.output_path)
    profiles_dict = load_profiles(args.profile_path)
    logger.info(f'Processing {len(dataset)} adversarial entries')

    with ProcessPoolExecutor(max_workers=args.num_workers) as executor:
        futures = [
            executor.submit(process_attack, attack_id, data, profiles_dict, config, args.mode)
            for attack_id, data in dataset.items()
        ]

        for future in tqdm(as_completed(futures), total=len(futures), desc='Processing attacks'):
            result = future.result()
            save_result(result, args.output_path)

    logger.info(
        f'All adversarial entries have been processed and saved to {args.output_path}'
    )


if __name__ == '__main__':
    main()
