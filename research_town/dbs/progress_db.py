import json
from typing import Any, Dict, List, Type, TypeVar

from .progress_data import BaseProgressData

T = TypeVar('T', bound=BaseProgressData)


class ProgressDB:
    def __init__(self) -> None:
        self.data: Dict[str, List[BaseProgressData]] = {
            'ResearchInsight': [],
            'ResearchIdea': [],
            'ResearchPaperSubmission': [],
            'ResearchReviewForPaperSubmission': [],
            'ResearchRebuttalForPaperSubmission': [],
            'ResearchMetaReviewForPaperSubmission': [],
        }

    def add(self, obj: T) -> None:
        class_name = obj.__class__.__name__
        if class_name in self.data:
            self.data[class_name].append(obj)
        else:
            raise ValueError(f'Unsupported type: {class_name}')

    def get(self, cls: Type[T], **conditions: Dict[str, Any]) -> List[T]:
        class_name = cls.__name__
        if class_name not in self.data:
            raise ValueError(f'Unsupported type: {class_name}')
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
            raise ValueError(f'Unsupported type: {class_name}')
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
            raise ValueError(f'Unsupported type: {class_name}')
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
            json.dump(
                {k: [item.dict() for item in v] for k, v in self.data.items()},
                f,
                indent=2,
            )

    def load_from_json(
        self, file_name: str, model_classes: Dict[str, Type[BaseProgressData]]
    ) -> None:
        with open(file_name, 'r') as f:
            raw_data = json.load(f)
            self.data = {
                k: [model_classes[k](**item) for item in v] for k, v in raw_data.items()
            }
