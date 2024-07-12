import json
from typing import Any, Dict, List, Type, TypeVar

from pydantic import BaseModel

from ..utils.logger import logger
from .env_data import (
    AgentAgentCollaborationFindingLog,
    AgentAgentIdeaDiscussionLog,
    AgentIdeaBrainstormingLog,
    AgentPaperLiteratureReviewLog,
    AgentPaperMetaReviewWritingLog,
    AgentPaperRebuttalWritingLog,
    AgentPaperReviewWritingLog,
    AgentPaperWritingLog,
    BaseEnvLogData,
)

T = TypeVar('T', bound=BaseModel)


class EnvLogDB:
    def __init__(self) -> None:
        self.data: Dict[str, List[Any]] = {}
        self.data_classes: Dict[str, Type[BaseEnvLogData]] = {}
        for data_class in [
            AgentPaperLiteratureReviewLog,
            AgentIdeaBrainstormingLog,
            AgentAgentCollaborationFindingLog,
            AgentAgentIdeaDiscussionLog,
            AgentPaperWritingLog,
            AgentPaperReviewWritingLog,
            AgentPaperRebuttalWritingLog,
            AgentPaperMetaReviewWritingLog,
        ]:
            self.register_class(data_class)

    def register_class(self, cls: Type[T]) -> None:
        class_name = cls.__name__
        self.data[class_name] = []
        self.data_classes[class_name] = cls

    def add(self, obj: T) -> None:
        class_name = obj.__class__.__name__
        if class_name in self.data:
            self.data[class_name].append(obj)
            logger.info(
                f"Creating instance of '{obj.__class__.__name__}': \n'{obj.dict()}'"
            )
        else:
            raise ValueError(f'Unsupported log type: {class_name}')

    def get(self, cls: Type[T], **conditions: Dict[str, Any]) -> List[T]:
        class_name = cls.__name__
        if class_name not in self.data:
            raise ValueError(f'Unsupported log type: {class_name}')
        result = []
        for instance in self.data[class_name]:
            if all(
                getattr(instance, key) == value for key, value in conditions.items()
            ):
                result.append(instance)
        return result

    def update(
        self, cls: Type[T], conditions: Dict[str, Any], updates: Dict[str, Any]
    ) -> int:
        class_name = cls.__name__
        if class_name not in self.data:
            raise ValueError(f'Unsupported log type: {class_name}')
        updated_count = 0
        for i, instance in enumerate(self.data[class_name]):
            if all(
                getattr(instance, key) == value for key, value in conditions.items()
            ):
                updated_instance = instance.copy(update=updates)
                self.data[class_name][i] = updated_instance
                updated_count += 1
        return updated_count

    def delete(self, cls: Type[T], **conditions: Dict[str, Any]) -> int:
        class_name = cls.__name__
        if class_name not in self.data:
            raise ValueError(f'Unsupported log type: {class_name}')
        initial_count = len(self.data[class_name])
        self.data[class_name] = [
            instance
            for instance in self.data[class_name]
            if not all(
                getattr(instance, key) == value for key, value in conditions.items()
            )
        ]
        return initial_count - len(self.data[class_name])

    def save_to_json(self, file_name: str) -> None:
        with open(file_name, 'w') as f:
            json.dump(self.data.model_dump(), f, indent=2)

    def load_from_json(self, file_name: str) -> None:
        with open(file_name, 'r') as f:
            raw_data = json.load(f)
            self.data = {
                k: [self.model_classes[k](**item) for item in v]
                for k, v in raw_data.items()
            }
