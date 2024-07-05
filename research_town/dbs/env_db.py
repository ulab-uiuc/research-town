import json

from beartype.typing import Any, Dict, List, Type, TypeVar
from pydantic import BaseModel

from ..utils.logger import logger

T = TypeVar('T', bound=BaseModel)


class EnvLogDB:
    def __init__(self) -> None:
        self.data: Dict[str, List[Any]] = {
            'PaperProfile': [],
            'ResearchPaperSubmission': [],
            'AgentPaperLiteratureReviewLog': [],
            'AgentIdeaBrainstormingLog': [],
            'AgentAgentCollaborationFindingLog': [],
            'AgentAgentIdeaDiscussionLog': [],
            'AgentPaperWritingLog': [],
            'AgentPaperReviewWritingLog': [],
            'AgentPaperRebuttalWritingLog': [],
            'AgentPaperMetaReviewWritingLog': [],
        }

    def add(self, obj: T) -> None:
        class_name = obj.__class__.__name__
        if class_name in self.data:
            self.data[class_name].append(obj.model_dump())
            logger.info(
                f"Creating instance of '{obj.__class__.__name__}': '{obj.dict()}'"
            )
        else:
            raise ValueError(f'Unsupported log type: {class_name}')

    def get(self, cls: Type[T], **conditions: Dict[str, Any]) -> List[T]:
        class_name = cls.__name__
        if class_name not in self.data:
            raise ValueError(f'Unsupported log type: {class_name}')
        result = []
        for data in self.data[class_name]:
            instance = cls(**data)
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
        for data in self.data[class_name]:
            instance = cls(**data)
            if all(
                getattr(instance, key) == value for key, value in conditions.items()
            ):
                for key, value in updates.items():
                    setattr(instance, key, value)
                self.data[class_name].remove(data)
                self.data[class_name].append(instance.model_dump())
                updated_count += 1
        return updated_count

    def delete(self, cls: Type[T], **conditions: Dict[str, Any]) -> int:
        class_name = cls.__name__
        if class_name not in self.data:
            raise ValueError(f'Unsupported log type: {class_name}')
        initial_count = len(self.data[class_name])
        self.data[class_name] = [
            data
            for data in self.data[class_name]
            if not all(
                getattr(cls(**data), key) == value for key, value in conditions.items()
            )
        ]
        return initial_count - len(self.data[class_name])

    def save_to_file(self, file_name: str) -> None:
        with open(file_name, 'w') as f:
            json.dump(self.data, f, indent=2)

    def load_from_file(self, file_name: str) -> None:
        with open(file_name, 'r') as f:
            self.data = json.load(f)
