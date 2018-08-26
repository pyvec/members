import requests

from members.utils import scrape, get_first_as_text, parse_profile_link


__all__ = ['members']


PERSON_CSS = ['.team-member', '.team__person']
PERSON_NAME_CSS = ['.name', '.team__person__name']


def members():
    for year in generate_years():
        try:
            root_el = scrape(f'https://cz.pycon.org/{year}/')
        except requests.RequestException as exc:
            if exc.response.status_code == 404:
                break
            else:
                raise exc
        else:
            event = f'pyconcz{year}'
            event_name = f'PyCon CZ {year}'

            team_page_link = get_team_page_link(root_el)
            root_el = scrape(team_page_link)

            for person_el in root_el.cssselect(', '.join(PERSON_CSS)):
                name = get_first_as_text(
                    person_el.cssselect(', '.join(PERSON_NAME_CSS))
                )

                member = {
                    'name': name,
                    'roles': [f'{event}_org'],
                    'teams': [{
                        'source': event,
                        'name': event_name,
                        'description': (
                            f'Tým {event_name} jak je uveden '
                            'na webu konference'
                        ),
                    }],
                }

                for link_el in person_el.cssselect('a'):
                    key, value = parse_profile_link(link_el.get('href'))
                    member[key] = value

                for img_el in person_el.cssselect('img'):
                    member['avatars'] = [
                        {'source': event, 'url': img_el.get('src')}
                    ]

                yield member


def get_team_page_link(root_el):
    return root_el.cssselect('a[href*="about/team"]')[0].get('href')


def generate_years():
    year = 2015
    while True:
        yield year
        year += 1
