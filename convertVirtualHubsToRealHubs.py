import requests
from utils import utils
import concurrent.futures


real_hubs = []


def get_real_hub(env, orgId, virtualHub):
    url = f"http://tesseract.{env}.milezero.com/Tesseract-war/api/config/hub/{orgId}?countryCode=USA&companyBrandCode=01&posInstanceNumber={virtualHub}"

    response = requests.get(url=url, timeout=5).json()

    try:
        real_hubs.append(response['hubName'])
        print(f"{virtualHub} -> {response['hubName']}")
    except Exception as e:
        print(f"{virtualHub}")


def main():
    env = utils.select_env()
    orgId = utils.select_org(env)

    virtual_hubs = [
    ]

    virtual_hubs = list(set(virtual_hubs))

    with concurrent.futures.ThreadPoolExecutor() as pool:
        for vhub in virtual_hubs:
            pool.submit(get_real_hub, env, orgId, vhub)
    
    pool.shutdown(wait=True)

    print(f"{len(virtual_hubs)} in, {len(real_hubs)} out")

main()
