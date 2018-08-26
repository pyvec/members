import requests

from members.utils import get_github_api_headers


__all__ = ['members']


def members(org, token=None):
    usernames = set()

    users = paginate(f'https://api.github.com/orgs/{org}/members', token=token)
    for users in users:
        yield get_user(users['login'], org, token=token)
        usernames.add(users['login'])

    teams = paginate(f'https://api.github.com/orgs/{org}/teams', token=token)
    for team in teams:
        yield from generate_team_members(team, org, token=token)

    for username, repo_name in generate_contributions(org, token=token):
        if username not in usernames:
            yield get_user(username, org, token=token)
            usernames.add(username)
        yield {'github': username, 'github_repos_authored': [repo_name]}


def generate_team_members(team, org, token=None):
    url = f"https://api.github.com/teams/{team['id']}/members"
    res = request_api(url, token=token)
    res.raise_for_status()

    for team_member in res.json():
        yield {
            'github': team_member['login'],
            'teams': [{
                'source': f'github_{org}',
                'name': team['name'],
                'handle': f"{org}/team['slug']",
                'description': team['description'],
            }],
        }


def get_user(username, org, token=None):
    res = request_api(f'https://api.github.com/users/{username}', token=token)
    res.raise_for_status()
    user = res.json()

    member = {
        'github': username,
        'avatars': [{'source': 'github', 'url': user['avatar_url']}],
        'roles': [f'github_{org}'],
    }
    if user['name']:
        member['name'] = user['name']
    if user['email']:
        member['email'] = user['email']

    return member


def generate_contributions(org, token=None):
    repos = paginate(f'https://api.github.com/orgs/{org}/repos', token=token)
    for repo in repos:
        if (
            repo['private']
            or repo['fork']
            or repo['stargazers_count'] <= 1
            or repo['watchers_count'] <= 1
        ):
            continue  # skipping repos with low significance

        res = request_api(repo['contributors_url'], token=token)
        res.raise_for_status()
        contributors = res.json()

        if len(contributors) <= 3:
            continue  # skipping repos with low significance

        # let's consider the one with the most contributions to be the author
        primary_author = contributors[0]
        yield primary_author['login'], repo['full_name']

        # if the second one has at least 10% of the primary author's
        # contributions, let's assume they have significant knowledge to be
        # considered a co-author of the repository or to become one
        # in the future (we want to support avoiding burnout and bus factor)
        secondary_author = contributors[1]
        secondary_author_percentage = (
            (100 * secondary_author['contributions'])
            / primary_author['contributions']
        )
        if secondary_author_percentage > 10:
            yield secondary_author['login'], repo['full_name']


def paginate(url, token=None):
    page = 1
    while True:
        res = request_api(url, params={'page': page}, token=token)
        if res.status_code == 404:
            break
        res.raise_for_status()
        page += 1

        items = res.json()
        if not items:
            break
        yield from items


def request_api(url, **kwargs):
    if 'token' in kwargs:
        token = kwargs.pop('token')
        headers = kwargs.get('headers')
        kwargs['headers'] = get_github_api_headers(token, headers)
    return requests.get(url, **kwargs)
