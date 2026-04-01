# Maccabipedia MediaWiki Bot — Claude Code Guide

## 1. Coding Standards
- Follow PEP 8: `snake_case` for functions/variables, `PascalCase` for classes.
- Every new script must include a docstring explaining what it does, how to run it, and any dependencies.
- Use **`cmd`** for command-line operations — avoid PowerShell syntax (`$env:VAR`, backtick continuations). Use `^` for line continuation.

## 2. Automation & Data Integrity
- **Zero Tolerance for Silent Failures**: treat every discrepancy as an exception.
- **Fail Fast**: never silence exceptions with empty `try/except`. Let scripts crash so errors are visible.
- **Handle Edge Cases**: missing data, network timeouts, invalid wiki syntax.
- **Interactive Verification**: for fuzzy matching or data correction, prefer interactive scripts that cache user decisions.

## 4. Environment
- GitHub CLI is available as `gh.exe` (not `gh`) in WSL.

## 3. Git Hygiene
- **Always work on a feature branch.** Before making any changes — code, docs, or `.claude/` files — check the current branch. If on `master`, create a feature branch first. Nothing is committed directly to `master`; everything goes through a PR.
- Before any `git add`, run `git status` and review every file. Only stage files directly related to the current task.
- At the end of every task involving a git branch, switch back to `master` and confirm the branch is clean.

## 6. Lessons Learned

### Always validate API responses before parsing
Cargo Export returns HTML error pages on internal errors — not JSON. Always check `response.status_code == 200` and `'application/json' in response.headers.get('Content-Type', '')` before calling `.json()`. Log the raw response on failure.

### Use football bot as reference template for other sports
When implementing a feature for volleyball/basketball, always inspect the equivalent football implementation first and use it as the reference.

### Hebrew files opened in Windows apps need UTF-8 BOM
Use `utf-8-sig` encoding when writing CSV/TXT/JSON files with Hebrew text that may be opened in Excel or other Windows apps.

### Never use pywikibot's file_page.upload() — use requests directly
Produces malformed HTTP (bad MIME headers, LF-only line endings) → Apache 400. Use `requests.post(..., files=...)` with pywikibot session cookies. Reference: `upload_basketball_tickets.py` → `_upload_file_via_requests()`.

### Running scripts requires MACCABIPEDIA_UA_SCRIPT env var
ModSecurity WAF blocks unknown user-agent script names. Always: `source ~/.secrets && MACCABIPEDIA_UA_SCRIPT=<name> python script.py`

---

## 7. MaccabiPedia Structure

Read `.claude/maccabipedia_structure_knowledge.md` when working with game pages, player pages, templates, or the Cargo API.

## 8. Research Sources (read when searching for external data)

Read `.claude/maccabipedia_research_sources.md` when you need to find data from external sources — player rosters, match results, historical records, photos, or video for any sport.
