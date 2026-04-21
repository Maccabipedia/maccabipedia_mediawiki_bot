# MaccabiPedia YouTube Channel

Our channel — used to host Maccabi Tel Aviv match videos referenced from the wiki. When a match video gets deleted from an external channel (see `find_broken_videos.py`), we upload our local backup here and update the wiki to point at the new URL.

This doc captures the conventions that aren't obvious from the code: title format quirks (BIDI), brand-account OAuth gotchas, and the Google Drive backup folder layout. Keep it current when the upload workflow changes — the next operator will read it first.

Channel: https://www.youtube.com/@MaccabiPedia

## Video Metadata Conventions

- **Titles:** `עונת [YEAR] [COMPETITION] [ROUND] מכבי תל אביב - [OPPONENT] ([OPPONENT_SCORE]-[MACCABI_SCORE]) [TYPE]`
  - Score is in parentheses at the end, digits **stored reversed** (opponent's goals first). YouTube's BIDI renderer flips digit order inside parens in RTL context, so storing `(2-0)` displays as `(0-2)` — and Hebrew readers interpret `Maccabi - Hapoel (0-2)` as Maccabi=0, Hapoel=2, which is the intended semantics.
  - TYPE: `משחק מלא` for full match, `תקציר` for highlights
  - Example: `עונת 2008-09 גביע המדינה סיבוב ט מכבי תל אביב - הפועל תל אביב (2-0) תקציר` (Maccabi lost 0-2; displayed as `(0-2)`)
  - Competition: use the name from the wiki page (`ליגת העל`, `ליגה לאומית`, `גביע המדינה`, `גביע הטוטו`, `ליגת האלופות`, `ליגה האירופאית`, `גביע אירופה למחזיקות גביע`)
- **Description:** the wiki game-page URL, **URL-encoded** so YouTube auto-linkifies it (YouTube's linkifier is unreliable with non-ASCII URLs). Example: `https://www.maccabipedia.co.il/%D7%9E%D7%A9%D7%97%D7%A7:...`
- **Tags:** empty
- **Category:** Sports (ID 17)
- **Privacy:** public

## Playlists

One playlist per season: `מכביפדיה | עונת YYYY/YY` (e.g. `מכביפדיה | עונת 2001/02`).

**Every uploaded video is added to its season playlist.** If a season playlist doesn't exist yet, create it (public) before adding the video.

## Google Drive Video Backup Structure

All paths below are relative to `$MACCABIPEDIA_GOOGLE_DRIVE_ROOT/מכביפדיה_ראשי/וידאו/` (the mapped drive root — `/mnt/d/maccabipedia_google_drive` on Roee's WSL machine, but operator-specific).

### Football (כדורגל)
```
כדורגל/עונות/עונת [YEAR]/[COMPETITION]/[ROUND]/[תקציר|משחק מלא]/[filename]
```

Domestic competitions (Hebrew names, Hebrew filenames):
- `ליגה לאומית/מחזור [N]/תקציר|משחק מלא/`
- `גביע המדינה/סיבוב [X]/תקציר|משחק מלא/` (also `שמינית גמר`, `רבע גמר`, `חצי גמר`, `גמר`)
- `גביע הטוטו/מחזור [N]/תקציר|משחק מלא/`

European competitions (English round names, English filenames):
- `Europa League/[Round]/[Team1 Score-Score Team2]/Full Match|Highlights/`
- `Champions League/[Round]/[Team1 Score-Score Team2]/Full Match|Highlights/`
- `Cup Winner's Cup/[Round]/[Team1 Score-Score Team2]/Full Match|Highlights/`

Note: folders for pre-1999 seasons say `ליגה לאומית`, but on YouTube/wiki the competition is `ליגת העל` post-1999.

### Basketball (כדורסל)
```
כדורסל/[YEAR]/[competition]/
```
Only `2000-01/suproleague/` confirmed so far.

### Volleyball (כדורעף)
Files directly under `כדורעף/` named `כדורעף - [DD-MM-YYYY] [teams] - [competition]`

Formats found: `.webm`, `.mp4`, `.m4v`, `.mkv`, `.flv`

## OAuth Credentials

- Client secret: `~/.config/maccabipedia/youtube_client_secret.json`
- Token (reusable): `~/.config/maccabipedia/youtube_token.json`
- Scopes: `youtube.upload` + `youtube` (the second is needed to create playlists and add items to them)
- Auth script: `.claude/scripts/youtube_auth.py`

**IMPORTANT:** @MaccabiPedia is a **Google Brand Account**. During OAuth sign-in, the correct Google account (the one that manages the MaccabiPedia brand) must be selected. Authenticating with the wrong account gives a token with `channels().list(mine=True)` returning 0 items, and playlist/upload calls fail with "Channel not found".

**Token expiry:** The OAuth app is in "Testing" mode in Google Cloud → refresh tokens expire after **7 days**. Publishing the app in OAuth consent screen removes the expiry (no Google verification is needed for private use).

## Upload Script

`.claude/scripts/youtube_upload.py` — arguments:
- `--file`: path to the video file
- `--title`: YouTube title (follow the convention above)
- `--playlist`: playlist title (e.g. `מכביפדיה | עונת 2001/02`); created if missing

Run with `uv run python .claude/scripts/youtube_upload.py --file ... --title ... --playlist ...`. The script uploads, prints the resulting video URL, and adds it to the playlist.

## API Quota

YouTube Data API default quota: **10,000 units/day**. Each upload costs 1,600 units, and a playlist insert/add costs 50 — so ~6 uploads per day max before the quota resets.

## Useful Commands (no API key needed)

List recent videos:
```
yt-dlp --flat-playlist --print "%(title)s | %(id)s" "https://www.youtube.com/@MaccabiPedia/videos"
```

List all playlists (title + ID):
```
yt-dlp --flat-playlist --print "%(title)s | %(id)s" "https://www.youtube.com/@MaccabiPedia/playlists"
```
