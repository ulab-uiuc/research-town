import logging
from typing import Dict, List, Union

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
def logging_callback(messages: Union[List[Dict[str, str]], None] = None) -> None:
    """
    Logs messages using the logging module.

    :param messages: List of dictionaries containing 'text' and 'level' keys.
    """
    if not messages:
        return
    for message in messages:
        text = message.get('text', '')
        level = message.get('level', 'INFO').upper()

        if level == 'DEBUG':
            logging.debug(text)
        elif level == 'INFO':
            logging.info(text)
        elif level == 'WARNING':
            logging.warning(text)
        elif level == 'ERROR':
            logging.error(text)
        elif level == 'CRITICAL':
            logging.critical(text)
        else:
            logging.info(text)  # Default to INFO if the level is not recognized
