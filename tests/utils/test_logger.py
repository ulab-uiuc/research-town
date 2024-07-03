from beartype.typing import Dict, List, Union

from research_town.utils.logger import logging_decorator


@logging_decorator
def test_logging_callback() -> Union[List[Dict[str, str]], None]:
    return [{'text': 'foobar', 'level': 'INFO'}]
