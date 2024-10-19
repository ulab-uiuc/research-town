from typing import Any, Dict, List, Type, TypeVar, Union

from ..configs import DatabaseConfig
from ..data.data import Data
from .db_base import BaseDB

T = TypeVar('T', bound=Data)


class ComplexDB:
    def __init__(self, classes_to_register: List[Any], config: DatabaseConfig) -> None:
        self.dbs: Dict[str, BaseDB[Any]] = {}
        for data_class in classes_to_register:
            self.register_class(data_class, config)

    def register_class(self, data_class: Any, config: DatabaseConfig) -> None:
        class_name = data_class.__name__
        db = BaseDB(data_class, config)
        self.dbs[class_name] = db

    def set_project_name(self, project_name: str) -> None:
        for db in self.dbs.values():
            db.set_project_name(project_name)

    def count(self, data_class: Type[T], **conditions: Union[str, int, float]) -> int:
        class_name = data_class.__name__
        if class_name in self.dbs:
            return self.dbs[class_name].count(**conditions)
        else:
            raise ValueError(f'Unsupported type: {class_name}')

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
