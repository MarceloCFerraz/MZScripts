import requests

def get_location(env, locationId):
    url = f"http://lockbox.{env}.milezero.com/lockbox-war/api/location/{locationId}"

    return requests.get(url=url, timeout=5).json()