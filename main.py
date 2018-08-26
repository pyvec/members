import os
import json
import itertools
import hashlib

import requests

from members.adapters import github, pyconcz, pyladies, pyvec, pyvo, slack


__all__ = ['main']


def main(slack_api_token=None, github_token=None):
    all_members = (Member(m) for m in itertools.chain.from_iterable([
        github.members('pyvec', token=github_token),
        github.members('pyladiescz', token=github_token),
        pyconcz.members(),
        pyladies.members(),
        pyvec.members(),
        pyvo.members(github_token=github_token),
        slack.members(slack_api_token),
    ]))

    unique_members = (
        merge_members(group) for grouper, group
        in itertools.groupby(sorted(all_members))
    )

    print(json.dumps(list(unique_members), ensure_ascii=False, indent=2))


class Member(dict):
    unique_keys = [
        'email', 'github', 'twitter', 'linkedin', 'facebook',
        'instagram', 'slack',
    ]

    def __eq__(self, other):
        return any(
            self[key] == other[key]
            for key in self.keys()
            if (key in Member.unique_keys and other.get(key))
        )

    def __gt__(self, other):
        return self.__ne__(other)


def merge_members(members):
    merged = {}

    for member in members:
        for key in ['name', 'email', 'github', 'twitter', 'linkedin',
                    'facebook', 'instagram', 'slack', 'slack_url', 'website']:
            merged.setdefault(key, member.get(key))

        for key in ['aliases', 'descriptions', 'github_repos_authored',
                    'roles']:
            merged.setdefault(key, set())
            merged[key].update(member.get(key) or [])

        for key in ['teams', 'avatars']:
            merged.setdefault(key, [])
            merged[key] += member.get(key) or []

        if member.get('name'):
            merged['aliases'].add(member['name'])

    if merged['email']:
        email = merged['email'].lower().strip()
        email_hash = hashlib.md5(email.encode()).hexdigest()
        merged['avatars'].append({
            'source': 'gravatar',
            'url': f'https://www.gravatar.com/avatar/{email_hash}?size=100&d=404',
        })

    merged['avatars'] = [
        {'source': a['source'], 'url': res.url} for (res, a) in
        ((requests.get(a['url']), a) for a in merged['avatars'])
        if res.ok
    ]

    for key in ['aliases', 'descriptions', 'github_repos_authored',
                'roles']:
        merged[key] = list(merged[key])
    del merged['email']

    return merged


if __name__ == '__main__':
    main(slack_api_token=os.environ.get('SLACK_API_TOKEN'),
         github_token=os.environ.get('GITHUB_TOKEN'))
