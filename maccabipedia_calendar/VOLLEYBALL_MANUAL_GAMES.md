# Volleyball Calendar Manual Games & Overrides

## Overview

The volleyball calendar sync system now supports:
1. **Manual game protection** - Games added manually to the calendar won't be deleted
2. **Date overrides** - Fix incorrect game dates from IVA website by matching the original date

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

### Date Overrides

**For fixing wrong dates from IVA**

#### Override File Location
`maccabipedia_calendar/volleyball_game_overrides.json`

#### Format

```json
{
  "OLD_DATE_TIME": "NEW_DATE_TIME"
}
```

#### Date Format
`DD/MM/YYYY HH:MM` (must match the IVA site format)

**Example:**
To move a game from Jan 27 to Feb 10:
```json
{
  "27/01/2026 19:00": "10/02/2026 19:00"
}
```

---

## Usage Examples

### Example: Move Game Date

IVA shows a game on 27/01/2026, but it's actually 10/02/2026:

```json
{
  "27/01/2026 19:00": "10/02/2026 19:00"
}
```

### Example: Add Manual Game

**Scenario:** Game not on IVA website at all

**Solution:**
1. Add game directly in Google Calendar
2. Done! It's automatically protected

---

## How to Use

### Adding a Date Override

1. Open `maccabipedia_calendar/volleyball_game_overrides.json`
2. Add translation: `"OLD_DD/MM/YYYY HH:MM": "NEW_DD/MM/YYYY HH:MM"`
3. Save the file
4. Next sync will apply the change

### Finding the Old Date

The "Old Date" is the one currently appearing on the IVA website or the current calendar event (if it hasn't been overridden yet). Use the format `DD/MM/YYYY HH:MM`.
