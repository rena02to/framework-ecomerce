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
