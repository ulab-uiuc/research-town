from typing import Dict, List, Never, Union

from research_town.utils.logging import logging_decorator


@logging_decorator
def test_logging_callback() -> Union[List[Dict[str, str]], List[Never], None]:
    return []
