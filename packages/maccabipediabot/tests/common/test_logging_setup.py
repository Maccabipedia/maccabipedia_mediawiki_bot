import logging

from maccabipediabot.common.logging_setup import setup_logging, DEFAULT_FORMAT


def test_setup_logging_applies_level_and_format():
    root = logging.getLogger()
    previous_level = root.level
    previous_handlers = list(root.handlers)
    try:
        for handler in list(root.handlers):
            root.removeHandler(handler)
        setup_logging(level=logging.WARNING)
        assert root.level == logging.WARNING
        assert any(
            isinstance(handler, logging.StreamHandler)
            and handler.formatter is not None
            and handler.formatter._fmt == DEFAULT_FORMAT
            for handler in root.handlers
        )
    finally:
        for handler in list(root.handlers):
            root.removeHandler(handler)
        for handler in previous_handlers:
            root.addHandler(handler)
        root.setLevel(previous_level)


def test_setup_logging_accepts_custom_format():
    root = logging.getLogger()
    previous_level = root.level
    previous_handlers = list(root.handlers)
    try:
        for handler in list(root.handlers):
            root.removeHandler(handler)
        setup_logging(level=logging.INFO, format='%(message)s')
        assert any(
            handler.formatter is not None and handler.formatter._fmt == '%(message)s'
            for handler in root.handlers
        )
    finally:
        for handler in list(root.handlers):
            root.removeHandler(handler)
        for handler in previous_handlers:
            root.addHandler(handler)
        root.setLevel(previous_level)
