import requests
from lxml import html


__all__ = ['scrape']


def scrape(url):
    res = requests.get(url)
    res.raise_for_status()
    root_el = html.fromstring(res.content)
    root_el.make_links_absolute(res.url)
    return root_el
