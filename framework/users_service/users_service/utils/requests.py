import requests


def call_service(url, token):
    cookies = {"token": token}
    r = requests.get(url, cookies=cookies)
    if r.status_code != 200:
        return None
    return r.json()


def call_service_cart(url, service_token):
    headers = {"X-Service-Token": service_token}
    r = requests.post(url, headers=headers)
    if r.status_code != 201:
        return None
    return r.json()
