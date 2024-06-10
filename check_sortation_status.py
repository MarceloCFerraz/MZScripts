import pprint

import requests
import requests

pp = pprint.PrettyPrinter(indent=2)

date = "2024-06-06"
hub_name = "3880"

get_hub_packages_url = "http://switchboard.prod.milezero.com/switchboard-war/api/package/search/3c897e84-3957-4958-b54d-d02c01b14f15/{}/actionday?action=PACK&localDate={}"

get_ss_package_details_url = "http://sortationservices.prod.milezero.com/SortationServices-war/api/package/details/PI/{}/3c897e84-3957-4958-b54d-d02c01b14f15/true"

headers = {"content-type": "application/json"}


def get_hub_packages():
    response = requests.get(
        url=get_hub_packages_url.format(hub_name, date), headers=headers
    )
    data = response.json()
    return data


def check_sortation(package_id):
    response = requests.get(
        url=get_ss_package_details_url.format(package_id), headers=headers
    )
    if not response.status_code == 200:
        print(package_id)


if __name__ == "__main__":
    hub_packages = get_hub_packages()
    for package in hub_packages["packageRecords"]:
        check_sortation(package["packageId"])
