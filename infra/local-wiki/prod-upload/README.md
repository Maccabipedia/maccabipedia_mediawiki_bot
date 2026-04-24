# prod-upload — three files to FTP into the prod wiki root

Upload **all three** of these files into the prod web root (the directory
that currently contains the live `LocalSettings.php`). Replace the existing
`LocalSettings.php` with the one in this folder.

| Local path | Upload as | Tracked in git? |
|---|---|---|
| `LocalSettings.php` | `LocalSettings.php` (overwrites the monolith) | yes |
| `LocalSettings.shared.php` | `LocalSettings.shared.php` (new file) | yes |
| `LocalSettings.env.prod.php` | `LocalSettings.env.prod.php` (new file) | **no** — gitignored, contains real DB password / SecretKey / UpgradeKey / SecureHTML secret |

After uploading, browse `https://www.maccabipedia.co.il/` once and confirm
the homepage renders. If anything looks off, FTP the backup of the original
`LocalSettings.php` back over the new stub — the other two files become
inert because nothing requires them.

## Behavioral notes

The split is byte-equivalent to the prior monolithic LocalSettings.php
**except**:

- `$wgFavicon` and `$wgAppleTouchIcon` switched from absolute
  (`https://www.maccabipedia.co.il/favicon.ico`) to relative (`/favicon.ico`).
  Both still resolve to the same file on prod.

Everything else — extensions, namespaces, group permissions, hooks, Cargo
config, ContactPage config, namespace defines — is unchanged. The
`$wgDebugLogGroups` paths intentionally stay single-quoted (literal `$IP`
and `{$wgDBname}`) to match prod's existing log path behavior.

## Source of truth

This folder is the canonical home for `LocalSettings.shared.php` and
`LocalSettings.env.prod.php`. The local docker stack at
`infra/local-wiki/docker-compose.yml` bind-mounts `LocalSettings.shared.php`
from here, so any edit lands in both prod and dev runs after the next
docker reload. No copying or syncing required.

`LocalSettings.env.prod.php` is gitignored — never committed.
