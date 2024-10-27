import json
import os
import pickle
from typing import Any, Dict, List, Set, TypeVar, Union

import numpy as np
import numpy.typing as npt

from ....data.data import Data
from ..client import DatabaseClient

T = TypeVar('T', bound=Data)


class LocalDatabaseClient(DatabaseClient):
    def __init__(self) -> None:
        self.data: Dict[str, Dict[str, Any]] = {}
        self.data_embed: Dict[str, Dict[str, npt.NDArray[np.float32]]] = {}
        self.registered_namespaces: Set[str] = set()

        folder_path = os.getenv('DATABASE_FOLDER_PATH')
        if folder_path is None:
            raise ValueError(
                'LocalDatabaseClient: env variable DATABASE_FOLDER_PATH is required'
            )

        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        self.folder_path = folder_path
        self.load()

    def register_namespace(self, namespace: str, with_embeddings: bool) -> None:
        if namespace not in self.registered_namespaces:
            self.registered_namespaces.add(namespace)
            self.data[namespace] = {}
            if with_embeddings:
                self.data_embed[namespace] = {}
            self.save_manifest()

    def count(self, namespace: str, **conditions: Union[str, int, float]) -> int:
        if conditions is None or not conditions:
            return len(self.data[namespace])
        result = 0
        for data in self.data[namespace].values():
            if all(data[key] == value for key, value in conditions.items()):
                result += 1
        return result

    def add(
        self,
        namespace: str,
        data: List[Dict[str, Any]],
        embeddings: List[npt.NDArray[np.float32]],
    ) -> None:
        with_embed = namespace in self.data_embed
        if with_embed and len(data) != len(embeddings):
            raise ValueError(
                f'Length of data and embedding should match for namespace: {namespace}'
            )
        if all('pk' not in data_item for data_item in data):
            raise ValueError("Primary key 'pk' is required in data")

        if with_embed:
            for data_item, embedding in zip(data, embeddings, strict=True):
                self.data_embed[namespace][data_item['pk']] = embedding
                self.data[namespace][data_item['pk']] = data_item
        else:
            for data_item in data:
                self.data[namespace][data_item['pk']] = data_item

        self.save_namespace(namespace, with_embed=with_embed)

    def update(self, namespace: str, pk: str, updates: Dict[str, Any]) -> bool:
        if namespace in self.data and pk in self.data[namespace]:
            with_embed = False
            for key, value in updates.items():
                if value is not None:
                    if key == 'embedding' and namespace in self.data_embed:
                        self.data_embed[namespace][pk] = value
                        with_embed = True
                    else:
                        self.data[namespace][pk][key] = value
            self.save_namespace(namespace, with_embed=with_embed)
            return True
        return False

    def delete(self, namespace: str, pk: str) -> bool:
        if namespace in self.data and pk in self.data[namespace]:
            self.data[namespace].pop(pk)
            if namespace in self.data_embed and pk in self.data_embed[namespace]:
                self.data_embed[namespace].pop(pk)
                with_embed = True
            else:
                with_embed = False
            self.save_namespace(namespace, with_embed=with_embed)
            return True
        return False

    def get(
        self, namespace: str, **conditions: Union[str, int, float, List[int], None]
    ) -> List[Dict[str, Any]]:
        if conditions is None or not conditions:
            return list(self.data[namespace].values())
        result = []
        for data in self.data[namespace].values():
            if all(data[key] == value for key, value in conditions.items()):
                result.append(data)
        return result

    def search(
        self,
        namespace: str,
        query_embeddings: List[npt.NDArray[np.float32]],
        num: int = 1,
        **conditions: Union[str, int, float, List[int], None],
    ) -> List[List[Dict[str, Any]]]:
        if namespace not in self.data_embed:
            raise ValueError(
                f'Embedding search not available for namespace: {namespace}'
            )
        # Filter candidates based on conditions
        candidates = self.get(namespace, **conditions)
        if not candidates:
            return [[] for _ in range(len(query_embeddings))]

        # Fetch embeddings for candidates
        pks = [data['pk'] for data in candidates]
        candidate_embeddings = np.asarray(
            [self.data_embed[namespace][pk] for pk in pks], dtype=np.float32
        )
        candidate_embeddings = candidate_embeddings / np.linalg.norm(
            candidate_embeddings, axis=1, keepdims=True
        )

        q_embeddings = np.asarray(query_embeddings, dtype=np.float32)
        q_embeddings = q_embeddings / np.linalg.norm(
            q_embeddings, axis=1, keepdims=True
        )

        # Calculate cosine similarity
        similarities = q_embeddings @ candidate_embeddings.T

        # Get top matches
        matches = []
        for sorted_indices in np.argsort(similarities, axis=1):
            sorted_indices = sorted_indices[::-1][:num]
            matches.append([candidates[i] for i in sorted_indices])
        return matches

    def save(self, with_embed: bool = False) -> None:
        for namespace in self.data:
            self.save_namespace(namespace, with_embed=with_embed)
        self.save_manifest()

    def save_manifest(self) -> None:
        manifest = {
            'namespaces': list(self.registered_namespaces),
            'embedding_namespaces': list(self.data_embed.keys()),
        }
        with open(
            os.path.join(self.folder_path, 'manifest.json'), 'w', encoding='utf-8'
        ) as f:
            json.dump(manifest, f, indent=2)

    def save_namespace(self, namespace: str, with_embed: bool = False) -> None:
        file_name = f'{namespace}.json'

        if with_embed and namespace in self.data_embed:
            self.save_embeddings(namespace=namespace)

        with open(
            os.path.join(self.folder_path, file_name), 'w', encoding='utf-8'
        ) as f:
            json.dump(
                self.data[namespace],
                f,
                indent=2,
            )

    def save_embeddings(self, namespace: str) -> None:
        if namespace not in self.data_embed:
            return
        file_name = f'{namespace}.pkl'
        with open(os.path.join(self.folder_path, file_name), 'wb') as pkl_file:
            pickle.dump(self.data_embed[namespace], pkl_file)

    def load(self) -> None:
        if not os.path.exists(os.path.join(self.folder_path, 'manifest.json')):
            return

        with open(
            os.path.join(self.folder_path, 'manifest.json'), encoding='utf-8'
        ) as f:
            manifest: Dict[str, Any] = json.load(f)
        self.registered_namespaces = set(manifest['namespaces'])
        embedding_namespaces = set(manifest['embedding_namespaces'])
        for namespace in self.registered_namespaces:
            self.load_namespace(namespace, with_embed=namespace in embedding_namespaces)

    def load_namespace(self, namespace: str, with_embed: bool = False) -> None:
        file_name = f'{namespace}.json'

        if with_embed:
            self.load_embeddings(namespace=namespace)

        if not os.path.exists(os.path.join(self.folder_path, file_name)):
            data: Dict[str, Any] = {}
        else:
            with open(os.path.join(self.folder_path, file_name), encoding='utf-8') as f:
                data = json.load(f)
        self.data[namespace] = data

    def load_embeddings(self, namespace: str) -> None:
        file_name = f'{namespace}.pkl'
        if not os.path.exists(os.path.join(self.folder_path, file_name)):
            self.data_embed[namespace] = {}
        else:
            with open(os.path.join(self.folder_path, file_name), 'rb') as pkl_file:
                self.data_embed[namespace] = pickle.load(pkl_file)
