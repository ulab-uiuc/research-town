from typing import Dict, List, Mapping, Optional, Type, TypeVar, Union

from .data import BaseDBData
from .db_base import BaseDB

T = TypeVar('T', bound=BaseDBData)


class ComplexDB:
    def __init__(self) -> None:
        self.dbs: Dict[str, BaseDB] = {}

    def register_class(self, profile_class: Type[T]) -> None:
        class_name = profile_class.__name__
        self.dbs[class_name] = BaseDB(profile_class)

    def add(self, profile: T) -> None:
        class_name = profile.__class__.__name__
        if class_name in self.dbs:
            self.dbs[class_name].add(profile)
        else:
            raise ValueError(f'Unsupported type: {class_name}')

    def update(
        self,
        profile_class: Type[T],
        updates: Mapping[str, Optional[Union[str, int, float]]],
        **conditions: Union[str, int, float],
    ) -> int:
        update_count = 0
        class_name = profile_class.__name__
        if class_name in self.dbs:
            profile_pks = [
                profile.pk for profile in self.get(profile_class, **conditions)
            ]
            for profile_pk in profile_pks:
                if self.dbs[class_name].update(profile_pk, updates):
                    update_count += 1
            return update_count
        else:
            raise ValueError(f'Unsupported type: {class_name}')

    def delete(
        self, profile_class: Type[T], **conditions: Union[str, int, float]
    ) -> int:
        delete_count = 0
        class_name = profile_class.__name__
        if class_name in self.dbs:
            profile_pks = [
                profile.pk for profile in self.get(profile_class, **conditions)
            ]
            for profile_pk in profile_pks:
                if self.dbs[class_name].delete(profile_pk):
                    delete_count += 1
            return delete_count
        else:
            raise ValueError(f'Unsupported type: {class_name}')

    def get(
        self, profile_class: Type[T], **conditions: Union[str, int, float]
    ) -> List[T]:
        class_name = profile_class.__name__
        if class_name in self.dbs:
            return self.dbs[class_name].get(**conditions)
        else:
            raise ValueError(f'Unsupported type: {class_name}')

    def save_to_json(self, file_name: str) -> None:
        for class_name, db in self.dbs.items():
            db.save_to_json(f'{file_name}_{class_name}.json')

    def save_to_pkl(self, file_name: str) -> None:
        for class_name, db in self.dbs.items():
            db.save_to_pkl(f'{file_name}_{class_name}.pkl')

    def load_from_json(self, file_name: str) -> None:
        for class_name, db in self.dbs.items():
            db.load_from_json(f'{file_name}_{class_name}.json')

    def load_from_pkl(self, file_name: str) -> None:
        for class_name, db in self.dbs.items():
            db.load_from_pkl(f'{file_name}_{class_name}.pkl')
