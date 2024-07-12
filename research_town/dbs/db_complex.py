from typing import Any, Dict, List, Type, TypeVar, Union

from .data import BaseDBData
from .db_base import BaseDB

T = TypeVar('T', bound=BaseDBData)


class ComplexDB:
    def __init__(self) -> None:
        self.dbs: Dict[str, BaseDB[Any]] = {}

    def register_class(self, data_class: Any) -> None:
        class_name = data_class.__name__
        self.dbs[class_name] = BaseDB(data_class)

    def add(self, data: T) -> None:
        class_name = data.__class__.__name__
        if class_name in self.dbs:
            self.dbs[class_name].add(data)
        else:
            raise ValueError(f'Unsupported type: {class_name}')

    def update(
        self,
        data_class: Type[T],
        updates: Dict[str, Any],
        **conditions: Union[str, int, float],
    ) -> int:
        update_count = 0
        class_name = data_class.__name__
        if class_name in self.dbs:
            pks = [data.pk for data in self.get(data_class, **conditions)]
            for pk in pks:
                if self.dbs[class_name].update(pk, updates):
                    update_count += 1
            return update_count
        else:
            raise ValueError(f'Unsupported type: {class_name}')

    def delete(self, data_class: Type[T], **conditions: Union[str, int, float]) -> int:
        delete_count = 0
        class_name = data_class.__name__
        if class_name in self.dbs:
            pks = [data.pk for data in self.get(data_class, **conditions)]
            for pk in pks:
                if self.dbs[class_name].delete(pk):
                    delete_count += 1
            return delete_count
        else:
            raise ValueError(f'Unsupported type: {class_name}')

    def get(self, data_class: Type[T], **conditions: Union[str, int, float]) -> List[T]:
        class_name = data_class.__name__
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
