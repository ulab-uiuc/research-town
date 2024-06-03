import datetime
import json
import os

from beartype.typing import Any, Dict, Optional, Tuple


def show_time() -> str:
    time_stamp = (
        '\033[1;31;40m['
        + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        + ']\033[0m'
    )

    return time_stamp


def text_wrap(text: str) -> str:
    return '\033[1;31;40m' + str(text) + '\033[0m'


def write_to_json(data: Dict[str, Any], output_file: str) -> None:
    with open(output_file, 'w') as file:
        json.dump(data, file, indent=4)


def check_path(path: str) -> None:
    if not os.path.exists(path):
        os.mkdir(path)


def count_entries_in_json(file_path: str) -> int:
    with open(file_path, 'r') as file:
        data = json.load(file)
        return len(data)


def clean_title(title: str) -> str:
    cleaned_title = title.replace('\n', ' ').strip()
    cleaned_title = os.path.splitext(cleaned_title)[0]
    cleaned_title = (
        cleaned_title.replace(':', '')
        .replace('- ', ' ')
        .replace('-', ' ')
        .replace('_', ' ')
        .title()
    )

    return 
    
def parse_review(paper_review: str) -> Tuple[Optional[str], Optional[str], Optional[str], Optional[str], Optional[str]]:
    sections = {
        'review_summary': None,
        'review_strength': None,
        'review_weakness': None,
        'review_improvement': None,
        'review_assessment': None
    }
    
    patterns = {
        'review_summary': r'#### Summary\s*(.*?)\s*(?=####|\Z)',
        'review_strength': r'#### Strengths\s*(.*?)\s*(?=####|\Z)',
        'review_weakness': r'#### Weaknesses\s*(.*?)\s*(?=####|\Z)',
        'review_improvement': r'#### Suggestions for Improvement\s*(.*?)\s*(?=####|\Z)',
        'review_assessment': r'#### Overall Assessment\s*(.*?)\s*(?=####|\Z)'
    }
    
    for key, pattern in patterns.items():
        match = re.search(pattern, paper_review, re.DOTALL)
        if match:
            sections[key] = match.group(1).strip()
    
    return (
        sections['review_summary'], 
        sections['review_strength'], 
        sections['review_weakness'], 
        sections['review_improvement'], 
        sections['review_assessment']
    )
