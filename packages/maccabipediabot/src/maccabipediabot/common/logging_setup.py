import logging

DEFAULT_FORMAT = '%(asctime)s : %(levelname)s : %(message)s'


def setup_logging(level: int = logging.INFO, format: str = DEFAULT_FORMAT) -> None:
    logging.basicConfig(format=format, level=level)
