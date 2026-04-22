# External club-history sites — Maccabipedia relevance scoring

Scored catalog of club-history / match-archive websites harvested from a Facebook post in the **Football Lineups and Results Research** group.

- **Source thread:** https://www.facebook.com/groups/375803282812198/posts/1395508027508380/
- **Group:** https://www.facebook.com/groups/375803282812198/ (Football Lineups and Results Research)
- **Original ask (Marco D'Avanzo):** "looking for as many as possible internet sites about club history, reporting a list of international friendlies matches played so far by that club."
- **Captured:** 2026-04-22 (138 unique URLs across 132 domains after stripping FB tracking params)

## Scoring rubric

Score = expected likelihood the site contains a Maccabi Tel Aviv fixture (home or away, official or friendly) that Maccabipedia could cross-reference for lineups, scorers, attendance, or a match report.

| Score | Meaning |
|-------|---------|
| **5** | Confirmed UEFA opponent — verified against the canonical opponent list (below). Site is a per-match archive. |
| **4** | Probable opponent: friendly-only evidence, or an Intertoto / obscure-qualifying tie that needs confirmation. |
| **3** | **Meta-league site** covering an entire country whose clubs played Maccabi — useful as a cross-reference index. |
| **2** | Unlikely opponent (lower division, or demoted from v1 Tier 5 because no UEFA tie was found). Include only if no better source exists. |
| **0** | No plausible Maccabi connection (South American, unrelated regional). Skip. |

**Verification basis** (2026-04-22): Tier 4–5 assignments were cross-checked against:

- Wikipedia — [Maccabi Tel Aviv F.C. in European football](https://en.wikipedia.org/wiki/Maccabi_Tel_Aviv_F.C._in_European_football) (canonical opponent list)
- RSSSF — [Israel in European Cups](https://www.rsssf.org/tablesi/isra-ec.html) (through 2004, covers Intertoto)

v1 of this doc (initial commit in PR #111) placed ~30 famous clubs at Tier 5 by guess rather than verification. They are now in Tier 2 marked **[demoted]** so reviewers can see what was pruned; if a citation surfaces, promote that specific site back.

---

## 🟢 Tier 5 — Confirmed UEFA opponents

Each line cites the competition/season from the canonical list.

### Italy
- **myjuve.it** — Juventus, UCL group 2004/05

### England
- **bounder.friardale.co.uk** — Chelsea, UCL group 2015/16
- **avfchistory.co.uk** — Aston Villa, UEL league phase 2025/26

### Netherlands
- **afc-ajax.info** — Ajax, UCL group 2004/05 + UEL league phase 2024/25
- **psv.supporters.nl** — PSV, UEFA Conference League KO play-off 2021/22
- **fctwentestatistieken.nl** — FC Twente, Intertoto Cup 1977 group (per RSSSF)

### Germany
- **bayernbaeda.de** — Bayern Munich, UCL group 2004/05

### France
- **histoiredupsg.fr** — PSG, Europa League play-off 2010/11
- **lalegendedesgirondins.com** — Bordeaux, Europa League group 2013/14

### Switzerland
- **fcb-archiv.ch** — FC Basel, UCL qualifying 2013/14 + UEL knockout 2013/14 + UCL qualifying 2015/16
- **dbfcz.ch** — FC Zürich, Intertoto Cup 1978 (per RSSSF)

### Scandinavia
- **allsvenskamff.blogspot.com** — Malmö FF, Intertoto Cup 1978 (per RSSSF)

### Belgium
- **rafcmuseum.be** — Royal Antwerp, Intertoto Cup 1980 (per RSSSF)

### Eastern Europe
- **povijest.gnkdinamo.hr** — Dinamo Zagreb, UEFA Cup 2001/02 + UEL league phase 2025/26

---

## 🟡 Tier 4 — Probable / unverified

Promote to Tier 5 only with a cited matchup.

- **zenit-history.ru** — Zenit St. Petersburg, Europa League group 2016/17 (strong candidate for promotion to 5)
- **partizanopedia.rs** — Partizan Belgrade (1996/97 UEFA Cup PR per RSSSF review agent; not in Wikipedia canonical list — needs reconciliation)
- **ifkdb.se** — IFK Göteborg ("UEFA Cup 1981 iconic" claim in v1 could not be verified — needs citation)
- **serbenfiquista.com** — Benfica (v1 claimed "UEL/UCL qualifying"; not found — needs citation)
- **metalist-kh-stat.net.ua** — Metalist Kharkiv (unconfirmed)
- **dniprohistory.blogspot.com** — FC Dnipro (unconfirmed)
- **fc-dynamo.ru** — Dynamo Moscow (unconfirmed)
- **aik.se** — AIK Stockholm (unconfirmed)
- **storiadelcagliari.it** — Cagliari (friendlies only)
- **empoli1920.com** — Empoli (friendlies only)
- **evertonresults.com** — Everton (friendlies only)
- **westhamstats.info** — West Ham (friendlies only)
- **statcity.co.uk** — Manchester City (friendly 2011)
- **ozwhitelufc.net.au** — Leeds United (friendlies only)
- **fulhamfootballprogrammes.co.uk** — Fulham (friendly 2010)
- **mufcinfo.com** — Manchester United (v1 claimed UCL 2004/05 — wrong, that group was Bayern/Juve/Ajax; friendly 2013 plausible)
- **fiorentinaweb.com** — Fiorentina (friendlies only)

---

## 🟠 Tier 3 — Meta-league cross-references

League-wide archives — useful for verifying any confirmed Maccabi opponent.

- **koningvoetbal.nl** — All-time Dutch football
- **ererat.nl** — Eredivisie all-time
- **csfotbal.cz** — Czech first league (Slavia Prague was a Maccabi UEL opponent 1993 and 2017/18)
- **austriasoccer.at** — Austrian league archive (LASK 2021/22 CL group)
- **fotbollsweden.se** — Sweden (stats, no lineups)
- **datencenter.comon.ergebnis-dienst.de** — German football data hub (Bayern, Eintracht Frankfurt, Werder Bremen)
- **footballfacts.ru** — Soviet / Russian championship archive (Dynamo Kyiv, Zenit)
- **historie.vvv-venlo.nl** — VVV-Venlo (Dutch lower flight)
- **gvavstats.nl** — GVAV (pre-1971 Groningen) historical

---

## 🔵 Tier 2 — Unlikely or no confirmed UEFA tie

### Demoted from v1 Tier 5 (no match in Wikipedia canonical list)

If a friendly or missed UEFA record surfaces, promote the specific site back with a citation.

- **storiainter.com** (Internazionale) [demoted]
- **magliarossonera.it** (AC Milan) [demoted]
- **almanaccogiallorosso.it** (AS Roma) [demoted]
- **laziowiki.org** (Lazio) [demoted]
- **lfchistory.net** (Liverpool) [demoted]
- **thearsenalhistory.com** (Arsenal) [demoted]
- **topspurs.com** (Tottenham) [demoted]
- **afcheritage.org** (Aberdeen) [demoted]
- **feyenoord.supporters.nl** (Feyenoord) [demoted]
- **fcgstats.nl** (FC Groningen) [demoted]
- **stats.sv-vitesse.nl** (Vitesse) [demoted]
- **heraclesstatistieken.nl** (Heracles) [demoted]
- **necarchief.nl** (NEC) [demoted]
- **der-betze-brennt.de** (Kaiserslautern) [demoted]
- **micha-s-fc-cologne-site.be** (1. FC Köln) [demoted]
- **asse-stats.com** (Saint-Étienne) [demoted]
- **om1899.com** (Marseille) [demoted]
- **racingstub.com** (RC Strasbourg) [demoted]
- **fcmetz.com** (FC Metz) [demoted — Maccabi played **Lens**, not Metz, in the 1999/00 UEFA Cup]
- **infoatleti.es** (Atlético Madrid) [demoted]
- **players.fcbarcelona.com** (FC Barcelona) [demoted]
- **athletic-club.eus** (Athletic Bilbao) [demoted]
- **rapidarchiv.at** (Rapid Wien) [demoted]
- **austria-archiv.at** (Austria Wien) [demoted]
- **bscyb.ch** (Young Boys) [demoted]
- **statistikk.til.no** (Tromsø IL) [demoted]
- **brondbystats.dk** (Brøndby) [demoted]
- **legia.net** (Legia Warsaw) [demoted]
- **historiawisly.pl** (Wisła Kraków) [demoted]
- **cska-games.ru** (CSKA Moscow) [demoted]
- **en.levskisofia.info** (Levski Sofia) [demoted]
- **en.fccska.com** (CSKA Sofia) [demoted]
- **dinamo-tbilisi.ru** (Dinamo Tbilisi) [demoted]

### Lower-division / niche clubs (no known Maccabi tie)

- **cfchistory.com** (Chesterfield) • **hattersheritage.co.uk** (Luton) • **millwall-history.org.uk** • **swindon-town-fc.co.uk** • **greensonscreen.co.uk** (Plymouth) • **carousel.royalwebhosting.net** (Notts County) • **neilbrown.newcastlefans.com** (transfers) • **grecianarchive.exeter.ac.uk** (Exeter) • **wrexhamafcarchive.co.uk** • **londonhearts.com** (Hearts)
- **dundalkfcwhoswho.com** — Dundalk played Maccabi UEL group 2016/17 → **promote to 5 if confirmed** (domain name matches, but verify site coverage)
- **eintracht-archiv.de** — ambiguous: if Eintracht Frankfurt → UEL group 2013/14 (Tier 5); if Braunschweig → no tie (Tier 2)
- **fsv05.de** (Mainz) • **preussenfieber.de** (Münster) • **kickersarchiv.de** (Stuttgart Kickers — note: **VfB Stuttgart** played Maccabi 2025/26, but this archive covers the separate Kickers club) • **kleeblatt-chronik.de** (Greuther Fürth) • **ludwigspark.de** (Saarbrücken) • **ochehoppaz.de** (SpVgg Unterhaching?) • **ffc-history.de** (FFC Frankfurt women)
- **cadistas1910.com** (Cádiz) • **ciberche.net** (Hércules/Betis?) • **sitercl.com** — if RC Lens → UEFA Cup 1999/00 **→ promote to 5**
- **sirapedia.it** (Siracusa) • **storiapiacenza1919.it** (Piacenza) • **wlecce.it** • **tifosolospezia.altervista.org** (Spezia) • **xoomer.virgilio.it/...taranto.html** (Taranto)
- **historie.brann.no** • **lynhistorie.com** (Lyn) • **ffksupporter.net** (Fredrikstad) • **efbhistorik.dk** (Esbjerg)
- **kanari-fansen.no** (Lillestrøm — wiki)
- **football.lg.ua** (Luhansk) • **sr.m.wikipedia.org/FK_Palilulac_Beograd** • **gencler.org** (Gençlerbirliği)

---

## ⚪ Self / primary sources

Not an external tier — separated so they don't dilute the external-archive signal.

- **maccabipedia.co.il** — this project itself
- **maccabi-tlv.co.il** — official Maccabi TLV club site

---

## 🔴 Tier 0 — Skip (no Maccabi fixture plausible)

South-American and unrelated regional sites:

- **acervosantosfc.com** (Santos) • **historiadeboca.com.ar** (Boca) • **gelp.org** (Gimnasia La Plata) • **elsitiodealmagro.com.ar** (Almagro) • **elviola.com.ar** (Argentine regional) • **galopedia.blogspot.com** • **bangu.net** (Bangu) • **bloglondrinense.blogspot.com** (Londrina) • **flaestatistica.com.br** (Flamengo) • **fluzao.xyz** (Fluminense) • **fripedia.blogspot.com** (Friburguense) • **gremiopedia.com** (Grêmio) • **historiadecolocolo.com** (Colo-Colo) • **historiadocoritiba.com.br** (Coritiba) • **historialblanquiazul.wordpress.com** (Alianza Lima) • **jogosdoguarani.com** (Guarani) • **memoriawanderers.cl** (Wanderers Valparaíso) • **meutimenarede.com.br** (São Paulo / generic Brazilian) • **uniaomania.com** (União São João) • **verdazzo.com.br** (Palmeiras) • **voltacopedia.blogspot.com** (Voltaço) • **drtareksaid.net** (Zamalek — Egyptian, no Maccabi fixture)

---

## Known gaps — confirmed Maccabi opponents whose archive wasn't in this thread

Candidates for future harvesting from elsewhere (not present in the FB list): Werder Bremen (CWC 1994/95), Grasshopper, Fenerbahçe, Tenerife, Lens, Boavista, Roda JC, PAOK, APOEL, Panathinaikos, Beşiktaş, Dynamo Kyiv, Stoke City, Eintracht Frankfurt, Porto, Zenit (Tier-4 candidate here), AZ Alkmaar, Dundalk (present at Tier 2 — investigate), Villarreal, Slavia Prague, Shakhtar Donetsk, RB Salzburg, Qarabag, Sivasspor, LASK, Zira, Aris Thessaloniki, OGC Nice, AEK Larnaca, Gent, Olympiacos, Braga, Midtjylland, Bodø/Glimt, Real Sociedad, Lyon, VfB Stuttgart, SC Freiburg, Bologna.

---

## Summary counts

| Tier | Count | Action |
|------|-------|--------|
| 5 | 15 sites | Index & mine for Maccabi match pages |
| 4 | 17 sites | Spot-check; promote on citation |
| 3 | 9 sites  | Keep as meta-league cross-references |
| 2 | ~60 sites (incl. 33 demoted from v1 Tier 5) | Ignore unless a lead surfaces |
| 0 | 22 sites | Skip entirely |
| self | 2 sites | Primary sources, not scored |

## Next steps

1. **Harvest Tier 5 Maccabi match URLs** — site schemas differ; expect a per-site adapter rather than one generic scraper.
2. **Resolve Tier 4 uncertainties** — especially IFK Göteborg, Benfica, Partizan (source conflict), Zenit (likely promotable).
3. **Disambiguate two Tier 2 domains**: `eintracht-archiv.de` (Frankfurt vs Braunschweig) and `sitercl.com` (RC Lens?) — each resolves to a Tier 5 opponent if the domain really covers that club.
4. **Skip Tier 0 entirely** and ignore further FB threads of this type that don't prefilter.
