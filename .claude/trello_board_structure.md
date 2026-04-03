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

## Workflow with Claude Code

1. **Adding tasks**: Tell Claude to add a card — it goes to Inbox with auto-labels.
2. **Triage**: Review Inbox periodically, move cards to Next Up or archive.
3. **Pick up work**: Claude checks cards with `Claude` label in Next Up.
4. **Complete**: Claude moves card to Done with a comment (commit reference if applicable).
5. **Cleanup**: Archive Done cards monthly.
