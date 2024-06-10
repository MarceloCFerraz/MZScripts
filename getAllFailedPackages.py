from concurrent.futures import ThreadPoolExecutor

import requests

PKGS = []
SUCCESSES = []
ERRORS = []


def divide_into_batches(lst, batch_size=100):
    batches = []
    for i in range(0, len(lst), batch_size):
        batch = lst[i : i + batch_size]
        batches.append(batch)
    return batches


def get_failed_packages():
    get_failed_url = "https://switchboard.prod.milezero.com/switchboard-war/api/package/search/3c897e84-3957-4958-b54d-d02c01b14f15/failed?startTime=2024-06-05T00%3A00%3A00Z&endTime=2024-06-07T04%3A59%3A00Z"
    response = requests.get(url=get_failed_url, timeout=10000)

    return response.json()


def bulk_get_package_details(env, org_id, key_type, keys):
    url = f"https://switchboard.{env}.milezero.com/switchboard-war/api/package/search/bulk"

    payload = {
        "idType": key_type,
        "ids": keys,
        "filters": {
            "orgId": org_id,
            "includeCancelledPackage": True,
        },
    }

    print(payload)

    return requests.post(url=url, json=payload, timeout=30).json()


def get_packages_with_no_route(batch, org, env):
    pkgs = bulk_get_package_details(env, org, "pi", batch)["packageRecords"]

    for pkg in pkgs:
        if not pkg["planningDetails"].get("plannerRouteId"):
            PKGS.append(pkg)


def revive_package(env, package):
    API = f"http://switchboard.{env}.milezero.com/switchboard-war/api/"
    org_id = package["orgId"]
    packageId = package["packageId"]
    requestData = {"notes": "Requested by dispatcher"}

    endpoint = "{}package/revive/{}/{}".format(API, org_id, packageId)

    print(f">>>>> Reviving {packageId} <<<<<")

    response = requests.post(endpoint, json=requestData, timeout=15)
    print(
        f"{response.status_code} {response.text if response.status_code > 400 else ''}"
    )


def mark_package_as_delivery_failed(env, package):
    org_id = package["orgId"]
    packageId = package["packageId"]

    url = f"http://switchboard.{env}.milezero.com/switchboard-war/api/package/update/{org_id}/{packageId}/DELIVERY_FAILED/status"

    requestData = {"notes": "Requested By Dispatcher"}

    print(f">>>>> Marking {packageId} as DELIVERY_FAILED <<<<<")

    try:
        response = requests.post(url=url, json=requestData, timeout=15)
        print("> OK" if response.status_code < 400 else f"> FAIL\n{response.text}")
    except Exception as e:
        print("> Package couldn't be marked as DELIVERY_FAILED. See error bellow")
        print(e)


def prepare_package_for_replan(env, package):
    status = package["packageStatuses"]["status"]
    REVIVE_STATUSES = ["CANCELLED"]
    DELIVERY_FAILED_STATUSES = ["REJECTED", "DAMAGED", "DELIVERED"]

    # if package is marked as cancelled or damaged,
    # revive the package
    if status in REVIVE_STATUSES:
        revive_package(env, package)

    # if package is marked as rejected or delivered,
    # change its status to DELIVERY_FAILED
    if status in DELIVERY_FAILED_STATUSES:
        mark_package_as_delivery_failed(env, package)


def replan_batch(env, orgId, batch: list[dict], next_delivery_date):
    packageIDs = []

    for package in batch:
        # if package is from the correct hub or if we don't want to filter by hub, continues
        prepare_package_for_replan(env, package)

        packageIDs.append(package["packageId"])

    if packageIDs:
        result = bulk_resubmit_packages(env, orgId, packageIDs, next_delivery_date)

        for success in result["SUCCESS"]:
            SUCCESSES.append(success)

        for error in result["ERROR"]:
            ERRORS.append(error)


def bulk_resubmit_packages(env, org_id, packageIDs, next_delivery_date):
    url = f"https://switchboard.{env}.milezero.com/switchboard-war/api/fulfillment/resubmit/bulk/{org_id}"

    requestData = {
        "packageIds": packageIDs,
        "adjustTimeWindow": True,
        "treatEverydayAsProcessingDay": False,
        "targetLocalDate": next_delivery_date,
        "notes": "To fix null route",
    }

    response = requests.post(url=url, json=requestData, timeout=15).json()
    res = {"SUCCESS": [], "ERROR": []}

    for success in response.get("succeededResubmits"):
        res["SUCCESS"].append(success.get("packageId"))

    for error in response.get("failedResubmits"):
        res["ERROR"].append(error.get("packageId"))

    print(
        f">>>>> New Batch ({len(packageIDs)} {next_delivery_date}) <<<<<\n"
        + f"> {len(res['SUCCESS'])} OK\t {len(res['ERROR'])} FAILED"
    )

    return res


def print_results():
    total = len(SUCCESSES) + len(ERRORS)

    print(f"Successful Resubmits ({len(SUCCESSES)}/{total}): ")
    print(SUCCESSES)

    print(f"Unsuccessful Resubmits ({len(ERRORS)}/{total}): ")
    print(ERRORS)


if __name__ == "__main__":
    env = "prod"
    org = "3c897e84-3957-4958-b54d-d02c01b14f15"

    print("Loading failed packages")
    failed_packages = get_failed_packages()["packages"]
    pids = list(set([p["packageId"] for p in failed_packages]))

    print(f"loaded {len(failed_packages)}")

    print("Splitting into batches of 100")
    batches = divide_into_batches(pids)

    print("Fetching for package details")
    with ThreadPoolExecutor() as pool:
        for batch in batches:
            pool.submit(get_packages_with_no_route, batch, org, env)
    pool.shutdown(True)

    print(f"{len(PKGS)} packages with no routes")

    print("Splitting them into batches")
    batches = divide_into_batches(PKGS)

    print("Resubmitting packages")
    with ThreadPoolExecutor() as pool:
        for batch in batches:
            pool.submit(replan_batch, env, org, batch, "2024-06-07")
    pool.shutdown(True)

    print_results()
