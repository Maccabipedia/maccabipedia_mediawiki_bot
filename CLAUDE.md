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
- **Always work on a feature branch.** Before making any code changes, check the current branch. If on `master`, create a feature branch first.
- Before any `git add`, run `git status` and review every file. Only stage files directly related to the current task.
- At the end of every task involving a git branch, switch back to `master` and confirm the branch is clean.

## 6. Lessons Learned (CRITICAL — read every session)

### Always validate API responses before parsing
Cargo Export returns HTML error pages on internal errors — not JSON. Always check `response.status_code == 200` and `'application/json' in response.headers.get('Content-Type', '')` before calling `.json()`. Log the raw response on failure.

### Use football bot as reference template for other sports
When implementing a feature for volleyball/basketball, always inspect the equivalent football implementation first and use it as the reference.

### Hebrew files opened in Windows apps need UTF-8 BOM
Use `utf-8-sig` encoding when writing CSV/TXT/JSON files with Hebrew text that may be opened in Excel or other Windows apps.

### Unrelated files must not be staged in commits
Files created during experimentation must be cleaned up before staging. Never use `git add .` blindly.

### Switch back to `master` after finishing a feature
After completing and merging a task, always `git checkout master` and confirm the branch is clean.

### Never use pywikibot's file_page.upload() — use requests directly
pywikibot's MIME multipart builder (based on Python's `email.mime` library) produces malformed HTTP requests:
- Adds `MIME-Version: 1.0` to every body part (email header, invalid in HTTP)
- Uses LF-only `\n` line endings instead of CRLF `\r\n` (required by RFC 2046)

Apache returns 400 Bad Request. Use `requests.post(..., files={'file': ('FAKE-NAME', data, mime_type)})` with cookies and CSRF token from pywikibot's session instead. See `upload_basketball_tickets.py` → `_upload_file_via_requests()` for the reference implementation.

### Running scripts requires MACCABIPEDIA_UA_SCRIPT env var
Scripts that upload to Maccabipedia must set the user-agent to a whitelisted script name via:
```
source ~/.secrets && MACCABIPEDIA_UA_SCRIPT=gamesbot_basketball python script.py
```
The server's ModSecurity WAF blocks requests from unknown user-agent script names.

---

## 7. MaccabiPedia Structure (CRITICAL — read every session)

Always read `.claude/maccabipedia_structure_knowledge.md` before working with game pages, player pages, templates, or the Cargo API.
