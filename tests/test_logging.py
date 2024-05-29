from research_town.utils.logging_callback import logging_callback


def test_logging_callback() -> None:
    logging_callback()
    logging_callback([])
    logging_callback([{'text': 'text', 'level': 'INFO'}])
