import datetime
import json
import os


def show_time():
    time_stamp = (
        "\033[1;31;40m["
        + str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        + "]\033[0m"
    )

    return time_stamp


def text_wrap(text):
    return "\033[1;31;40m" + str(text) + "\033[0m"


def write_to_json(data, output_file):
    with open(output_file, "w") as file:
        json.dump(data, file, indent=4)


def check_path(path):
    if not os.path.exists(path):
        os.mkdir(path)


def count_entries_in_json(file_path):
    with open(file_path, "r") as file:
        data = json.load(file)
        return len(data)


def clean_title(title):
    cleaned_title = title.replace("\n", " ").strip()
    cleaned_title = os.path.splitext(cleaned_title)[0]
    cleaned_title = (
        cleaned_title.replace(":", "")
        .replace("- ", " ")
        .replace("-", " ")
        .replace("_", " ")
        .title()
    )

    return cleaned_title
