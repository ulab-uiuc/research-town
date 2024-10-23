from abc import ABC, abstractmethod
from typing import Any, Dict, List, Union

import numpy as np
import numpy.typing as npt


class DatabaseClient(ABC):
    @abstractmethod
    def register_namespace(self, namespace: str, with_embeddings: bool) -> None:
        """
        Register a namespace in the database.

        :param namespace: The namespace to register.
        :param with_embeddings: Whether to store embeddings in the namespace
                                and perform search operations.
        """

    @abstractmethod
    def count(self, namespace: str, **conditions: Union[str, int, float]) -> int:
        """
        Count the number of records in the namespace that satisfy the conditions.

        :param namespace: The namespace to count records from.
        :param conditions: Conditions to filter the records.
        :return: The number of records that satisfy the conditions.
        """

    @abstractmethod
    def add(
        self,
        namespace: str,
        data: List[Dict[str, Any]],
        embeddings: List[npt.NDArray[np.float32]],
    ) -> None:
        """
        Add the list of data to a given namespace.

        :param namespace: The namespace to add data to.
        :param data: list of data to add.
        :param embeddings: The embeddings of the data. It should be in the same order as data.
        In case of no embeddings, pass an empty list.
        """

    @abstractmethod
    def update(self, namespace: str, pk: str, updates: Dict[str, Any]) -> bool:
        """
        Update the record with the given primary key in the namespace.
        :param namespace: The namespace to update the record in.
        :param pk: The primary key of the record to update.
        :param updates: The updates to apply to the record.
        :return: True if the record was updated successfully, False otherwise.

        To update the embeddings of a record, pass the new embedding as a value in the
        updates dictionary with the key as 'embedding'.
        """

    @abstractmethod
    def delete(self, namespace: str, pk: str) -> bool:
        """
        Delete the record with the given primary key from the namespace.
        :param namespace: The namespace to delete the record from.
        :param pk: The primary key of the record to delete.
        :return: True if the record was deleted successfully, False otherwise.
        """

    @abstractmethod
    def get(
        self, namespace: str, **conditions: Union[str, int, float, List[int], None]
    ) -> List[Dict[str, Any]]:
        """
        Get the records from the namespace that satisfy the conditions.
        :param namespace: The namespace to get records from.
        :param conditions: Conditions to filter the records.
        :return: The list of records that satisfy the conditions.
        """

    @abstractmethod
    def search(
        self,
        namespace: str,
        query_embeddings: List[npt.NDArray[np.float32]],
        num: int = 1,
        **conditions: Union[str, int, float, List[int], None],
    ) -> List[List[Dict[str, Any]]]:
        """
        Search for the records in the namespace that satisfy the conditions
            and are closest to the query embeddings.

        :param namespace: The namespace to search records from.
        :param query_embeddings: The embeddings to search for.
        :param num: The number of records to return.
        :param conditions: Conditions to filter the records.

        :return: The list of list of records that satisfy the conditions and
                are closest to the query embeddings.
                Each list corresponds to the records closest to the corresponding query embeddings.
        """
