import json
import logging
from logging import StreamHandler

from beartype.typing import Any, Dict, List, Literal, Mapping, Type, TypeVar, Union
from pydantic import BaseModel
from termcolor import colored

LogType = Union[List[Dict[str, str]], None]

ColorType = Literal[
    'red',
    'green',
    'yellow',
    'blue',
    'magenta',
    'cyan',
    'light_grey',
    'dark_grey',
    'light_red',
    'light_green',
    'light_yellow',
    'light_blue',
    'light_magenta',
    'light_cyan',
    'white',
]

LOG_COLORS: Mapping[str, ColorType] = {
    'BACKGROUND LOG': 'blue',
    'ACTION': 'green',
    'OBSERVATION': 'yellow',
    'DETAIL': 'cyan',
    'ERROR': 'red',
    'PLAN': 'light_magenta',
}


class ColoredFormatter(logging.Formatter):
    def format(self: logging.Formatter, record: logging.LogRecord) -> Any:
        msg_type = record.__dict__.get('msg_type', None)
        if msg_type in LOG_COLORS:
            msg_type_color = colored(msg_type, LOG_COLORS[msg_type])
            msg = colored(record.msg, LOG_COLORS[msg_type])
            time_str = colored(
                self.formatTime(record, self.datefmt), LOG_COLORS[msg_type]
            )
            name_str = colored(record.name, LOG_COLORS[msg_type])
            level_str = colored(record.levelname, LOG_COLORS[msg_type])
            if msg_type == 'ERROR':
                return f'{time_str} - {name_str}:{level_str}: {record.filename}:{record.lineno}\n{msg_type_color}\n{msg}'
            return f'{time_str} - {msg_type_color}\n{msg}'
        elif msg_type == 'STEP':
            msg = '\n\n==============\n' + record.msg + '\n'
            return f'{msg}'
        return logging.Formatter.format(self, record)


console_formatter = ColoredFormatter(
    '\033[92m%(asctime)s - %(name)s:%(levelname)s\033[0m: %(filename)s:%(lineno)s - %(message)s',
    datefmt='%H:%M:%S',
)


def get_console_handler() -> Any:
    """
    Returns a console handler for logging.
    """
    console_handler = StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)
    return console_handler


app_logger = logging.getLogger('research_town')
app_logger.setLevel(logging.DEBUG)
app_logger.addHandler(get_console_handler())

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
            app_logger.info(
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
