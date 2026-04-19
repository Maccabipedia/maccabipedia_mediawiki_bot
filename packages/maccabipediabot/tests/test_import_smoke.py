"""Every submodule under maccabipediabot must import cleanly.

Catches module-scope NameError / ImportError / SyntaxError that would
otherwise only surface at CI runtime (see PR that added this file).
"""
import importlib
import pkgutil

import pytest

import maccabipediabot


# Pywikibot config files (user-config.py, user-password.py) live inside the
# package for deployment, but they're executed by pywikibot in a prepared
# namespace — importing them directly raises NameError on undefined vars.
_EXCLUDED_PREFIXES = ("maccabipediabot.pywikibot_configs",)

# Missing optional dep (openpyxl); tracked separately, excluded from smoke.
_EXCLUDED_MODULES = {
    "maccabipediabot.maintenance.videos.extract_links",
}


def _all_submodules() -> list[str]:
    return [
        info.name
        for info in pkgutil.walk_packages(
            maccabipediabot.__path__, prefix="maccabipediabot."
        )
        if not info.name.startswith(_EXCLUDED_PREFIXES)
        and info.name not in _EXCLUDED_MODULES
    ]


@pytest.mark.parametrize("module_name", _all_submodules())
def test_module_imports(module_name: str) -> None:
    importlib.import_module(module_name)
