import re


__all__ = ['parse_profile_link']


def parse_profile_link(url):
    if url.startswith('mailto:'):
        email = re.sub(r' ?zavináč ?', '@', url.replace('mailto:', ''))
        return 'email', email

    if 'github.com' in url:
        username = parse_username(url, r'.*github\.com\/')
        return 'github', username

    if 'facebook.com' in url:
        username = parse_username(url, r'.*facebook\.com\/')
        return 'facebook', username

    if 'twitter.com' in url:
        username = parse_username(url, r'.*twitter\.com\/@?')
        return 'twitter', username

    if 'linkedin.com' in url:
        username = parse_username(url, r'.*linkedin\.com\/in\/')
        return 'linkedin', re.sub(r'\/.+$', '', username)

    if 'instagram.com' in url:
        username = parse_username(url, r'.*instagram\.com\/')
        return 'instagram', username

    return 'website', url


def parse_username(url, re_pattern):
    return re.sub(re_pattern, '', url).rstrip('/').lower()
