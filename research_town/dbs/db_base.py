import json
import pickle
from typing import Dict, Generic, List, Mapping, Optional, Type, TypeVar, Union

from .data import BaseDBData

T = TypeVar('T', bound=BaseDBData)


class BaseDB(Generic[T]):
    def __init__(self, profile_class: Type[T]) -> None:
        self.data: Dict[str, T] = {}
        self.profile_class = profile_class

    def add(self, profile: T) -> None:
        self.data[profile.pk] = profile

    def update(
        self, profile_pk: str, updates: Mapping[str, Optional[Union[str, int, float]]]
    ) -> bool:
        if profile_pk in self.data:
            for key, value in updates.items():
                if value is not None:
                    setattr(self.data[profile_pk], key, value)
            return True
        return False

    def delete(self, profile_pk: str) -> bool:
        if profile_pk in self.data:
            del self.data[profile_pk]
            return True
        return False

    def get(self, **conditions: Union[str, int, float]) -> List[T]:
        result = []
        for profile in self.data.values():
            if all(getattr(profile, key) == value for key, value in conditions.items()):
                result.append(profile)
        return result

    def save_to_json(self, file_name: str) -> None:
        with open(file_name, 'w') as f:
            json.dump(
                {pk: profile.model_dump() for pk, profile in self.data.items()},
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
            self.data = {
                pk: self.profile_class(**profile_data)
                for pk, profile_data in data.items()
            }

    def load_from_pkl(self, file_name: str) -> None:
        with open(file_name, 'rb') as pkl_file:
            self.data_embed = pickle.load(pkl_file)
