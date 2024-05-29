import importlib
from typing import Any, Dict, List, Set, Tuple, Union
from ..dbs import AgentProfile, PaperProfile, AgentPaperReviewLog, AgentPaperMetaReviewLog

from pydantic import BaseModel

def serialize_paper_profiles(papers: List[PaperProfile]) -> Dict[str, str]:
    paper_dict = {}
    for paper in papers:
        if paper.title is not None and paper.abstract is not None:
            paper_dict[paper.pk] = {
                'abstract': paper.abstract,
                'title': paper.title
            }
    return paper_dict

def serialize_agent_profiles(profiles: List[AgentProfile]) -> Dict[str, str]:
    profile_dict = {}
    for profile in profiles:
        if profile.name is not None and profile.bio is not None:
            profile_dict[profile.id] = {
                'name': profile.name,
                'bio': profile.bio
            }
    return profile_dict

def serialize_agent_paper_reviewlogs(review_logs: List[AgentPaperReviewLog]) -> Dict[str, Dict[str, Union[str, int]]]:
    review_dict = {}
    for review_log in review_logs:
        if review_log.review_content is not None and review_log.review_score is not None:
            review_dict[review_log.pk] = {
                'review_content': review_log.review_content,
                'review_score': review_log.review_score
            }
    return review_dict

def serialize_agent_paper_metareviewlogs(meta_review_logs: List[AgentPaperMetaReviewLog]) -> Dict[str, Dict[str, Union[str, bool]]]:
    meta_review_dict = {}
    for meta_review_log in meta_review_logs:
        if meta_review_log.meta_review is not None and meta_review_log.decision is not None:
            meta_review_dict[meta_review_log.pk] = {
                'meta_review': meta_review_log.meta_review,
                'decision': meta_review_log.decision
            }
    return meta_review_dict

def serialize_agent_agent_discussionlogs(discussion_logs: List[AgentAgentDiscussionLog]) -> Dict[str, Dict[str, Union[str, int]]]:
    discussion_dict = {}
    for discussion_log in discussion_logs:
        if discussion_log.message is not None:
            discussion_dict[discussion_log.pk] = {
                'message': discussion_log.message
            }
    return discussion_dict

class Serializer(object):
    @classmethod
    def serialize(cls, obj: Any) -> Any:
        if isinstance(obj, (str, int, float, bool, type(None))):
            return obj
        elif isinstance(obj, dict):
            return {key: cls.serialize(value) for key, value in obj.items()}
        elif isinstance(obj, (list, tuple, set)):
            return type(obj)(cls.serialize(item) for item in obj)
        elif hasattr(obj, '__dict__'): # custom class
            return {
                '__class__': obj.__class__.__name__,
                '__module__': obj.__class__.__module__,
                **{key: cls.serialize(value) for key, value in obj.__dict__.items() if not callable(value) and key != 'ckpt'}
            }
        else:
            raise TypeError(f"Unsupported data type: {type(obj)}")

    @classmethod
    def deserialize(cls, data: Union[Dict[str, Any], List[Any], Tuple[Any, ...], Set[Any], str, int, bool]) -> Any:
        if not isinstance(data, dict):
            if isinstance(data, list):
                return [cls.deserialize(item) for item in data]
            elif isinstance(data, tuple):
                return tuple(cls.deserialize(item) for item in data)
            elif isinstance(data, set):
                return {cls.deserialize(item) for item in data}
            if isinstance(data, str) or isinstance(data, int) or isinstance(data, bool):
                return data
            else:
                raise TypeError(f"Unsupported data type: {type(data)}")

        class_name = data.get('__class__')
        module_name = data.get('__module__')

        if class_name and module_name:
            module = importlib.import_module(module_name)
            target_class = getattr(module, class_name)
            obj = target_class.__new__(target_class)

            attributes = {k: v for k, v in data.items() if k not in {'__class__', '__module__'}}

            if issubclass(target_class, BaseModel):
                # Use Pydantic's construct method for BaseModel subclasses
                obj = target_class.construct(**attributes)
            else:
                for key, value in attributes.items():
                    setattr(obj, key, cls.deserialize(value))
            return obj
        else:
            return {key: cls.deserialize(value) for key, value in data.items()}
