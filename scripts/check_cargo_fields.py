import requests

API_URL = 'https://www.maccabipedia.co.il/index.php'

for table in ['Football_Games', 'Volleyball_Games', 'Basketball_Games']:
    params = {
        'title': 'Special:CargoExport',
        'format': 'json',
        'tables': table,
        'fields': '_pageName',
        'limit': 1,
    }
    resp = requests.get(API_URL, params=params)
    print(f'{table}: {resp.text[:200]}')

# Try to find the winning game field name
params = {
    'title': 'Special:CargoExport',
    'format': 'json',
    'tables': 'Football_Games',
    'fields': '_pageName',
    'where': 'WinningGame="כן"',
    'limit': 3,
}
resp = requests.get(API_URL, params=params)
print(f'\nWinningGame test: {resp.text[:300]}')

params['where'] = 'IsWinningGame="כן"'
resp = requests.get(API_URL, params=params)
print(f'IsWinningGame test: {resp.text[:300]}')
