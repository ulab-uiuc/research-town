import datetime
import importlib
import json
import logging
import os
from typing import Any, Dict, List, Set, Tuple, Union

from pydantic import BaseModel


def show_time() -> str:
    time_stamp = (
        "\033[1;31;40m["
        + str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        + "]\033[0m"
    )

    return time_stamp


def text_wrap(text: str) -> str:
    return "\033[1;31;40m" + str(text) + "\033[0m"


def write_to_json(data: Dict[str, Any], output_file: str) -> None:
    with open(output_file, "w") as file:
        json.dump(data, file, indent=4)


def check_path(path: str) -> None:
    if not os.path.exists(path):
        os.mkdir(path)


def count_entries_in_json(file_path: str) -> int:
    with open(file_path, "r") as file:
        data = json.load(file)
        return len(data)


def clean_title(title: str) -> str:
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


logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
def logging_callback(messages: Union[List[Dict[str, str]], None] = None) -> None:
    """
    Logs messages using the logging module.

    :param messages: List of dictionaries containing 'text' and 'level' keys.
    """
    if not messages:
        return
    for message in messages:
        text = message.get('text', '')
        level = message.get('level', 'INFO').upper()

        if level == 'DEBUG':
            logging.debug(text)
        elif level == 'INFO':
            logging.info(text)
        elif level == 'WARNING':
            logging.warning(text)
        elif level == 'ERROR':
            logging.error(text)
        elif level == 'CRITICAL':
            logging.critical(text)
        else:
            logging.info(text)  # Default to INFO if the level is not recognized

class Serializer:
    @classmethod
    def serialize(cls, obj: Any) -> Any:
        if isinstance(obj, (str, int, float, bool, type(None))):
            return obj
        elif isinstance(obj, dict):
            return {key: cls.serialize(value) for key, value in obj.items()}
        elif isinstance(obj, (list, tuple, set)):
            return type(obj)(cls.serialize(item) for item in obj)
        elif hasattr(obj, '__dict__'): # custom class
            return {
                '__class__': obj.__class__.__name__,
                '__module__': obj.__class__.__module__,
                **{key: cls.serialize(value) for key, value in obj.__dict__.items() if not callable(value) and key != 'ckpt'}
            }
        else:
            raise TypeError(f"Unsupported data type: {type(obj)}")

    @classmethod
    def deserialize(cls, data: Union[Dict[str, Any], List[Any], Tuple[Any, ...], Set[Any], str, int, bool]) -> Any:
        if not isinstance(data, dict):
            if isinstance(data, list):
                return [cls.deserialize(item) for item in data]
            elif isinstance(data, tuple):
                return tuple(cls.deserialize(item) for item in data)
            elif isinstance(data, set):
                return {cls.deserialize(item) for item in data}
            if isinstance(data, str) or isinstance(data, int) or isinstance(data, bool):
                return data
            else:
                raise TypeError(f"Unsupported data type: {type(data)}")

        class_name = data.get('__class__')
        module_name = data.get('__module__')

        if class_name and module_name:
            module = importlib.import_module(module_name)
            target_class = getattr(module, class_name)
            obj = target_class.__new__(target_class)

            attributes = {k: v for k, v in data.items() if k not in {'__class__', '__module__'}}

            if issubclass(target_class, BaseModel):
                # Use Pydantic's construct method for BaseModel subclasses
                obj = target_class.construct(**attributes)
            else:
                for key, value in attributes.items():
                    setattr(obj, key, cls.deserialize(value))
            return obj
        else:
            return {key: cls.deserialize(value) for key, value in data.items()}
