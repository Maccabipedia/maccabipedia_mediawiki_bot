# Volleyball Calendar Manual Games & Overrides

## Overview

The volleyball calendar sync system now supports:
1. **Manual game protection** - Games added manually to the calendar won't be deleted
2. **Data overrides** - Fix incorrect IVA website data (dates, times, locations, scores)

---

## How It Works

### Manual Games Protection

**Automatic protection** - No action needed!

- Games added manually to Google Calendar are automatically protected
- The system only deletes events marked as `iva_sourced: true`
- Manual games lack this flag, so they're never deleted

**To add a manual game:**
1. Add the game directly in Google Calendar
2. That's it! The sync won't touch it

---

### Data Overrides

**For fixing wrong IVA data** (incorrect dates, times, locations, etc.)

#### Override File Location
`maccabipedia_calendar/volleyball_game_overrides.json`

#### Format

```json
{
  "מכבי חיפה מחזור 5 ליגה": {
    "date": "2026-02-15 19:00",
    "stadium": "היכל הספורט רמת גן"
  },
  "הפועל ירושלים מחזור 3 גביע המדינה": {
    "date": "2026-01-28 20:30"
  }
}
```

#### Key Format
The key must match the `maccabipedia_id` format:
```
"{opponent} {fixture} {competition}"
```

**Examples:**
- `"מכבי חיפה מחזור 5 ליגה"`
- `"הפועל ירושלים מחזור 3 גביע המדינה"`

#### Available Override Fields

| Field | Format | Example |
|-------|--------|---------|
| `date` | `YYYY-MM-DD HH:MM` | `"2026-02-15 19:00"` |
| `stadium` | String | `"היכל הספורט רמת גן"` |
| `maccabi_result` | Integer | `3` |
| `opponent_result` | Integer | `1` |

---

## Usage Examples

### Example 1: Fix Wrong Date

IVA shows game on Feb 10, but it's actually Feb 15:

```json
{
  "מכבי חיפה מחזור 5 ליגה": {
    "date": "2026-02-15 19:00"
  }
}
```

### Example 2: Fix Multiple Fields

```json
{
  "הפועל ירושלים מחזור 3 גביע המדינה": {
    "date": "2026-01-28 20:30",
    "stadium": "היכל טוטו ירושלים"
  }
}
```

### Example 3: Update Score

```json
{
  "מכבי נתניה מחזור 8 ליגה": {
    "maccabi_result": 3,
    "opponent_result": 2
  }
}
```

---

## How to Use

### Adding an Override

1. Open `maccabipedia_calendar/volleyball_game_overrides.json`
2. Add your override entry
3. Save the file
4. Next sync will use the corrected data

### Finding the Game ID

The game ID format is: `"{opponent} {fixture} {competition}"`

Check the calendar event description or logs to find the exact format.

---

## Troubleshooting

### Override not working?

1. **Check the key format** - Must exactly match `"{opponent} {fixture} {competition}"`
2. **Check date format** - Must be `YYYY-MM-DD HH:MM`
3. **Check logs** - Look for "Applying overrides to game" messages
4. **Remove metadata fields** - Keys starting with `_` are ignored (used for comments)

### Manual game was deleted?

- This shouldn't happen! Manual games lack the `iva_sourced` flag
- Check if the game was originally created by the sync (it would have `iva_sourced: true`)
- If you need to protect an auto-created game, delete it and re-add manually

---

## Technical Details

### Event Marking

All IVA-sourced events have:
```json
{
  "extendedProperties": {
    "shared": {
      "maccabipedia_id": "...",
      "iva_sourced": "true"
    }
  }
}
```

Manual events lack the `iva_sourced` flag.

### Override Application

Overrides are applied **after** fetching from IVA but **before** syncing to calendar:

1. Fetch games from IVA
2. Load override file
3. **Apply overrides** ← Happens here
4. Sync to calendar

This ensures corrected data reaches the calendar.
