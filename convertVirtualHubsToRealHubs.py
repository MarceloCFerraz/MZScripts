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
        8232,
        3748,
        3909,
        8101,
        8613,
        8102,
        8162,
        3909,
        8101,
        8103,
        8102,
        8613,
        8162,
        8103,
        8033,
        8081,
        8235,
        8463,
        8033,
        8560,
        8235,
        8081,
        8628,
        8560,
        8463,
        8845,
        8048,
        8845,
        8048,
        8819,
        8005,
        8006,
        8109,
        8819,
        8005,
        8006,
        8109
    ]

    virtual_hubs = list(set(virtual_hubs))

    with concurrent.futures.ThreadPoolExecutor() as pool:
        for vhub in virtual_hubs:
            pool.submit(get_real_hub, env, orgId, vhub)
    
    pool.shutdown(wait=True)

    print(f"{len(virtual_hubs)} in, {len(real_hubs)} out")

main()
