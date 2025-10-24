import requests


def call_service(self, url, token):
    cookies = {"token": token}
    r = requests.get(url, cookies=cookies)
    if r.status_code != 200:
        return None
    return r.json()
