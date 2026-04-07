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
| Hardcoded paths/config | Leave as-is | Migrate faithfully first, refactor later |
| Original repo | Decide later | Focus on migration now |

## Step 1: Git subtree merge

```bash
git subtree add --prefix=packages/maccabistats \
  https://github.com/Maccabipedia/maccabistats.git master
```

This creates a merge commit that brings the entire maccabistats history into `packages/maccabistats/`. Every historical commit is preserved and reachable via `git log packages/maccabistats/`.

## Step 2: Convert setup.py to pyproject.toml

**Delete:** `packages/maccabistats/setup.py`, `packages/maccabistats/MANIFEST.in`

**Create:** `packages/maccabistats/pyproject.toml`

```toml
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[project]
name = "maccabistats"
version = "2.53"
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

[tool.setuptools.packages.find]
where = ["src"]
```

Keep `src/maccabistats/version.py` — it's imported at runtime by maccabistats code.

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

**Current:** Python 3.7, pip install, runs `github_actions_scripts/find_maccabipedia_errors.py` and `fetch_games_from_maccabipedia.py`

**Migrated:**
- Python 3.11 + `astral-sh/setup-uv@v6`
- `uv sync` instead of pip
- `uv run python -m maccabistats.github_actions_scripts.find_maccabipedia_errors` (or equivalent module path)
- Same cron schedule (daily 18:00 UTC) + workflow_dispatch
- Same Telegram notification steps (secrets: `TELEGRAM_TOKEN`, `TELEGRAM_CHAT_ID`)

### 5b: upload_maccabipedia_games_to_maccabipedia_ftp.yaml

**Current:** Python 3.7, pip install, runs `github_actions_scripts/upload_maccabipedia_games_to_ftp.py` and `fetch_games_from_maccabipedia.py`

**Migrated:**
- Same uv-based setup as above
- `uv run python -m maccabistats.github_actions_scripts.upload_maccabipedia_games_to_ftp`
- Same cron schedule (daily 20:00 UTC) + workflow_dispatch
- Same FTP + Telegram secrets

### Required GitHub secrets (manual step)

These secrets must be added to the monorepo's GitHub settings:
- `TELEGRAM_TOKEN` — Telegram bot token for notifications
- `TELEGRAM_CHAT_ID` — Telegram chat ID for notifications
- `FTP_HOST` — FTP server hostname
- `FTP_USERNAME` — FTP credentials
- `FTP_PASSWORD` — FTP credentials

## Step 6: Cleanup subtree artifacts

After the subtree merge, remove files from `packages/maccabistats/` that conflict with or duplicate monorepo-level config:

- `packages/maccabistats/.github/` — workflows moved to monorepo level
- `packages/maccabistats/.gitignore` — monorepo root `.gitignore` covers this
- `packages/maccabistats/.gitattributes` — monorepo root handles this
- `packages/maccabistats/setup.py` — replaced by pyproject.toml
- `packages/maccabistats/MANIFEST.in` — not needed with pyproject.toml

**Keep:**
- `README.md`, `CHANGELOG.md` — package-level documentation
- `src/` — all source code as-is
- `tests/` — test suite
- `scripts/` — analysis scripts and JSON data files (used by the package)

## Step 7: Regenerate lock file

```bash
uv sync
```

This resolves `maccabistats` as a workspace package and updates `uv.lock`.

## Step 8: Verification

### 8a: Tests
```bash
uv run pytest  # All tests across all 3 packages
```

### 8b: Import check
```bash
uv run python -c "from maccabistats import get_maccabi_stats; print('OK')"
uv run python -c "from maccabipediabot.common import maccabipedia_bot; print('OK')"
```

### 8c: Workflow validation
- Verify all workflow YAML files parse correctly
- For each migrated workflow, run the entry-point module to confirm the module path resolves (e.g. `uv run python -c "import maccabistats.github_actions_scripts.find_maccabipedia_errors"`)

### 8d: Post-merge manual verification
After the PR is merged, manually trigger each migrated workflow via GitHub Actions `workflow_dispatch` to confirm end-to-end execution with secrets.

## Out of scope

- Refactoring hardcoded paths (`~/maccabistats/logs/`, config paths)
- Archiving or modifying the original maccabistats GitHub repo
- Publishing maccabistats to PyPI from the monorepo
- Adding linting/type-checking for maccabistats code
