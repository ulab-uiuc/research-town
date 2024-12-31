from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from ..configs import DatabaseConfig
from ..data.data import Data
from ..utils.logger import logger
from .db_provider import DatabaseClientHandler

T = TypeVar('T', bound=Data)


class BaseDB(Generic[T]):
    def __init__(
        self, data_class: Type[T], config: DatabaseConfig, with_embeddings: bool = False
    ) -> None:
        self.project_name: Optional[str] = None
        self.data_class = data_class
        self.database_client = DatabaseClientHandler.get_client_instance(config)
        self.database_client.register_namespace(
            self.data_class.__name__, with_embeddings=with_embeddings
        )

    def set_project_name(self, project_name: str) -> None:
        self.project_name = project_name

    def count(self, **conditions: Union[str, int, float]) -> int:
        num = self.database_client.count(self.data_class.__name__, **conditions)
        return num

    def add(self, data: T) -> None:
        if self.project_name is not None:
            data.project_name = self.project_name
        if hasattr(data, 'embed') and getattr(data, 'embed') is not None:
            embeddings = [getattr(data, 'embed').numpy(force=True).squeeze()]
            data.embed = None
        else:
            embeddings = []
        self.database_client.add(
            self.data_class.__name__, [data.model_dump(exclude_none=True)], embeddings
        )
        logger.info(f"Creating instance of '{data.__class__.__name__}'")

    def update(self, pk: str, updates: Dict[str, Any]) -> bool:
        return self.database_client.update(self.data_class.__name__, pk, updates)

    def delete(self, pk: str) -> bool:
        return self.database_client.delete(self.data_class.__name__, pk)

    def get(self, **conditions: Union[str, int, float, List[int], None]) -> List[T]:
        data = self.database_client.get(self.data_class.__name__, **conditions)
        return [self.data_class(**d) for d in data]
