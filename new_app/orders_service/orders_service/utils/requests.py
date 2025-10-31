import requests


def call_service(url, token):
    cookies = {"access_token": token}
    r = requests.get(url, cookies=cookies)
    if r.status_code == 401:
        return {
            "status_code": r.status_code,
            "data": {"message": "O token fornecido é inválido ou está ausente."},
        }
    return {"status_code": r.status_code, "data": r.json() if r.content else None}


def call_service_update_cart(url, token, data):
    cookies = {"access_token": token}
    r = requests.post(url, cookies=cookies, data=data)
    if r.status_code == 401:
        return {
            "status_code": r.status_code,
            "data": {"message": "O token fornecido é inválido ou está ausente."},
        }
    return {"status_code": r.status_code, "data": r.json() if r.content else None}


def call_service_patch(url, token, data):
    cookies = {"access_token": token}
    r = requests.patch(url, cookies=cookies, data=data)
    if r.status_code == 401:
        return {
            "status_code": r.status_code,
            "data": {"message": "O token fornecido é inválido ou está ausente."},
        }
    return {"status_code": r.status_code, "data": r.json() if r.content else None}
