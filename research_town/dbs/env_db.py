from pydantic import BaseModel, Field
from typing import Optional
import json
from typing import TypeVar, Type, List, Dict, Any

T = TypeVar('T', bound=BaseModel)

class EnvLogDB:
    def __init__(self):
        self.data = {
            "AgentPaperReviewLog": [],
            "AgentPaperRebuttalLog": [],
            "AgentPaperMetaReviewLog": [],
            "AgentAgentDiscussionLog": []
        }

    def add(self, obj: T) -> None:
        class_name = obj.__class__.__name__
        if class_name in self.data:
            self.data[class_name].append(obj.dict())
        else:
            raise ValueError(f"Unsupported log type: {class_name}")

    def get(self, cls: Type[T], **conditions) -> List[T]:
        class_name = cls.__name__
        if class_name not in self.data:
            raise ValueError(f"Unsupported log type: {class_name}")
        result = []
        for data in self.data[class_name]:
            instance = cls(**data)
            if all(getattr(instance, key) == value for key, value in conditions.items()):
                result.append(instance)
        return result

    def update(self, cls: Type[T], conditions: Dict[str, Any], updates: Dict[str, Any]) -> int:
        class_name = cls.__name__
        if class_name not in self.data:
            raise ValueError(f"Unsupported log type: {class_name}")
        updated_count = 0
        for data in self.data[class_name]:
            instance = cls(**data)
            if all(getattr(instance, key) == value for key, value in conditions.items()):
                for key, value in updates.items():
                    setattr(instance, key, value)
                self.data[class_name].remove(data)
                self.data[class_name].append(instance.dict())
                updated_count += 1
        return updated_count

    def delete(self, cls: Type[T], **conditions) -> int:
        class_name = cls.__name__
        if class_name not in self.data:
            raise ValueError(f"Unsupported log type: {class_name}")
        initial_count = len(self.data[class_name])
        self.data[class_name] = [
            data for data in self.data[class_name]
            if not all(getattr(cls(**data), key) == value for key, value in conditions.items())
        ]
        return initial_count - len(self.data[class_name])

    def save_to_file(self, file_name: str) -> None:
        with open(file_name, "w") as f:
            json.dump(self.data, f, indent=2)

    def load_from_file(self, file_name: str) -> None:
        with open(file_name, "r") as f:
            self.data = json.load(f)


class AgentPaperReviewLog(BaseModel):
    timestep: int
    review_id: str
    paper_id: str
    agent_id: str
    review_score: int
    review_content: str

class AgentPaperRebuttalLog(BaseModel):
    timestep: int
    rebuttal_id: str
    paper_id: str
    agent_id: str
    rebuttal_content: str

class AgentPaperMetaReviewLog(BaseModel):
    timestep: int
    decision_id: str
    paper_id: str
    agent_id: str
    decision: str
    meta_review: str

class AgentAgentDiscussionLog(BaseModel):
    timestep: int
    discussion_id: str
    agent_from_id: str
    agent_to_id: str
    message: str


