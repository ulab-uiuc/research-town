import json
import pickle
from typing import Any, Dict, Generic, List, Type, TypeVar, Union

from ..utils.logger import logger
from .data import BaseDBData

T = TypeVar('T', bound=BaseDBData)


class BaseDB(Generic[T]):
    def __init__(self, data_class: Type[T]) -> None:
        self.data: Dict[str, T] = {}
        self.data_class = data_class

    def add(self, data: T) -> None:
        self.data[data.pk] = data
        logger.info(
            f"Creating instance of '{data.__class__.__name__}': '{data.model_dump()}'"
        )

    def update(self, pk: str, updates: Dict[str, Any]) -> bool:
        if pk in self.data:
            for key, value in updates.items():
                if value is not None:
                    setattr(self.data[pk], key, value)
            return True
        return False

    def delete(self, pk: str) -> bool:
        if pk in self.data:
            del self.data[pk]
            return True
        return False

    def get(self, **conditions: Union[str, int, float]) -> List[T]:
        result = []
        for data in self.data.values():
            if all(getattr(data, key) == value for key, value in conditions.items()):
                result.append(data)
        return result

    def save_to_json(self, file_name: str) -> None:
        with open(file_name, 'w') as f:
            json.dump(
                {pk: data.model_dump() for pk, data in self.data.items()},
                f,
                indent=2,
            )

    def save_to_pkl(self, file_name: str) -> None:
        with open(file_name, 'wb') as pkl_file:
            pickle.dump(self.data_embed, pkl_file)

    def load_from_json(self, file_name: str, with_embed: bool = False) -> None:
        if with_embed:
            self.load_from_pkl(file_name.replace('.json', '.pkl'))

        with open(file_name, 'r') as f:
            data = json.load(f)
            if with_embed:
                for name in data.keys():
                    if name in self.data_embed:
                        data[name]['embed'] = self.data_embed[name][0]
            self.data = {pk: self.data_class(**data) for pk, data in data.items()}

    def load_from_pkl(self, file_name: str) -> None:
        with open(file_name, 'rb') as pkl_file:
            self.data_embed = pickle.load(pkl_file)
