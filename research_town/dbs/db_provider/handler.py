from typing import Optional

from ...configs import DatabaseConfig
from .client import DatabaseClient
from .registry import DATABASE_REGISTRY


class DatabaseClientHandler:
    __client__: Optional[DatabaseClient] = None

    @classmethod
    def get_client_instance(cls, config: DatabaseConfig) -> DatabaseClient:
        if cls.__client__ is None:
            database_provider_type = config.provider
            database_provider = DATABASE_REGISTRY.get(database_provider_type)
            if not database_provider:
                raise ValueError(
                    f'Database provider: {database_provider_type} not found'
                )
            cls.__client__ = database_provider()
        return cls.__client__

    @classmethod
    def reset_client_instance(cls) -> None:
        cls.__client__ = None
