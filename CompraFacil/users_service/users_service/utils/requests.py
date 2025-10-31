import requests


def call_service(url, token):
    cookies = {"token": token}
    r = requests.get(url, cookies=cookies)
    if r.status_code == 401:
        return {
            "status_code": r.status_code,
            "data": {"message": "O token fornecido é inválido ou está ausente."},
        }
    return {"status_code": r.status_code, "data": r.json() if r.content else None}


def call_service_cart(url, service_token):
    headers = {"X-Service-Token": service_token}
    r = requests.post(url, headers=headers)
    if r.status_code == 401:
        return {
            "status_code": r.status_code,
            "data": {"message": "O token fornecido é inválido ou está ausente."},
        }
    return {"status_code": r.status_code, "data": r.json() if r.content else None}
