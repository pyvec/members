import base64

import requests
import yaml

from members.utils import get_github_api_headers


__all__ = ['members']


def members(github_token=None):
    url = 'https://api.github.com/repos/pyvec/pyvo-data/contents'
    res = requests.get(f'{url}/series/', params={'ref': 'master'},
                       headers=get_github_api_headers(github_token))
    res.raise_for_status()

    series_files = (f"{item['path']}/series.yaml" for item
                    in res.json() if item['type'] == 'dir')
    for series_file in series_files:
        res = requests.get(f'{url}/{series_file}', params={'ref': 'master'})
        res.raise_for_status()

        try:
            data = yaml.safe_load(base64.b64decode(res.json()['content']))
            for organizer in data['organizer-info']:
                yield {
                    'name': organizer['name'],
                    'email': organizer['mail'],
                    'teams': [{
                        'source': 'pyvo',
                        'name': data['name'],
                        'description': f"{data['name']} - organizační tým",
                    }]
                }
        except KeyError:
            continue
