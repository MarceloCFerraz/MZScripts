import json
from urllib import response
import requests
import csv


org_id = "3c897e84-3957-4958-b54d-d02c01b14f15"

# revive_url = "http://switchboard.prod.milezero.com/switchboard-war/api/package/revive/{0}/{1}"


# 0 is orgId 1 is packageId
# switchboard_update_status_url = "http://switchboard.prod.milezero.com/switchboard-war/api/package/update/{0}/{1}/PACKED/status"

switchboard_resubmit_url = "http://switchboard.prod.milezero.com/switchboard-war/api/fulfillment/resubmit/3c897e84-3957-4958-b54d-d02c01b14f15/{0}"

# switchboard_package_url = "http://switchboard.prod.milezero.com/switchboard-war/api/package?keyType=bc&keyValue={0}"



# def revive(org_id, package_id):
#     revive_packages_url = revive_url.format(org_id, package_id)
#     headers = {'content-type': 'application/json'}
#     payload = {
#         "notes": "Uncancel Package per dispatch requests"
#     }
#     response = requests.post(revive_packages_url, data=json.dumps(payload), headers=headers)
#     print("Revive response")
#     print(response)

# def update_package_status(package_id):
#     update_url = switchboard_update_status_url.format(org_id, package_id)
#     headers = {'content-type': 'application/json'}
#     payload = {
#         "notes": "Requested by dispatch"
#     }

#     response = requests.post(update_url, data=json.dumps(payload), headers=headers)
#     print("update response")
#     print(response)


def switchbord_resubmit(packageid):
    headers = {'content-type': 'application/json'}
    switchboard_url = switchboard_resubmit_url.format(packageid)
    payload = {
        "adjustTimeWindow": "true",
        "targetLocalDate": "2023-07-24",
        "notes": "Requested by dispatch"
    }
    response = requests.post(switchboard_url, data=json.dumps(payload), headers=headers)
    print("resubmit response")
    print(response)
    return response



# def get_package_id(container_id):
#     get_package_id_url = switchboard_package_url.format(container_id)
#     response = requests.get(url=get_package_id_url,
#                             headers={'Accept': 'application/json'})
#     print(response)
#     pid = response.json().get("packageRecords")[0].get("packageId")
#     print(pid)
#     return pid



if __name__ == '__main__':
    with open('revivePackages.csv') as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        for row in readCSV:
            print(row[0])
            # package_id = get_package_id(row[0])
            package_id = row[0]
            # update_package_status(package_id)
            # revive(org_id, package_id)
            switchbord_resubmit(package_id)