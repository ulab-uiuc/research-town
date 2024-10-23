from .local import LocalDatabaseClient

DATABASE_REGISTRY = {
    'local': LocalDatabaseClient,
}
