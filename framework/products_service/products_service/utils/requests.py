import requests


def call_service(url, token):
    cookies = {"access_token": token}
    response = requests.get(url, cookies=cookies)
    if response.status_code != 200:
        return None
    return response.json()
