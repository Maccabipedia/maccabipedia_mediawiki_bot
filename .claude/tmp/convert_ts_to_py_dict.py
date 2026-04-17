"""Convert TS const map files to Python dict literals.

Each TS file shape:
    export const NAME: { [key: string]: string } = {
        'key': 'value',
        ...
    }

Output: Python dict literal `{ "key": "value", ... }` with empty entries dropped
and \\' un-escaped to '.
"""
import re
import sys
from pathlib import Path


def parse_ts_dict(ts_path: Path) -> dict[str, str]:
    text = ts_path.read_text(encoding="utf-8")
    out: dict[str, str] = {}
    # Match `'key': 'value',` or "key": "value", with optional trailing comma.
    # Handles single- or double-quoted keys/values; allows escaped quotes inside.
    pattern = re.compile(
        r"""(?:'((?:[^'\\]|\\.)*)'|"((?:[^"\\]|\\.)*)")"""
        r"""\s*:\s*"""
        r"""(?:'((?:[^'\\]|\\.)*)'|"((?:[^"\\]|\\.)*)")"""
        r"""\s*,?"""
    )
    for m in pattern.finditer(text):
        key = (m.group(1) or m.group(2) or "").replace("\\'", "'").replace('\\"', '"')
        value = (m.group(3) or m.group(4) or "").replace("\\'", "'").replace('\\"', '"')
        if not key and not value:
            continue
        if key in out and out[key] != value:
            print(f"  warning: duplicate key {key!r}: {out[key]!r} -> {value!r}", file=sys.stderr)
        out[key] = value
    return out


def render_python_dict(d: dict[str, str], indent: int = 4) -> str:
    """Render as multi-line dict literal with double-quoted keys/values.

    Strings containing " get escaped; otherwise plain double-quoted is used.
    """
    pad = " " * indent
    lines = ["{"]
    for k, v in d.items():
        kq = py_str(k)
        vq = py_str(v)
        lines.append(f"{pad}{kq}: {vq},")
    lines.append("}")
    return "\n".join(lines)


def py_str(s: str) -> str:
    """Render a Python string literal. Prefer double quotes; if value contains ", use single."""
    if '"' in s and "'" not in s:
        return f"'{s}'"
    if '"' in s and "'" in s:
        return '"' + s.replace('"', '\\"') + '"'
    return f'"{s}"'


def convert_int_dict(ts_path: Path) -> dict[int, str]:
    """For basket-game-type-heb-name.ts where keys are ints (no surrounding quotes)."""
    text = ts_path.read_text(encoding="utf-8")
    out: dict[int, str] = {}
    pattern = re.compile(r"(\d+)\s*:\s*'((?:[^'\\]|\\.)*)'\s*,?")
    for m in pattern.finditer(text):
        out[int(m.group(1))] = m.group(2).replace("\\'", "'").replace('\\"', '"')
    return out


def render_int_dict(d: dict[int, str], indent: int = 4) -> str:
    pad = " " * indent
    lines = ["{"]
    for k, v in d.items():
        lines.append(f"{pad}{k}: {py_str(v)},")
    lines.append("}")
    return "\n".join(lines)


if __name__ == "__main__":
    ts_dir = Path(".claude/tmp/ts-source")

    teams = parse_ts_dict(ts_dir / "eng-to-heb-team-name-map.ts")
    persons = parse_ts_dict(ts_dir / "eng-to-heb-person-name-map.ts")
    stadiums = parse_ts_dict(ts_dir / "eng-to-heb-stadium-name-map.ts")
    normalize = parse_ts_dict(ts_dir / "heb-name-normalize-map.ts")
    game_types = convert_int_dict(ts_dir / "basket-game-type-heb-name.ts")

    print("# === TEAMS ===")
    print(f"_TEAM_NAMES: dict[str, str] = {render_python_dict(teams)}")
    print(f"\n# total entries: {len(teams)}\n")

    print("# === PERSONS ===")
    print(f"_PERSON_NAMES: dict[str, str] = {render_python_dict(persons)}")
    print(f"\n# total entries: {len(persons)}\n")

    print("# === STADIUMS ===")
    print(f"_STADIUM_NAMES: dict[str, str] = {render_python_dict(stadiums)}")
    print(f"\n# total entries: {len(stadiums)}\n")

    print("# === NORMALIZE ===")
    print(f"_PLAYER_NAME_NORMALIZE: dict[str, str] = {render_python_dict(normalize)}")
    print(f"\n# total entries: {len(normalize)}\n")

    print("# === BASKET GAME TYPES ===")
    print(f"_BASKET_GAME_TYPE: dict[int, str] = {render_int_dict(game_types)}")
    print(f"\n# total entries: {len(game_types)}\n")
