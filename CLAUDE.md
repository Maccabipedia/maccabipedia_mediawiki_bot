# Maccabipedia MediaWiki Bot — Claude Code Guide

## 1. Script Execution
- **NEVER use `python3 -c`**, `python -c`, or any inline Python. No exceptions. Not even one-liners.
- **NEVER use multiline bash commands**, heredocs (`<< 'EOF'`), or commands containing `#` comments.
- **Always write scripts and temp data to files**, not inline. Use the Write tool to create the file, then `Bash` to run it. With worktrees, each session has its own working directory so files stay isolated.
- To open files/URLs: `bash .claude/scripts/open-in-browser.sh <url-or-path>`

## 2. Environment
- Running scripts requires `MACCABIPEDIA_UA_SCRIPT` env var — set in `settings.json` env. Pywikibot reads credentials from `user-password.py` directly; never use `source ~/.secrets`.

## 3. Git Workflow
- **Always work on a feature branch.** Nothing is committed directly to `master`; everything goes through a PR.
- **Use worktrees** for feature branches to avoid collisions between parallel sessions. Hooks in `.claude/hooks/` automatically create worktrees at `../maccabipedia_mediawikibot-wt/<name>/` with config and venv.
- Before any `git add`, run `git status` and review every file. Only stage files directly related to the current task.

## 4. Lessons Learned

### Always validate API responses before parsing
Cargo Export returns HTML error pages on internal errors — not JSON. Always check `response.status_code == 200` and `'application/json' in response.headers.get('Content-Type', '')` before calling `.json()`. Log the raw response on failure.

### Use football bot as reference template for other sports
When implementing a feature for volleyball/basketball, always inspect the equivalent football implementation first and use it as the reference.

### Hebrew files opened in Windows apps need UTF-8 BOM
Use `utf-8-sig` encoding when writing CSV/TXT/JSON files with Hebrew text that may be opened in Excel or other Windows apps.

### Never use pywikibot's file_page.upload() — use requests directly
Produces malformed HTTP (bad MIME headers, LF-only line endings) → Apache 400. Use `requests.post(..., files=...)` with pywikibot session cookies. Reference: `upload_basketball_tickets.py` → `_upload_file_via_requests()`.

## 5. Reference Files
- `.claude/maccabipedia_structure_knowledge.md` — Game pages, player pages, templates, Cargo API
- `.claude/maccabipedia_research_sources.md` — External data sources: rosters, match results, historical records, photos, video
- `.claude/maccabistats_knowledge.md` — maccabistats Python package API reference
