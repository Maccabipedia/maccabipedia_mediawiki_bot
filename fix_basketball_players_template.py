import logging

import mwparserfromhell
from pywikibot import pagegenerators

from pywikibot_boilerplate import run_boilerplate

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.DEBUG)

# We need to log before we run any of our maccabipedia (pywikibot or it's import) related code
site = run_boilerplate()

basketball_player_template_name = "פרופיל כדורסל"


def fix_basketball_players_page() -> None:
    logging.info(f'Iterating pages')
    category_iterator = pagegenerators.AllpagesPageGenerator(namespace=3003, site=site)

    for basketball_player_page in category_iterator:
        if '{{פרופיל כדורסל' not in basketball_player_page.text:
            logging.info(f'Skipping page: {basketball_player_page.title()}')
            continue
        parsed_mw_text = mwparserfromhell.parse(basketball_player_page.text)
        template = parsed_mw_text.filter_templates(basketball_player_template_name)[0]

        if template.has("עונות כשחקן"):
            template.remove("עונות כשחקן")

        if template.has("מספר תארים כשחקן"):
            template.remove("מספר תארים כשחקן")

        if template.has("אזרחות"):
            template.remove("אזרחות")

        if template.has("תאריך לידה"):
            template["תאריך לידה"] = str(template.get("תאריך לידה").value).strip().replace("-", ".")

        if template.has("תאריך פטירה"):
            template["תאריך פטירה"] = str(template.get("תאריך פטירה").value).strip().replace("-", ".")

        if template.has("גובה"):
            original_height_value = str(template.get("גובה").value)
            target_height_value = original_height_value.split()[0]
            if original_height_value.strip() != target_height_value:
                if not '.' in target_height_value:
                    a=6
                else:
                    template["גובה"] = target_height_value

        basketball_player_page.text = parsed_mw_text
        basketball_player_page.save(summary="MaccabiBot - Updating basketball players page", botflag=True)

if __name__ == '__main__':
    fix_basketball_players_page()
