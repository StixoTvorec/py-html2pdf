from logging import getLogger, Formatter, StreamHandler, FileHandler, DEBUG, INFO, WARNING, ERROR
from pathlib import Path
from sys import stderr

__all__ = ['init', 'config_logger', 'get_log_level', 'get_logger']


def get_logger():
    return getLogger('pdf_generator')


def init(max_level, file: str = ''):
    if type(max_level) == str:
        max_level = get_log_level(max_level)
    return config_logger(max_level, file)


def get_log_level(level: str) -> int:
    if 'debug' == level:
        return DEBUG
    if 'info' == level:
        return INFO
    if 'warning' == level:
        return WARNING
    return ERROR


def config_logger(max_level: int, file: str = ''):
    logger = get_logger()
    logger.setLevel(DEBUG)

    formatter = Formatter('%(asctime)s:%(name)s - %(levelname)s - %(message)s')

    if '' == file:
        handler = StreamHandler(stream=stderr)
    else:
        Path(file).absolute().parent.mkdir(parents=True, exist_ok=True)
        handler = FileHandler(filename=file)

    handler.setLevel(max_level)
    handler.setFormatter(formatter)

    for _handler in logger.handlers:
        logger.removeHandler(_handler)

    logger.addHandler(handler)

    return logger
