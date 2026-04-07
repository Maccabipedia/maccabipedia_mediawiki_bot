# Design: Migrate maccabistats into monorepo

## Summary

Absorb the [Maccabipedia/maccabistats](https://github.com/Maccabipedia/maccabistats) repository into this monorepo as `packages/maccabistats`, preserving full git history. Convert it from `setup.py` to `pyproject.toml`, wire it as a workspace dependency, migrate its CI workflows, and verify everything works.

## Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| History preservation | Yes, via `git subtree add` | Standard approach; replays all commits under `packages/maccabistats/` |
| Package build config | Convert `setup.py` → `pyproject.toml` | Match monorepo conventions (setuptools backend, src layout) |
| Workspace dependency | Local, not PyPI | maccabipediabot depends on workspace `maccabistats` directly |
| CI workflows | Move and adapt to monorepo style | Use `uv run`, Python 3.11, monorepo paths |
| Hardcoded paths/config | Leave as-is (except where migration breaks them) | Migrate faithfully first, refactor later. Fix paths that break due to directory depth change. |
| Original repo | Decide later | Focus on migration now |
| Version source of truth | Dynamic from `version.py` | Single source of truth via `[tool.setuptools.dynamic]` |

## Step 1: Git subtree merge

```bash
git subtree add --prefix=packages/maccabistats \
  https://github.com/Maccabipedia/maccabistats.git master
```

This creates a merge commit that brings the entire maccabistats history into `packages/maccabistats/`. Every historical commit is preserved and reachable via `git log packages/maccabistats/`.

**Pre-check:** Run `git lfs ls-files` on the maccabistats repo to confirm no LFS pointers exist (the `.gitattributes` has a stale LFS entry for a pre-src-layout path that is no longer valid).

## Step 2: Convert setup.py to pyproject.toml

**Delete:** `packages/maccabistats/setup.py`, `packages/maccabistats/MANIFEST.in`

**Create:** `packages/maccabistats/pyproject.toml`

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

Version is read dynamically from `src/maccabistats/version.py` (single source of truth). Package data includes JSON files (`achievements.json`, `players_by_titles.json`, `titles_by_season.json`) and markdown files used by the package.

## Step 3: Wire workspace dependency

**`packages/maccabipediabot/pyproject.toml`** — replace:
```
"maccabistats>=2.50",
```
with:
```
"maccabistats",
```

uv resolves this to the local workspace package automatically (same as how `maccabipedia-mcp` works — any package in `packages/*` is a workspace member).

## Step 4: Update root pyproject.toml

Add maccabistats tests to pytest config:

```toml
[tool.pytest.ini_options]
testpaths = [
    "packages/maccabipediabot/tests",
    "packages/maccabipedia-mcp/tests",
    "packages/maccabistats/tests",
]
```

No change needed to `[tool.uv.workspace]` — `members = ["packages/*"]` already picks up the new package.

## Step 5: Migrate CI workflows

Move both workflows from `packages/maccabistats/.github/workflows/` into `.github/workflows/`, adapting them to match the monorepo pattern (reference: `update_league_table_status.yaml`).

### 5a: show_maccabipedia_errors.yaml

**Current:** Python 3.7, pip install, runs `fetch_games_from_maccabipedia.py` then `find_maccabipedia_errors.py`

**Migrated:**
- Python 3.11 + `astral-sh/setup-uv@v6`
- `uv sync` instead of pip
- Step 1: `uv run python -m maccabistats.github_actions_scripts.fetch_games_from_maccabipedia`
- Step 2: `uv run python -m maccabistats.github_actions_scripts.find_maccabipedia_errors`
- Same cron schedule (daily 18:00 UTC) + workflow_dispatch
- Telegram notification steps using `appleboy/telegram-action@v2.25.0` (pinned version)
- Secrets: `MACCABIPEDIA_ERRORS_TELEGRAM_TOKEN`, `MACCABIPEDIA_ERRORS_TELEGRAM_TO`
- Keepalive job (matching monorepo pattern)

### 5b: upload_maccabipedia_games_to_maccabipedia_ftp.yaml

**Current:** Python 3.7, pip install, runs `fetch_games_from_maccabipedia.py` then `upload_maccabipedia_games_to_ftp.py`

**Migrated:**
- Same uv-based setup as above
- Step 1: `uv run python -m maccabistats.github_actions_scripts.fetch_games_from_maccabipedia`
- Step 2: `uv run python -m maccabistats.github_actions_scripts.upload_maccabipedia_games_to_ftp`
- Same cron schedule (daily 20:00 UTC) + workflow_dispatch
- FTP secrets + Telegram notification
- Keepalive job (matching monorepo pattern)

### Required GitHub secrets (manual step)

These secrets must be added to the monorepo's GitHub settings (names match the original maccabistats repo):
- `MACCABIPEDIA_ERRORS_TELEGRAM_TOKEN` — Telegram bot token for error notifications
- `MACCABIPEDIA_ERRORS_TELEGRAM_TO` — Telegram chat ID for error notifications
- `MACCABIPEDIA_FTP` — FTP server hostname
- `MACCABIPEDIA_FTP_USERNAME` — FTP username
- `MACCABIPEDIA_FTP_PASSWORD` — FTP password

## Step 6: Fix broken path in find_maccabipedia_errors.py

The error-finder script computes its output directory via:
```python
ROOT_FOLDER = Path(__file__).absolute().parent.parent.parent.parent
```

In the standalone repo, this resolves to the repo root. After migration to `packages/maccabistats/src/maccabistats/github_actions_scripts/`, four `.parent` calls only reach `packages/maccabistats/` — not the workspace root. The Telegram action step looks for the output file at the workspace root.

**Fix:** Move `ROOT_FOLDER` computation out of module scope and into the function body (e.g., inside `show_all_errors()`), using `git rev-parse --show-toplevel`:
```python
def _get_repo_root() -> Path:
    return Path(subprocess.check_output(
        ['git', 'rev-parse', '--show-toplevel'], text=True
    ).strip())
```

This keeps imports side-effect-free (important for verification step 9c) and only runs the git command when the script is actually executed. Works both locally and in CI, and is resilient to further directory moves.

## Step 7: Cleanup subtree artifacts

After the subtree merge, remove files from `packages/maccabistats/` that conflict with or duplicate monorepo-level config:

- `packages/maccabistats/.github/` — workflows moved to monorepo level
- `packages/maccabistats/.gitignore` — monorepo root `.gitignore` covers this (after adding `*.games` — see below)
- `packages/maccabistats/.gitattributes` — stale LFS entry for pre-src-layout path; no active LFS pointers
- `packages/maccabistats/setup.py` — replaced by pyproject.toml
- `packages/maccabistats/MANIFEST.in` — not needed with pyproject.toml
- `packages/maccabistats/scripts/` — contains only obsolete Windows batch files (`create_wheel.bat`, `run_mypy.bat`); not needed in a uv monorepo

**Add to root `.gitignore`:**
```
*.games
.wheels/
```

The maccabistats `.gitignore` had these entries. Without them, serialized `.games` files (can be 50+ MB) could be accidentally committed.

**Keep:**
- `README.md`, `CHANGELOG.md` — package-level documentation
- `src/` — all source code as-is
- `tests/` — test suite

## Step 8: Regenerate lock file

```bash
uv sync
```

This resolves `maccabistats` as a workspace package and updates `uv.lock`.

## Step 9: Verification

### 9a: Tests
```bash
uv run pytest  # All tests across all 3 packages
```

### 9b: Import check
```bash
uv run python -c "from maccabistats import get_maccabi_stats; print('OK')"
uv run python -c "from maccabipediabot.common import maccabipedia_bot; print('OK')"
```

### 9c: Workflow validation
- Verify all workflow YAML files parse correctly
- For each migrated workflow, confirm the entry-point module resolves:
  ```bash
  uv run python -c "import maccabistats.github_actions_scripts.find_maccabipedia_errors"
  uv run python -c "import maccabistats.github_actions_scripts.fetch_games_from_maccabipedia"
  uv run python -c "import maccabistats.github_actions_scripts.upload_maccabipedia_games_to_ftp"
  ```

### 9d: Post-merge manual verification
After the PR is merged, manually trigger each migrated workflow via GitHub Actions `workflow_dispatch` to confirm end-to-end execution with secrets.

## Out of scope

- Refactoring hardcoded paths (`~/maccabistats/logs/`, config paths) — except `ROOT_FOLDER` which breaks due to migration
- Archiving or modifying the original maccabistats GitHub repo
- Publishing maccabistats to PyPI from the monorepo
- Adding linting/type-checking for maccabistats code
