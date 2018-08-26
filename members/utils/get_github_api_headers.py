def get_github_api_headers(token=None, headers=None):
    headers = headers or {}

    if not token:
        return headers
    if token:
        headers.update({
            'User-Agent': 'pyvec-members/0.0',
            'Authorization': f'token {token}',
        })
        return headers
