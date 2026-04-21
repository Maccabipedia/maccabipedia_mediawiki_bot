# MaccabiPedia Trello Board Structure

Board URL: https://trello.com/b/n9Zz1CSL/maccabipedia

## Lists (Kanban flow)

| List | Purpose | Guidelines |
|------|---------|------------|
| **Inbox** | Unsorted ideas and tasks | Triage weekly. Move to Next Up or archive. |
| **Next Up** | Triaged and ready to work on | Max ~15 cards. Pull from here to In Progress. |
| **In Progress** | Currently being worked on | Max 3 cards. |
| **Waiting** | Blocked on someone else | External people, other team members, pending info. |
| **Done** | Completed tasks | Archive monthly to keep board clean. |

## Labels

### Sport labels
| Label | Color | Use for |
|-------|-------|---------|
| `Football` | green | Football-specific tasks |
| `Volleyball` | blue | Volleyball-specific tasks |
| `Basketball` | purple | Basketball-specific tasks |
| `Handball` | pink | Handball-specific tasks |

### Area/Type labels
| Label | Color | Use for |
|-------|-------|---------|
| `Site` | sky | Website, templates, MediaWiki, CSS, search, navigation |
| `Content` | orange | Photos, videos, songs, articles, newspapers, scanning |
| `Data Fix` | yellow | Corrections, missing data, mismatches, validation |
| `Automation` | blue_dark | Scripts, bots, Cargo queries, maccabistats |
| `Outreach` | lime | Contacting people, collecting items, interviews |

### Who/Effort labels
| Label | Color | Use for |
|-------|-------|---------|
| `Claude` | green_dark | Claude Code can execute autonomously |
| `Easy` | black_dark | Quick/simple tasks |

## Card labeling rules

- A card can have **multiple labels** (e.g. `Football` + `Data Fix` + `Claude`)
- Every card should have at least one **type label** (Site/Content/Data Fix/Automation/Outreach)
- Add a **sport label** only if the task is specific to that sport
- Add `Claude` label to tasks that can be automated/scripted

## MCP Integration

Claude Code connects to Trello via `@delorenj/mcp-server-trello` MCP server.
- Config: `.mcp.json` (gitignored, contains API key + token)
- Permissions: `mcp__trello__*` auto-approved in `.claude/settings.json`
- Board ID: `n9Zz1CSL`

## Verifying if a task is done

When checking if a Trello task is already done, check **all relevant layers** — not just git:

1. **Git history** — commits, PRs
2. **Rendered site** — visual check of the actual page as users see it
3. **Cargo API data** — underlying database values
4. **Wikitext source** — raw templates (`?action=raw`)
5. **Bot code** — whether logic exists in this repo

These layers can disagree. For example, wikitext may store data in the correct order but the template re-sorts it during rendering. Always verify the layer the task actually targets.

## Workflow with Claude Code

1. **Adding tasks**: Tell Claude to add a card — it goes to Inbox with auto-labels.
2. **Triage**: Review Inbox periodically, move cards to Next Up or archive.
3. **Pick up work**: User tells Claude which card to take.
4. **Complete**: Claude moves card to Done with a comment (commit reference if applicable).
5. **Cleanup**: Archive Done cards monthly.

## Card Lifecycle (Claude)

When told to take a card:
1. Fetch the card, read its description and checklist
2. Move card to **In Progress**
3. Do the work
4. **If blocked:** comment on the card describing the blocker; stay In Progress (do NOT move to Waiting)
5. **If a significant decision changes direction mid-work:** add a comment immediately
6. **When PR is created:** comment on the card with the PR link; stay In Progress
7. **When PR is merged:** move card to **Done**, add a summary comment with PR/commit link and any key decisions not already commented

**Commenting rule:** Minor decisions → summarize in the final Done comment. Major direction changes → comment immediately when they happen.

## Cards with physical artifacts (trello_tasks/ folder convention)

When a card involves files the user needs to act on (rename, triage, upload, verify, crop, decide), stage them into a dedicated folder instead of leaving the user to re-derive which files belong to the task.

**Location:** `$MACCABIPEDIA_DRIVE_ROOT/מכביפדיה_ראשי/trello_tasks/<short-id>_<hebrew_slug>/` (env var defined in `.claude/settings.local.json`, required — fail if unset, never hardcode the value)

- `<short-id>` is the Trello card's `idShort` (visible as `#530` on the card, also in the short URL `https://trello.com/c/.../530-...`). Prefix lets the user cross-reference folder ↔ card at a glance.
- `<hebrew_slug>` uses underscores, no spaces — e.g. `530_שם_המשחק_השלמת_העלאה`.
- Create the card first, then rename/create the folder with the returned `idShort`.

**Folder conventions inside:**
- Numbered Hebrew subfolders for distinct work buckets (e.g. `01_נובמבר_2003_סריקות_גולמיות/`, `02_שינוי_שם_IMG/`). Number-prefix for ordering.
- **Copy, don't move** — originals stay in place.
- Include `README.md` (Hebrew, brief) and any interactive HTML guide.
- Skip files explicitly marked "don't upload" at the source — don't even copy them.

**Card description convention:** reference the Windows-style path so Google Drive Desktop opens it in Explorer when the user clicks. Build it from `$MACCABIPEDIA_DRIVE_ROOT` at write time (convert the WSL mount prefix to its Windows drive letter and flip slashes) — never write the absolute path into durable source/docs.

**Template script:** `.claude/tmp/stage_trello_task.py` from card #530 (branch `check-shem`) is the reference implementation.
