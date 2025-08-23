from pathlib import Path

if __name__ == '__main__':
    base = Path(r'C:\code\maccabipedia_mediawikibot\games_papers_to_upload\from_drive\מעריב\טבלאות 84-85')

    for table in base.iterdir():
        try:
            fixture_number = [int(num) for num in table.stem.split() if num.isdigit()][0]
            table.rename(table.parent / f'טבלת ליגה עונת 1984-85 לאחר מחזור {fixture_number}.jpg')
        except Exception as e:
            print(e)
