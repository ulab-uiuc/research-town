import datetime
import json
import os
from typing import Any, Dict
import importlib
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


class Serializer:
    @classmethod
    def serialize(cls, obj):
        if isinstance(obj, (str, int, float, bool, type(None))):
            return obj
        elif isinstance(obj, dict):
            return {key: cls.serialize(value) for key, value in obj.items()}
        elif isinstance(obj, (list, tuple, set)):
            return type(obj)(cls.serialize(item) for item in obj)
        elif hasattr(obj, '__dict__'):
            return {
                '__class__': obj.__class__.__name__,
                '__module__': obj.__class__.__module__,
                **{key: cls.serialize(value) for key, value in obj.__dict__.items() if not callable(value)}
            }
        else:
            return obj

    @classmethod
    def deserialize(cls, data):
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