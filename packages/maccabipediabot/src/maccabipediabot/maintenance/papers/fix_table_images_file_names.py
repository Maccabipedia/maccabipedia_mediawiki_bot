from maccabipediabot.common.paths import papers_root

if __name__ == '__main__':
    base = papers_root() / 'מעריב' / 'טבלאות 84-85'

    for table in base.iterdir():
        try:
            fixture_number = [int(num) for num in table.stem.split() if num.isdigit()][0]
            table.rename(table.parent / f'טבלת ליגה עונת 1984-85 לאחר מחזור {fixture_number}.jpg')
        except Exception as e:
            print(e)
