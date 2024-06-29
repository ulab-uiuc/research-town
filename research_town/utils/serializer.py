import importlib

import torch
from beartype.typing import Any, Dict, List, Set, Tuple, Union
from pydantic import BaseModel


class Serializer:
    @classmethod
    def serialize(cls, obj: Any) -> Any:
        if isinstance(obj, (str, int, float, bool, type(None), torch.Tensor)):
            return obj
        elif isinstance(obj, dict):
            return {key: cls.serialize(value) for key, value in obj.items()}
        elif isinstance(obj, (list, tuple, set)):
            return type(obj)(cls.serialize(item) for item in obj)
        elif hasattr(obj, '__dict__'):  # custom class
            return {
                '__class__': obj.__class__.__name__,
                '__module__': obj.__class__.__module__,
                **{
                    key: cls.serialize(value)
                    for key, value in obj.__dict__.items()
                    if not callable(value) and key != 'ckpt'
                },
            }
        else:
            raise TypeError(f'Unsupported data type: {type(obj)}')

    @classmethod
    def deserialize(
        cls,
        data: Union[
            Dict[str, Any], List[Any], Tuple[Any, ...], Set[Any], str, int, bool
        ],
    ) -> Any:
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
                raise TypeError(f'Unsupported data type: {type(data)}')

        class_name = data.get('__class__')
        module_name = data.get('__module__')

        if class_name and module_name:
            module = importlib.import_module(module_name)
            target_class = getattr(module, class_name)
            obj = target_class.__new__(target_class)

            attributes = {
                k: v for k, v in data.items() if k not in {'__class__', '__module__'}
            }

            if issubclass(target_class, BaseModel):
                # Use Pydantic's construct method for BaseModel subclasses
                obj = target_class.model_construct(**attributes)
            else:
                for key, value in attributes.items():
                    setattr(obj, key, cls.deserialize(value))
            return obj
        else:
            return {key: cls.deserialize(value) for key, value in data.items()}
