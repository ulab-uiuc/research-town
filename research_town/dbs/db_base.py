import json
import os
import pickle
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

import torch

from ..data.data import Data
from ..utils.logger import logger

T = TypeVar('T', bound=Data)


class BaseDB(Generic[T]):
    def __init__(
        self, data_class: Type[T], load_file_path: Optional[str] = None
    ) -> None:
        self.project_name: Optional[str] = None
        self.data_class = data_class
        self.data: Dict[str, T] = {}
        self.data_embed: Dict[str, torch.Tensor] = {}
        if load_file_path is not None:
            self.load_from_json(load_file_path)

    def set_project_name(self, project_name: str) -> None:
        self.project_name = project_name

    def add(self, data: T) -> None:
        if self.project_name is not None:
            data.project_name = self.project_name
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

    def get(self, **conditions: Union[str, int, float, List[int], None]) -> List[T]:
        if conditions == {} or conditions is None:
            return list(self.data.values())
        result = []
        for data in self.data.values():
            if all(getattr(data, key) == value for key, value in conditions.items()):
                result.append(data)
        return result

    def save_to_json(
        self, save_path: str, with_embed: bool = False, class_name: Optional[str] = None
    ) -> None:
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        if class_name is None:
            file_name = f'{self.__class__.__name__}.json'
        else:
            file_name = f'{class_name}.json'

        if with_embed:
            self.save_to_pkl(save_path, class_name=class_name)

        with open(os.path.join(save_path, file_name), 'w') as f:
            json.dump(
                {pk: data.model_dump() for pk, data in self.data.items()},
                f,
                indent=2,
            )

    def save_to_pkl(self, save_path: str, class_name: Optional[str] = None) -> None:
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        if class_name is None:
            file_name = f'{self.__class__.__name__}.pkl'
        else:
            file_name = f'{class_name}.pkl'
        with open(os.path.join(save_path, file_name), 'wb') as pkl_file:
            pickle.dump(self.data_embed, pkl_file)

    def load_from_json(
        self, load_path: str, with_embed: bool = False, class_name: Optional[str] = None
    ) -> None:
        if class_name is None:
            file_name = f'{self.__class__.__name__}.json'
        else:
            file_name = f'{class_name}.json'

        if with_embed:
            self.load_from_pkl(load_path, class_name=class_name)

        with open(os.path.join(load_path, file_name), 'r') as f:
            data: Dict[str, Any] = json.load(f)
            if with_embed:
                for pk in data.keys():
                    if pk in self.data_embed:
                        data[pk]['embed'] = self.data_embed[pk]
            self.data = {pk: self.data_class(**data) for pk, data in data.items()}

    def load_from_pkl(self, load_path: str, class_name: Optional[str] = None) -> None:
        if class_name is None:
            file_name = f'{self.__class__.__name__}.pkl'
        else:
            file_name = f'{class_name}.pkl'
        with open(os.path.join(load_path, file_name), 'rb') as pkl_file:
            self.data_embed = pickle.load(pkl_file)
