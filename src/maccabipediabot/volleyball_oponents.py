import logging

from pywikibot_boilerplate import run_boilerplate

run_boilerplate()

import pywikibot as pw
from mwparserfromhell.nodes.template import Template

site = pw.Site()
site.login()

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

FOOTBALL_REFEREES = {"בורגר ",
"ביטון ",
"בייסק ",
"בן רובי ",
"בראדי (אנגליה) ",
"בראון ",
"ג'. פרוט ",
"גאון ",
"גוטארד ",
"גוטר ",
"גלמן ",
"גלן ניברג (שבדיה) ",
"גרינפלד ",
"ד. קווין ",
"דודאי ",
"דוידה מאסה (איטליה) ",
"דונאהי ",
"דניס היגלר (הולנד) ",
"הנק ואן דייקן ",
"הנרי דולאן ",
"הרמלין ",
"ו. טרואנה ",
"וורד ",
"וורנר ",
"וסרמן ",
"ז'רום בריסאר (צרפת) ",
"זהבי ",
"זילברג ",
"זמסקי ",
"חוסה מריה סאנצ'ס ",
"טום קרומפטון ",
"טיאגו מרטינס (פורטוגל) ",
"טיילור ",
"טרסטין פארוג'יה קאן (מלטה) ",
"יאסטז'מבסקי ",
"יון ",
"יונגרמן ",
"יצחק לוי ",
"כריסטופר יאגר (אוסטריה) ",
"לוינגר ",
"לייכטר ",
"לרנר ",
"מיטשל ",
"מייקל אוליבר (אנגליה) ",
"מיקולה בלאקין (אוקראינה) ",
"מקנזי ",
"מריו זבץ (קרואטיה) ",
"מרקוס ",
"נומרמן ",
"ניקולה דבאנוביץ' (מונטנגרו) ",
"סאשה סטגמן (גרמניה) ",
"סטולרי ",
"סלמי ",
"סרג'נט ס.מקנזי ",
"סרגנט מקנזי ",
"סרדיאן יובאנוביץ' (סרביה) ",
"עזיז ",
"פאבל אורל (צ'כיה) ",
"פייט ",
"פלזנשטיין ",
"פליקס ברייך (גרמניה) ",
"פרוינר ",
"פרנסואה לטייר (צרפת) ",
"קונסט ",
"קיריל לבניקוב (רוסיה) ",
"קליין ",
"קמינגס ",
"קמפיאס ",
"קרול ",
"ראדה אוברנוביץ' (סלובניה) ",
"רוב הנסי (אירלנד) ",
"רוברט הנסי (אירלנד) ",
"רון ואן דה ון ",
"שרגא רובינשטיין ",
"שרם "}

SHOULD_SAVE = True
SHOULD_SHOW_DIFF = True


def open_opponents_pages():
    for referee_name in FOOTBALL_REFEREES:
        canonical_name = referee_name.strip()
        game_page = pw.Page(site, f'כדורגל:{canonical_name} (שופט)')

        current_template = Template("שופט כדורגל\n")
        current_template.add("שם להצגה", f'{canonical_name}\n')

        game_page.text = str(current_template)

        if SHOULD_SAVE:
            logging.info("Saving {name}".format(name=game_page.title()))
            game_page.save(summary="MaccabiBot - Uploading football referees")


if __name__ == '__main__':
    open_opponents_pages()
