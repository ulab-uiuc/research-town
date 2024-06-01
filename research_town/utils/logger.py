import logging

import colorlog
from beartype.typing import Any, Callable, Dict, List, Union

app_logger = logging.getLogger('research_town')
app_logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_formatter = colorlog.ColoredFormatter(
    '%(log_color)s%(levelname)s:%(name)s:%(message)s',
    datefmt=None,
    reset=True,
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'red,bg_white',
    },
    secondary_log_colors={},
    style='%',
)
console_handler.setFormatter(console_formatter)
app_logger.addHandler(console_handler)

LogType = Union[List[Dict[str, str]], None]


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
