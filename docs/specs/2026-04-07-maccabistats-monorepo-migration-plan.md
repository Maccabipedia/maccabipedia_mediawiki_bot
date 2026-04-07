# Maccabistats Monorepo Migration — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Absorb the standalone maccabistats repository into this monorepo as `packages/maccabistats`, preserving full git history, converting to pyproject.toml, wiring as a workspace dependency, migrating CI workflows, and verifying everything works.

**Architecture:** Use `git subtree add` to merge the maccabistats repo under `packages/maccabistats/` with full history. Convert from `setup.py` to `pyproject.toml` with dynamic versioning. Wire as a uv workspace member so `maccabipediabot` uses the local code instead of PyPI.

**Tech Stack:** git subtree, uv workspaces, setuptools, GitHub Actions

**Spec:** `docs/specs/2026-04-07-maccabistats-monorepo-migration-design.md`

---

## File Map

### Files created
- `packages/maccabistats/pyproject.toml` — new build config replacing setup.py
- `packages/maccabistats/src/maccabistats/github_actions_scripts/__init__.py` — required for `python -m` invocation
- `.github/workflows/show_maccabipedia_errors.yaml` — migrated error-finder workflow
- `.github/workflows/upload_maccabipedia_games_to_maccabipedia_ftp.yaml` — migrated FTP upload workflow

### Files modified
- `pyproject.toml` (root) — add maccabistats tests to testpaths
- `packages/maccabipediabot/pyproject.toml` — change maccabistats dependency to workspace-local
- `.gitignore` (root) — add `*.games` and `.wheels/`
- `packages/maccabistats/src/maccabistats/github_actions_scripts/find_maccabipedia_errors.py` — fix ROOT_FOLDER path

### Files deleted (cleanup)
- `packages/maccabistats/setup.py`
- `packages/maccabistats/MANIFEST.in`
- `packages/maccabistats/.github/` (entire directory)
- `packages/maccabistats/.gitignore`
- `packages/maccabistats/.gitattributes`
- `packages/maccabistats/scripts/` (obsolete batch files: `create_wheel.bat`, `run_mypy.bat`)

---

## Task 1: Git subtree merge

**Context:** This is the foundational step. `git subtree add` fetches the maccabistats repo and replays all its commits under the `packages/maccabistats/` prefix. After this, `git log packages/maccabistats/` shows the full history.

- [ ] **Step 1: Verify no LFS pointers in maccabistats**

Run:
```bash
git ls-remote https://github.com/Maccabipedia/maccabistats.git
```
Then:
```bash
git clone --bare https://github.com/Maccabipedia/maccabistats.git /tmp/maccabistats-check && cd /tmp/maccabistats-check && git lfs ls-files 2>&1; cd -
```
Expected: Either "git lfs not installed" or empty output (no LFS objects). The `.gitattributes` has a stale LFS entry for `maccabistats/stats/maccabi.games` (pre-src-layout path) — this is dead and safe to delete later.

- [ ] **Step 2: Run git subtree add**

Run from the repo root:
```bash
git subtree add --prefix=packages/maccabistats https://github.com/Maccabipedia/maccabistats.git master
```
Expected: Git fetches the remote, creates a merge commit. You should see output like:
```
git fetch https://github.com/Maccabipedia/maccabistats.git master
...
Added dir 'packages/maccabistats'
```

- [ ] **Step 3: Verify the subtree landed correctly**

Run:
```bash
ls packages/maccabistats/
```
Expected: You should see `src/`, `tests/`, `setup.py`, `MANIFEST.in`, `README.md`, `CHANGELOG.md`, `.github/`, `.gitignore`, `.gitattributes`, `scripts/`.

Run:
```bash
git log --oneline packages/maccabistats/ | head -5
```
Expected: You see historical maccabistats commits (not just the merge commit).

---

## Task 2: Convert setup.py to pyproject.toml

**Files:**
- Create: `packages/maccabistats/pyproject.toml`
- Delete: `packages/maccabistats/setup.py`, `packages/maccabistats/MANIFEST.in`

- [ ] **Step 1: Create pyproject.toml**

Write `packages/maccabistats/pyproject.toml`:

```toml
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[project]
name = "maccabistats"
dynamic = ["version"]
requires-python = ">=3.11"
license = "MIT"
description = "Maccabi tel-aviv football team statistics manipulation."
dependencies = [
    "requests>=2.28,<3",
    "beautifulsoup4>=4.12,<5",
    "lxml>=4.9.1,<5",
    "python-dateutil>=2.7,<3",
    "matplotlib>=3.6.0,<4",
    "progressbar2>=4.0.0,<5",
]

[project.urls]
Repository = "https://github.com/Maccabipedia/maccabipedia_mediawikibot"
MaccabiPedia = "https://www.maccabipedia.co.il"

[tool.setuptools.dynamic]
version = {attr = "maccabistats.version.version"}

[tool.setuptools.packages.find]
where = ["src"]

[tool.setuptools.package-data]
maccabistats = ["**/*.json", "**/*.md"]
```

- [ ] **Step 2: Delete setup.py and MANIFEST.in**

Run:
```bash
rm packages/maccabistats/setup.py packages/maccabistats/MANIFEST.in
```

- [ ] **Step 3: Verify version resolves**

Run:
```bash
uv run python -c "import importlib.metadata; print(importlib.metadata.version('maccabistats'))"
```
Expected: `2.53` (or current version from `src/maccabistats/version.py`)

Note: This may not work until after `uv sync` in Task 5. If it fails here, verify after Task 5.

- [ ] **Step 4: Commit**

```bash
git add packages/maccabistats/pyproject.toml
git rm packages/maccabistats/setup.py packages/maccabistats/MANIFEST.in
git commit -m "refactor: convert maccabistats from setup.py to pyproject.toml

Use dynamic version from version.py, add package-data for JSON/MD files.
Matches monorepo conventions (setuptools backend, src layout)."
```

---

## Task 3: Wire workspace dependency and update root config

**Files:**
- Modify: `packages/maccabipediabot/pyproject.toml`
- Modify: `pyproject.toml` (root)

- [ ] **Step 1: Change maccabipediabot dependency to workspace-local**

In `packages/maccabipediabot/pyproject.toml`, replace:
```
    "maccabistats>=2.50",
```
with:
```
    "maccabistats",
```

This tells uv to resolve `maccabistats` from the local workspace member at `packages/maccabistats/` instead of PyPI.

- [ ] **Step 2: Add maccabistats tests to root pytest config**

In the root `pyproject.toml`, change the `testpaths` to:
```toml
[tool.pytest.ini_options]
testpaths = [
    "packages/maccabipediabot/tests",
    "packages/maccabipedia-mcp/tests",
    "packages/maccabistats/tests",
]
```

- [ ] **Step 3: Commit**

```bash
git add packages/maccabipediabot/pyproject.toml pyproject.toml
git commit -m "refactor: wire maccabistats as workspace dependency

Replace PyPI maccabistats>=2.50 with local workspace member.
Add maccabistats/tests to root pytest testpaths."
```

---

## Task 4: Cleanup subtree artifacts

**Files:**
- Delete: `packages/maccabistats/.github/`, `packages/maccabistats/.gitignore`, `packages/maccabistats/.gitattributes`, `packages/maccabistats/scripts/`
- Modify: `.gitignore` (root)

- [ ] **Step 1: Add `*.games` and `.wheels/` to root .gitignore**

Append to the root `.gitignore` (before the `# AI Agents` section):

```
# Maccabistats
*.games
.wheels/
```

These were in the maccabistats-level `.gitignore` that we're about to delete. `*.games` files are serialized pickle data (can be 50+ MB).

- [ ] **Step 2: Delete conflicting/obsolete files**

Run:
```bash
rm -rf packages/maccabistats/.github
rm packages/maccabistats/.gitignore
rm packages/maccabistats/.gitattributes
rm -rf packages/maccabistats/scripts
```

- [ ] **Step 3: Verify nothing important was deleted**

Run:
```bash
ls packages/maccabistats/
```
Expected remaining: `CHANGELOG.md`, `README.md`, `pyproject.toml`, `src/`, `tests/`

- [ ] **Step 4: Commit**

```bash
git add .gitignore
git rm -r packages/maccabistats/.github packages/maccabistats/.gitignore packages/maccabistats/.gitattributes packages/maccabistats/scripts
git commit -m "chore: cleanup maccabistats subtree artifacts

Remove .github/ (workflows migrated separately), .gitignore (covered by
root), .gitattributes (stale LFS entry), scripts/ (obsolete batch files).
Add *.games and .wheels/ to root .gitignore."
```

---

## Task 5: Regenerate lock file and verify basic functionality

- [ ] **Step 1: Run uv sync**

Run:
```bash
uv sync
```
Expected: Resolves successfully. `maccabistats` should appear as a workspace member in the output, not fetched from PyPI.

- [ ] **Step 2: Verify maccabistats imports**

Run:
```bash
uv run python -c "from maccabistats import get_maccabi_stats; print('maccabistats OK')"
```
Expected: `maccabistats OK`

Run:
```bash
uv run python -c "from maccabistats.version import version; print(f'version: {version}')"
```
Expected: `version: 2.53`

- [ ] **Step 3: Verify maccabipediabot still imports maccabistats**

Run:
```bash
uv run python -c "import maccabistats; print(type(maccabistats)); print('cross-package OK')"
```
Expected: Shows the module type and `cross-package OK`

- [ ] **Step 4: Run existing monorepo tests (maccabipediabot + maccabipedia-mcp only)**

Run:
```bash
uv run pytest packages/maccabipediabot/tests packages/maccabipedia-mcp/tests -v
```
Expected: All 52 existing tests pass. This confirms the workspace dependency change didn't break anything.

- [ ] **Step 5: Commit lock file**

```bash
git add uv.lock
git commit -m "chore: regenerate uv.lock with maccabistats as workspace member"
```

---

## Task 6: Fix broken ROOT_FOLDER path in find_maccabipedia_errors.py

**Files:**
- Modify: `packages/maccabistats/src/maccabistats/github_actions_scripts/find_maccabipedia_errors.py`

**Context:** The script computes `ROOT_FOLDER` at module scope using `Path(__file__).absolute().parent.parent.parent.parent`. In the standalone repo, four `.parent` calls from `src/maccabistats/github_actions_scripts/find_maccabipedia_errors.py` reach the repo root. After migration to `packages/maccabistats/src/maccabistats/github_actions_scripts/`, four `.parent` calls only reach `packages/maccabistats/` — not the workspace root. The Telegram action looks for output files at the workspace root.

- [ ] **Step 1: Edit find_maccabipedia_errors.py**

In `packages/maccabistats/src/maccabistats/github_actions_scripts/find_maccabipedia_errors.py`, replace the module-level `ROOT_FOLDER` and `BASE_LOG_FILE_NAME` lines:

Replace:
```python
import logging
from datetime import datetime
from logging import FileHandler
from pathlib import Path

from maccabistats import load_from_maccabipedia_source, ErrorsFinder
from maccabistats.maccabilogging import remove_live_logging
from maccabistats.stats.maccabi_games_stats import MaccabiGamesStats

ROOT_FOLDER = Path(__file__).absolute().parent.parent.parent.parent
BASE_LOG_FILE_NAME = ROOT_FOLDER / f'{datetime.now().strftime("%Y_%m_%d")}__maccabipedia_errors'
```

With:
```python
import logging
import subprocess
from datetime import datetime
from logging import FileHandler
from pathlib import Path

from maccabistats import load_from_maccabipedia_source, ErrorsFinder
from maccabistats.maccabilogging import remove_live_logging
from maccabistats.stats.maccabi_games_stats import MaccabiGamesStats


def _get_repo_root() -> Path:
    return Path(subprocess.check_output(
        ['git', 'rev-parse', '--show-toplevel'], text=True
    ).strip())
```

Then in the `show_all_errors()` function, replace:
```python
def show_all_errors() -> None:
    remove_live_logging()
    logging.info('Loading MaccabiPedia games, official games only, no friendly games')
    maccabipedia_games = load_from_maccabipedia_source().official_games
    logging.info(f'Loaded MaccabiPedia games: {maccabipedia_games}')

    old_games_file_handler = FileHandler(f'{BASE_LOG_FILE_NAME}_before_1950.txt', encoding='utf8')
```

With:
```python
def show_all_errors() -> None:
    remove_live_logging()

    root_folder = _get_repo_root()
    base_log_file_name = root_folder / f'{datetime.now().strftime("%Y_%m_%d")}__maccabipedia_errors'

    logging.info('Loading MaccabiPedia games, official games only, no friendly games')
    maccabipedia_games = load_from_maccabipedia_source().official_games
    logging.info(f'Loaded MaccabiPedia games: {maccabipedia_games}')

    old_games_file_handler = FileHandler(f'{base_log_file_name}_before_1950.txt', encoding='utf8')
```

Also update the second FileHandler reference later in the same function. Replace:
```python
    new_games_file_handler = FileHandler(f'{BASE_LOG_FILE_NAME}_after_1950.txt', encoding='utf8')
```

With:
```python
    new_games_file_handler = FileHandler(f'{base_log_file_name}_after_1950.txt', encoding='utf8')
```

- [ ] **Step 2: Verify the module imports without side effects**

Run:
```bash
uv run python -c "import maccabistats.github_actions_scripts.find_maccabipedia_errors; print('import OK')"
```
Expected: This should FAIL because `github_actions_scripts` has no `__init__.py`. That's fixed in Task 7. For now, just verify the file has no syntax errors:
```bash
uv run python -c "
import ast
ast.parse(open('packages/maccabistats/src/maccabistats/github_actions_scripts/find_maccabipedia_errors.py').read())
print('syntax OK')
"
```
Expected: `syntax OK`

- [ ] **Step 3: Commit**

```bash
git add packages/maccabistats/src/maccabistats/github_actions_scripts/find_maccabipedia_errors.py
git commit -m "fix: use git rev-parse for ROOT_FOLDER in find_maccabipedia_errors

The old Path(__file__).parent chain breaks after moving into the monorepo
(reaches packages/maccabistats/ instead of workspace root). Use git
rev-parse --show-toplevel which works regardless of directory depth.
Moved to function body to keep imports side-effect-free."
```

---

## Task 7: Create __init__.py for github_actions_scripts and migrate CI workflows

**Files:**
- Create: `packages/maccabistats/src/maccabistats/github_actions_scripts/__init__.py`
- Create: `.github/workflows/show_maccabipedia_errors.yaml`
- Create: `.github/workflows/upload_maccabipedia_games_to_maccabipedia_ftp.yaml`

**Context:** The `github_actions_scripts` directory does NOT have an `__init__.py` in the original repo. We need one so that `python -m maccabistats.github_actions_scripts.find_maccabipedia_errors` works (the monorepo convention is `python -m` invocation, not direct script paths).

- [ ] **Step 1: Create __init__.py**

Write an empty `packages/maccabistats/src/maccabistats/github_actions_scripts/__init__.py`:

```python
```

(Empty file — just needs to exist for Python package discovery.)

- [ ] **Step 2: Verify module import now works**

Run:
```bash
uv run python -c "import maccabistats.github_actions_scripts.find_maccabipedia_errors; print('import OK')"
uv run python -c "import maccabistats.github_actions_scripts.fetch_games_from_maccabipedia; print('import OK')"
uv run python -c "import maccabistats.github_actions_scripts.upload_maccabipedia_games_to_ftp; print('import OK')"
```
Expected: All three print `import OK`. (The find_maccabipedia_errors import should NOT trigger the git rev-parse call since we moved it into the function body.)

- [ ] **Step 3: Create show_maccabipedia_errors.yaml**

Write `.github/workflows/show_maccabipedia_errors.yaml`:

```yaml
name: Find MaccabiPedia Errors
on:
  schedule:
    - cron: "0 18 * * *"
  workflow_dispatch:

jobs:
  maccabipedia-errors:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: 3.11
          architecture: x64
      - uses: astral-sh/setup-uv@v6
      - name: Install dependencies
        run: uv sync
      - name: Fetch MaccabiPedia Data
        run: uv run python -m maccabistats.github_actions_scripts.fetch_games_from_maccabipedia
      - name: Find Errors
        run: uv run python -m maccabistats.github_actions_scripts.find_maccabipedia_errors
      - name: Get current date
        id: date
        run: echo "date=$(date +'%Y_%m_%d')" >> $GITHUB_OUTPUT
      - name: Send Errors to Telegram (before 1950)
        uses: appleboy/telegram-action@v2.25.0
        with:
          to: ${{ secrets.MACCABIPEDIA_ERRORS_TELEGRAM_TO }}
          token: ${{ secrets.MACCABIPEDIA_ERRORS_TELEGRAM_TOKEN }}
          message: MaccabiPedia errors for game before 1950
          document: ${{ steps.date.outputs.date }}__maccabipedia_errors_before_1950.txt
      - name: Send Errors to Telegram (After 1950)
        uses: appleboy/telegram-action@v2.25.0
        with:
          to: ${{ secrets.MACCABIPEDIA_ERRORS_TELEGRAM_TO }}
          token: ${{ secrets.MACCABIPEDIA_ERRORS_TELEGRAM_TOKEN }}
          message: MaccabiPedia errors for game after 1950
          document: ${{ steps.date.outputs.date }}__maccabipedia_errors_after_1950.txt
  workflow-keepalive:
    if: github.event_name == 'schedule'
    runs-on: ubuntu-latest
    permissions:
      actions: write
    steps:
      - uses: liskin/gh-workflow-keepalive@v1
```

Note the changes from the original:
- Python 3.11 (was 3.7)
- `astral-sh/setup-uv@v6` + `uv sync` (was pip install)
- `uv run python -m ...` (was `python src/maccabistats/...`)
- `echo "date=..." >> $GITHUB_OUTPUT` (was deprecated `::set-output`)
- `appleboy/telegram-action@v2.25.0` (was `@master`)
- Added `workflow-keepalive` job

- [ ] **Step 4: Create upload_maccabipedia_games_to_maccabipedia_ftp.yaml**

Write `.github/workflows/upload_maccabipedia_games_to_maccabipedia_ftp.yaml`:

```yaml
name: Upload MaccabiPedia Games FTP
on:
  schedule:
    - cron: "0 20 * * *"
  workflow_dispatch:

jobs:
  maccabipedia-games-to-maccabipedia-host:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: 3.11
          architecture: x64
      - uses: astral-sh/setup-uv@v6
      - name: Install dependencies
        run: uv sync
      - name: Fetch MaccabiPedia Data
        run: uv run python -m maccabistats.github_actions_scripts.fetch_games_from_maccabipedia
      - name: Upload Games File To MaccabiPedia FTP
        env:
          MACCABIPEDIA_FTP: ${{ secrets.MACCABIPEDIA_FTP }}
          MACCABIPEDIA_FTP_USERNAME: ${{ secrets.MACCABIPEDIA_FTP_USERNAME }}
          MACCABIPEDIA_FTP_PASSWORD: ${{ secrets.MACCABIPEDIA_FTP_PASSWORD }}
        run: uv run python -m maccabistats.github_actions_scripts.upload_maccabipedia_games_to_ftp
      - name: Notify Telegram Latest Games Uploaded
        uses: appleboy/telegram-action@v2.25.0
        with:
          to: ${{ secrets.MACCABIPEDIA_ERRORS_TELEGRAM_TO }}
          token: ${{ secrets.MACCABIPEDIA_ERRORS_TELEGRAM_TOKEN }}
          message: Latest MaccabiPedia games uploaded to our FTP
  workflow-keepalive:
    if: github.event_name == 'schedule'
    runs-on: ubuntu-latest
    permissions:
      actions: write
    steps:
      - uses: liskin/gh-workflow-keepalive@v1
```

- [ ] **Step 5: Verify workflow YAML is valid**

Run:
```bash
uv run python -c "
import yaml
for f in ['.github/workflows/show_maccabipedia_errors.yaml', '.github/workflows/upload_maccabipedia_games_to_maccabipedia_ftp.yaml']:
    yaml.safe_load(open(f))
    print(f'{f}: valid YAML')
"
```
Expected: Both files report valid YAML. (If `yaml` module is not available, install it: `uv add --dev pyyaml` or just validate with `python -c "import json, yaml"` won't work — in that case use an online YAML validator or skip this check.)

Alternative without pyyaml:
```bash
uv run python -c "
import ast, json
# Just verify the files exist and are non-empty
from pathlib import Path
for f in ['show_maccabipedia_errors.yaml', 'upload_maccabipedia_games_to_maccabipedia_ftp.yaml']:
    p = Path('.github/workflows') / f
    assert p.exists(), f'{f} not found'
    assert p.stat().st_size > 100, f'{f} seems empty'
    print(f'{f}: exists ({p.stat().st_size} bytes)')
"
```

- [ ] **Step 6: Commit**

```bash
git add packages/maccabistats/src/maccabistats/github_actions_scripts/__init__.py
git add .github/workflows/show_maccabipedia_errors.yaml
git add .github/workflows/upload_maccabipedia_games_to_maccabipedia_ftp.yaml
git commit -m "feat: migrate maccabistats CI workflows to monorepo

Add __init__.py to github_actions_scripts for python -m invocation.
Convert both workflows: Python 3.11, uv, pinned telegram action,
keepalive jobs, modern GITHUB_OUTPUT syntax."
```

---

## Task 8: Final verification

- [ ] **Step 1: Run ALL tests across all three packages**

Run:
```bash
uv run pytest -v
```
Expected: All tests pass — the original 52 (maccabipediabot + maccabipedia-mcp) plus the maccabistats tests. Note: maccabistats tests make live HTTP calls to MaccabiPedia's Cargo API, so this requires network access and will be slower.

If maccabistats tests fail due to network issues (MaccabiPedia down, rate limiting, etc.), that's not a migration problem. Verify the existing 52 tests pass and that the maccabistats test failures are network-related, not import/path-related.

- [ ] **Step 2: Verify all module entry points resolve**

Run:
```bash
uv run python -c "import maccabistats.github_actions_scripts.find_maccabipedia_errors; print('1 OK')"
uv run python -c "import maccabistats.github_actions_scripts.fetch_games_from_maccabipedia; print('2 OK')"
uv run python -c "import maccabistats.github_actions_scripts.upload_maccabipedia_games_to_ftp; print('3 OK')"
```
Expected: All three print OK without errors or side effects (no git commands, no network calls).

- [ ] **Step 3: Verify cross-package dependency**

Run:
```bash
uv run python -c "
from maccabistats.version import version
print(f'maccabistats version: {version}')
import maccabipediabot
print('maccabipediabot imports OK (uses workspace maccabistats)')
"
```
Expected: Shows version and confirms maccabipediabot imports work.

- [ ] **Step 4: Verify git history is preserved**

Run:
```bash
git log --oneline packages/maccabistats/ | head -10
```
Expected: Shows historical maccabistats commits (version bumps, feature additions, etc.), not just the migration commits.

- [ ] **Step 5: Review all changes**

Run:
```bash
git log --oneline master..HEAD
```
Expected: You should see approximately these commits (newest first):
1. `feat: migrate maccabistats CI workflows to monorepo`
2. `chore: regenerate uv.lock with maccabistats as workspace member`
3. `chore: cleanup maccabistats subtree artifacts`
4. `refactor: wire maccabistats as workspace dependency`
5. `refactor: convert maccabistats from setup.py to pyproject.toml`
6. `fix: use git rev-parse for ROOT_FOLDER in find_maccabipedia_errors`
7. The subtree merge commit
8. (Plus the spec commits from earlier)

Verify no untracked files are left behind:
```bash
git status
```
Expected: Clean working tree.
