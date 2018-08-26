import requests


__all__ = ['members']


def members():
    res = requests.get('http://pyvec.org/cs/api.json')
    res.raise_for_status()

    for entry in res.json()['members']['entries']:
        member = {
            'name': entry['name'],
            'roles': [f"pyvec_{entry['role']}"],
            'teams': [{
                'source': 'pyvec',
                'name': f'Pyvec',
                'description': f'Neziskovka Pyvec',
            }]
        }
        if entry.get('github'):
            member['github'] = entry['github']
        if entry.get('twitter'):
            member['twitter'] = entry['twitter']
        if entry.get('linkedin'):
            member['linkedin'] = entry['linkedin']
        yield member
