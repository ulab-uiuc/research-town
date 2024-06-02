import logging
from logging import StreamHandler

from beartype.typing import Any, Callable, Dict, List, Literal, Mapping, Union
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


def logging_decorator(
    func: Callable[..., LogType],
) -> Callable[..., LogType]:
    def wrapper(*args: List[Any], **kwargs: Dict[str, Any]) -> None:
        messages = func(*args, **kwargs)
        if not messages:
            return
        for message in messages:
            text = message.get('text', '')
            level = str(message.get('level', 'INFO')).upper()

            if level == 'DEBUG':
                app_logger.debug(text)
            elif level == 'INFO':
                app_logger.info(text)
            elif level == 'WARNING':
                app_logger.warning(text)
            elif level == 'ERROR':
                app_logger.error(text)
            elif level == 'CRITICAL':
                app_logger.critical(text)
            else:
                app_logger.info(text)  # Default to INFO if the level is not recognized

    return wrapper
