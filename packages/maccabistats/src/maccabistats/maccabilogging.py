import logging
import os
from logging import Filter
from logging.handlers import RotatingFileHandler
from pathlib import Path

maccabistats_root_folder_path = Path.home().as_posix()
log_file_path_pattern = os.path.join(maccabistats_root_folder_path, "maccabistats", "logs", "maccabistats-{suffix}.log")
log_file_folder_path = os.path.dirname(log_file_path_pattern)

MB = 1024 * 1024

if not os.path.isdir(log_file_folder_path):
    os.makedirs(log_file_folder_path)

logger = logging.getLogger("maccabistats")


class SpecificLevelFilter(Filter):
    def __init__(self, level):
        super().__init__()

        self.__level = level

    def filter(self, log_record):
        return log_record.levelno == self.__level


def faster_logging():
    # Patch
    logger.info("Use faster logging, removing debug & stdout handlers")
    logger.removeHandler(logger.handlers[3])  # Without stdout
    logger.removeHandler(logger.handlers[0])  # Without Debug


def remove_live_logging():
    # Patch
    logger.info("Removing stdout handlers")
    logger.removeHandler(logger.handlers[3])  # Without stdout


def initialize_logging():
    # Root logger, so all other logger will inherit those handlers.

    logger.setLevel(logging.DEBUG)

    normal_formatter = logging.Formatter(
        '%(asctime)s %(processName)s(%(process)d)  %(name)s  %(levelname)s --- %(message)s')
    advanced_formatter = logging.Formatter(
        '%(asctime)s %(processName)s(%(process)d) %(name)s %(levelname)s --- %(funcName)s(l.%(lineno)d) :: %(message)s')

    debug_handler = RotatingFileHandler(log_file_path_pattern.format(suffix='all'), 'a', encoding="utf-8",
                                        maxBytes=20 * MB)
    debug_handler.setFormatter(advanced_formatter)
    debug_handler.setLevel(logging.DEBUG)

    info_handler = RotatingFileHandler(log_file_path_pattern.format(suffix='info'), 'a', encoding="utf-8",
                                       maxBytes=10 * MB)
    info_handler.setFormatter(advanced_formatter)
    info_handler.setLevel(logging.INFO)
    info_handler.addFilter(SpecificLevelFilter(logging.INFO))

    warning_handler = RotatingFileHandler(log_file_path_pattern.format(suffix='warning'), 'a', encoding="utf-8",
                                          maxBytes=10 * MB)
    warning_handler.setFormatter(normal_formatter)
    warning_handler.setLevel(logging.WARNING)
    warning_handler.addFilter(SpecificLevelFilter(logging.WARNING))

    exception_handler = RotatingFileHandler(log_file_path_pattern.format(suffix='exception'), 'a', encoding="utf-8",
                                            maxBytes=10 * MB)
    exception_handler.setFormatter(advanced_formatter)
    exception_handler.setLevel(logging.ERROR)
    exception_handler.addFilter(SpecificLevelFilter(logging.ERROR))

    stdout_handler = logging.StreamHandler()
    stdout_handler.setFormatter(normal_formatter)
    stdout_handler.setLevel(logging.INFO)

    logger.addHandler(debug_handler)
    logger.addHandler(info_handler)
    logger.addHandler(warning_handler)
    logger.addHandler(stdout_handler)
    logger.addHandler(exception_handler)

    logger.debug("Initialize logger")
