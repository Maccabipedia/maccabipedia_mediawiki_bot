"""Build interactive HTML showing PDF pages for undecided scorer names."""
import json

page_images = json.load(open("/tmp/page_images.json"))

undecided_games = [
    {"date": "04-10-1930", "season": "1930/31", "opponent": 'המעופפים רמלה', "score": "4-2",
     "pages": [8, 9], "csv_scorers": "רוברט מורגן )ע(, זליבנסקי31, מנחם חרש, שמואל בכ ר",
     "items": [
         {"id": "זליבנסקי",    "csv": "זליבנסקי",    "wiki": "אריה זליבנסקי", "pct": 76},
         {"id": "רוברט_מורגן", "csv": "רוברט מורגן", "wiki": "הרברט מייטנר",  "pct": 61},
     ]},
    {"date": "25-10-1930", "season": "1930/31", "opponent": 'הפועל ת"א', "score": "2-1",
     "pages": [8, 9], "csv_scorers": "מנחם חרש 18, מרדכי פצנובסקי/מנחם חרש 55",
     "items": [
         {"id": "מרדכי_צנובסקי_או", "csv": "מרדכי צנובסקי או מנחם חרש", "wiki": "מרדכי פצנובסקי", "pct": 67},
         {"id": "או", "csv": "או", "wiki": "", "pct": 0},
     ]},
    {"date": "14-05-1932", "season": "1931/32", "opponent": "מכבי חשמונאי", "score": "2-3",
     "pages": [18, 19], "csv_scorers": "בן-ציון אפשטיין ,(31) פנחס פידלר 73",
     "items": [
         {"id": "נחס_ידלר",        "csv": "נחס ידלר",        "wiki": "פנחס פידלר",    "pct": 89},
         {"id": "בן_ציון_א_שטיין", "csv": "בן-ציון א שטיין", "wiki": "בן ציון אפשטיין", "pct": 87},
     ]},
    {"date": "04-03-1933", "season": "1932/33", "opponent": "מכבי חשמונאי", "score": "2-0",
     "pages": [24, 25], "csv_scorers": "יעקב זליבנסקי, אמרה יעקב י",
     "items": [
         {"id": "אמרה_י_קב_י", "csv": "אמרה י קב י", "wiki": "אברהם יעקובי", "pct": 70},
     ]},
    {"date": "06-01-1934", "season": "1933/34", "opponent": "מכבי רחובות", "score": "?",
     "pages": [28, 29], "csv_scorers": "?",
     "items": [
         {"id": "אמרה_י_קבי", "csv": "אמרה י קבי", "wiki": "אברהם יעקובי", "pct": 73},
     ]},
    {"date": "20-11-1937", "season": "1937/38", "opponent": "הפועל חיפה", "score": "?",
     "pages": [47, 48], "csv_scorers": "?",
     "items": [
         {"id": "צבי_וול_וביץ", "csv": "צבי וול וביץ", "wiki": "וולפוביץ", "pct": 70},
     ]},
    {"date": "05-11-1938", "season": "1938/39", "opponent": 'מכבי פ"ת', "score": "2-0",
     "pages": [57, 58], "csv_scorers": ")הופסק (",
     "items": [
         {"id": "הו_סק", "csv": "הו סק", "wiki": "", "pct": 0},
     ]},
    {"date": "02-12-1939", "season": "1939", "opponent": "הכח", "score": "1-4",
     "pages": [64, 65], "csv_scorers": ")טכני(",
     "items": [
         {"id": "טכני_1939", "csv": "טכני", "wiki": "", "pct": 0},
     ]},
    {"date": "27-06-1942", "season": "1941/43", "opponent": 'מכבי פ"ת', "score": "4-0",
     "pages": [102, 103], "csv_scorers": "זוני ,(2) גאול מכליס, יוסף מרימוביץ'",
     "items": [
         {"id": "זוני", "csv": "זוני", "wiki": "גוני", "pct": 75},
     ]},
    {"date": "16-10-1943", "season": "1941/43", "opponent": "הומנטמן", "score": "3-0",
     "pages": [108, 109], "csv_scorers": ")טכני(",
     "items": [
         {"id": "טכני_1943", "csv": "טכני", "wiki": "", "pct": 0},
     ]},
    {"date": "13-12-1947", "season": "1947/48", "opponent": 'הפועל פ"ת', "score": "?",
     "pages": [165, 166], "csv_scorers": "?",
     "items": [
         {"id": "דב_שונשיין", "csv": "דב שונשיין", "wiki": "", "pct": 0},
     ]},
    {"date": "29-11-1947", "season": "1947/48", "opponent": 'הפועל ראשל"צ', "score": "?",
     "pages": [168, 169], "csv_scorers": "?",
     "items": [
         {"id": "צבי_1947", "csv": "צבי", "wiki": "", "pct": 0},
     ]},
    {"date": "03-01-1948", "season": "1947/48", "opponent": 'מכבי פ"ת', "score": "?",
     "pages": [165, 166], "csv_scorers": "?",
     "items": [
         {"id": "שמואל_בן_דרור", "csv": "שמואל בן -דרור 04", "wiki": "ישראל בן-דרור", "pct": 81},
     ]},
    {"date": "13-03-1948", "season": "1947/48", "opponent": 'הפועל פ"ת', "score": "6-1",
     "pages": [170, 171], "csv_scorers": "אהרון סידי ,(19) שמואל ישראלי ,25) ,(68 יהושע גלזר ,(42) יוסף",
     "items": [
         {"id": "שמואל_ישראלי", "csv": "שמואל ישראלי",  "wiki": "שמואל פרלמן",   "pct": 70},
         {"id": "יהוש_גלזר",    "csv": "יהוש גלזר",     "wiki": "שייע גלזר",     "pct": 67},
         {"id": "יוס_1948",     "csv": "יוס",           "wiki": "יוסף מרימוביץ", "pct": 60},
     ]},
]


def img_tag(p):
    key = str(p)
    if key in page_images:
        return ('<img src="data:image/png;base64,' + page_images[key] +
                '" style="max-width:100%;border:1px solid #ccc;border-radius:4px;">')
    return '<p style="color:red">Page ' + str(p) + ' not available</p>'


total_items = sum(len(g["items"]) for g in undecided_games)

CSS = """
body{font-family:Arial,sans-serif;margin:20px;background:#f0f0f0;}
h1{color:#2c3e50;}
.game-block{background:#fff;border-radius:10px;padding:16px 20px;margin:20px 0;box-shadow:0 2px 6px rgba(0,0,0,.12);}
.game-header{font-size:1.15em;font-weight:bold;color:#2c3e50;margin-bottom:6px;}
.csv-line{background:#f8f4e8;border-right:4px solid #e67e22;padding:6px 10px;border-radius:4px;margin-bottom:12px;font-size:.95em;}
.item{display:flex;align-items:center;gap:10px;margin:6px 0;padding:8px 12px;border-radius:8px;background:#f5f5f5;flex-wrap:wrap;}
.item.approved{background:#d5f5e3;}
.item.rejected{background:#fde8e8;opacity:.7;}
.item-name{font-weight:bold;font-size:1.05em;min-width:140px;}
.item-wiki{color:#555;min-width:160px;}
.pct{display:inline-block;padding:2px 7px;border-radius:10px;font-size:.82em;font-weight:bold;}
.r-high{background:#d5f5e3;color:#1e8449;}
.r-mid{background:#fef9e7;color:#b7770d;}
.r-low{background:#fde8e8;color:#922b21;}
.r-none{background:#eee;color:#555;}
.btn{padding:5px 12px;border:none;border-radius:6px;cursor:pointer;font-size:.9em;font-weight:bold;}
.btn-approve{background:#27ae60;color:#fff;}
.btn-approve:hover{background:#1e8449;}
.btn-reject{background:#e74c3c;color:#fff;}
.btn-reject:hover{background:#c0392b;}
.btn.active{box-shadow:0 0 0 3px #2c3e50;}
.pages-row{display:flex;gap:12px;flex-wrap:wrap;margin-top:12px;}
.page-wrap{flex:1;min-width:300px;}
.page-label{font-size:.8em;color:#888;margin-bottom:4px;}
.export-bar{position:fixed;bottom:0;left:0;right:0;background:#2c3e50;color:#fff;padding:10px 20px;display:flex;align-items:center;gap:16px;z-index:100;}
.export-bar button{padding:7px 18px;background:#2980b9;color:#fff;border:none;border-radius:6px;cursor:pointer;font-size:.95em;font-weight:bold;}
#export-out{position:fixed;bottom:55px;left:20px;right:20px;background:#fff;border:1px solid #ccc;border-radius:8px;padding:16px;font-family:monospace;font-size:.85em;white-space:pre-wrap;direction:ltr;display:none;max-height:50vh;overflow-y:auto;box-shadow:0 4px 20px rgba(0,0,0,.2);z-index:200;}
#copy-btn{padding:6px 14px;background:#7f8c8d;color:#fff;border:none;border-radius:6px;cursor:pointer;display:none;}
"""

JS = """
<script>
var decisions = {};
var total = __TOTAL__;
function mark(gi, id, state) {
  var el = document.getElementById('item-' + gi + '-' + id);
  el.className = 'item ' + state;
  el.querySelectorAll('.btn').forEach(function(b){b.classList.remove('active');});
  el.querySelector(state==='approved'?'.btn-approve':'.btn-reject').classList.add('active');
  decisions[id] = {state:state, csv:el.dataset.csv, wiki:el.dataset.wiki};
  document.getElementById('progress').textContent = Object.keys(decisions).length + ' / ' + total + ' סומנו';
}
function exportDecisions() {
  var af=[], rf=[];
  Object.values(decisions).forEach(function(d){
    if (d.state==='approved') af.push({csv:d.csv, wiki:d.wiki||d.csv});
    else rf.push(d.csv);
  });
  var out = JSON.stringify({use_wiki_name:af, junk_to_drop:rf}, null, 2);
  var box = document.getElementById('export-out');
  box.textContent = out;
  box.style.display = 'block';
  document.getElementById('copy-btn').style.display = 'inline-block';
}
function copyOut() {
  navigator.clipboard.writeText(document.getElementById('export-out').textContent);
  document.getElementById('copy-btn').textContent = 'הועתק!';
  setTimeout(function(){ document.getElementById('copy-btn').textContent = 'העתק'; }, 1500);
}
</script>
""".replace("__TOTAL__", str(total_items))

parts = [
    '<!DOCTYPE html>\n<html dir="rtl" lang="he">\n<head>\n<meta charset="utf-8">\n',
    '<title>בדיקת שמות כובשים</title>\n<style>\n', CSS, '</style>\n</head>\n<body>\n',
    '<h1>&#128196; בדיקת שמות כובשים &#8212; עמודי הספר</h1>\n',
    '<p style="color:#666">לכל שם לא ברור &#8212; בדוק את עמוד הספר, ואז '
    '<strong>אשר</strong> (שם נכון) או <strong>דחה</strong> (זבל).</p>\n',
]

for gi, game in enumerate(undecided_games):
    pages_html = ''
    for p in game["pages"]:
        pages_html += ('<div class="page-wrap"><div class="page-label">&#128196; עמוד ' +
                       str(p) + '</div>' + img_tag(p) + '</div>')

    items_html = ''
    for item in game["items"]:
        wiki_str = ('&#8594; ויקי: <strong>' + item["wiki"] + '</strong>') if item["wiki"] else '(לא נמצא)'
        pct = item["pct"]
        pcls = 'r-high' if pct >= 90 else ('r-mid' if pct >= 70 else ('r-low' if pct > 0 else 'r-none'))
        pct_badge = '<span class="pct ' + pcls + '">' + (str(pct) + '%' if pct else '?') + '</span>'
        iid = item["id"]
        icsv = item["csv"].replace('"', '&quot;')
        iwiki = (item["wiki"] or "").replace('"', '&quot;')
        items_html += (
            '<div class="item" id="item-' + str(gi) + '-' + iid + '" '
            'data-id="' + iid + '" data-csv="' + icsv + '" data-wiki="' + iwiki + '">'
            '<span class="item-name">' + item["csv"] + '</span>'
            '<span class="item-wiki">' + wiki_str + ' ' + pct_badge + '</span>'
            '<button class="btn btn-approve" '
            'onclick="mark(\'' + str(gi) + '\',\'' + iid + '\',\'approved\')">&#10003; אשר</button>'
            '<button class="btn btn-reject" '
            'onclick="mark(\'' + str(gi) + '\',\'' + iid + '\',\'rejected\')">&#10007; דחה</button>'
            '</div>\n'
        )

    parts += [
        '<div class="game-block">',
        '<div class="game-header">' + game["date"] + ' | ' + game["season"] +
        ' | מכבי ת"א vs ' + game["opponent"] + ' (' + game["score"] + ')</div>',
        '<div class="csv-line">כובשים מה-CSV: ' + game["csv_scorers"] + '</div>',
        '<div class="items">' + items_html + '</div>',
        '<div class="pages-row">' + pages_html + '</div>',
        '</div>\n',
    ]

parts += [
    '<div style="height:65px"></div>\n',
    '<div class="export-bar">',
    '<span id="progress">0 / ' + str(total_items) + ' סומנו</span>',
    '<button onclick="exportDecisions()">&#128190; ייצא JSON</button>',
    '<button id="copy-btn" onclick="copyOut()">העתק</button>',
    '</div>',
    '<pre id="export-out"></pre>',
    JS,
    '</body></html>',
]

out = ''.join(parts)
open("data/verify_scorer_names_pages.html", "w", encoding="utf-8").write(out)
print("done, size:", len(out) // 1024, "KB")
