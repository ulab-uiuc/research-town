import datetime
import json
import os

from beartype.typing import Any, Dict


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

    return cleaned_title
