from members.utils import scrape, get_first_as_text, parse_profile_link


__all__ = ['members']


def members():
    links = scrape('https://pyladies.cz/').cssselect('.navbar-cities li a')

    for link in links:
        root_el = scrape(link.get('href'))
        city = get_first_as_text(root_el.cssselect('.current-page .city-title'))  # NOQA

        for person_el in root_el.cssselect('.team .person'):
            avatars = filter(None, (
                {'source': 'pyladies', 'url': img_el.get('src')}
                for img_el in person_el.cssselect('img.img-circle')
                if not img_el.get('src', '').endswith('blank.png')
            ))

            role = get_first_as_text(person_el.cssselect('em')).lower()
            role = 'pyladies_org' if 'org' in role else 'pyladies_coach'

            member = {
                'name': get_first_as_text(person_el.cssselect('.member-name')),
                'avatars': avatars,
                'roles': [role],
                'teams': [{
                    'source': 'pyladies',
                    'name': f'PyLadies {city}',
                    'description': f'Tým PyLadies {city}',
                }]
            }

            for link_el in person_el.cssselect('a'):
                key, value = parse_profile_link(link_el.get('href'))
                member[key] = value

            yield member
