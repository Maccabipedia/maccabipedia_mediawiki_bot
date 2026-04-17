"""Check if Dubai OT game has הארכה= set on the wiki."""
import mwparserfromhell, pywikibot as pw
from maccabipediabot.basketball.gamesbot_basketball import _site

page = pw.Page(_site(), "כדורסל:26-03-2026 מכבי תל אביב נגד דובאי - יורוליג")
tmpl = mwparserfromhell.parse(page.text).filter_templates(matches=lambda t: t.name.matches("משחק כדורסל"))[0]
for p in tmpl.params:
    k = str(p.name).strip()
    v = str(p.value).strip()
    if "הארכה" in k and v:  # non-empty OT field
        print(f"  {k!r} = {v!r}")
