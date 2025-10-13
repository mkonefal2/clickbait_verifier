import requests


def fetch(url, timeout=10):
    r = requests.get(url, timeout=timeout)
    r.raise_for_status()
    return r.text
