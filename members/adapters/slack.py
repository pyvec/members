from operator import attrgetter

import requests


__all__ = ['members']


def members(api_token):
    usergroups_by_id = {}
    usergroups_ids_by_user_id = {}

    for usergroup, users_ids in generate_usergroups(api_token):
        usergroups_by_id[usergroup['id']] = usergroup
        for user_id in users_ids:
            usergroups_ids_by_user_id.setdefault(user_id, set())
            usergroups_ids_by_user_id[user_id].add(usergroup['id'])

    for user in generate_users(api_token):
        skip = (
            not user['profile'].get('email')
            or user.get('deleted')
            or user.get('is_bot')
        )
        if skip:
            continue

        usergroups = (usergroups_by_id[ug_id] for ug_id
                      in usergroups_ids_by_user_id.get(user['id'], []))
        yield to_member(user, usergroups)


def generate_usergroups(api_token, cursor=None):
    data = request_slack_api(api_token, 'usergroups.list')
    for usergroup in data['usergroups']:
        yield usergroup, list_usergroup_users_ids(api_token, usergroup)
    try:
        next_cursor = data['response_metadata']['next_cursor']
    except KeyError:
        pass
    else:
        yield from generate_usergroups(cursor=next_cursor)


def list_usergroup_users_ids(api_token, usergroup):
    data = request_slack_api(api_token, 'usergroups.users.list',
                             usergroup=usergroup['id'])
    if data.get('user_count'):
        assert len(data['users']) == int(data['user_count'])
    return data['users']


def generate_users(api_token, cursor=None):
    data = request_slack_api(api_token, 'users.list')
    for user in data['members']:
        yield user
    try:
        next_cursor = data['response_metadata']['next_cursor']
    except KeyError:
        pass
    else:
        yield from generate_users(api_token, cursor=next_cursor)


def request_slack_api(api_token, endpoint, **params):
    res = requests.get(f'https://slack.com/api/{endpoint}',
                       params=params,
                       headers={'Authorization': f'Bearer {api_token}'})
    res.raise_for_status()
    return res.json()


def to_member(user, usergroups):
    # https://api.slack.com/types/user
    # https://api.slack.com/types/usergroup

    profile = user['profile']

    # https://api.slack.com/changelog/2017-09-the-one-about-usernames
    name = profile.get('real_name') or profile.get('display_name')
    handle = profile.get('display_name') or profile.get('real_name')

    aliases = frozenset(filter(None, [
        profile.get('real_name'),
        profile.get('real_name_normalized'),
        profile.get('display_name'),
        profile.get('display_name_normalized'),
    ]))

    roles = filter(None, [
        'slack_owner' if user.get('is_owner') else None,
        'slack_admin' if user.get('is_admin') else None,
    ])

    teams = [{
        'source': 'slack',
        'name': ug['name'],
        'handle': ug['handle'],
        'description': ug['description'],
    } for ug in usergroups]

    avatars = filter(attrgetter('url'), [
        {'source': 'slack', 'url': profile.get('image_32')},
        {'source': 'slack', 'url': profile.get('image_192')},
    ])

    return {
        'name': name,
        'email': profile['email'],
        'avatars': avatars,
        'roles': roles,
        'aliases': aliases,
        'teams': teams,
        'descriptions': [profile['title']] if profile.get('title') else [],
        'slack_url': f"https://pyvec.slack.com/team/{user['id']}/",
        'slack': handle,
    }
