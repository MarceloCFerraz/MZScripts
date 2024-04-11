import datetime
import time
from concurrent.futures import ThreadPoolExecutor

import requests

from utils import hubs, utils

pending_retries = set()


def retry_request(env, requestId):
    retry = f"http://tesseract.{utils.convert_env(env)}.milezero.com/Tesseract-war/api/processor/retry/{requestId}"
    check = f"http://tesseract.{utils.convert_env(env)}.milezero.com/Tesseract-war/api/request/detail/{requestId}"

    requests.post(url=retry)
    response = requests.get(url=check).json()
    if response.get("requestStatus") is not None:
        current = response["requestStatus"].get("currentProcessState")
        print(f'Current Status of "{requestId}": {current}')

        if current != "COMPLETED":
            pending_retries.add(requestId)


def reretry_request(env, requestId):
    print(f"Re-re-trying {requestId}")

    status = "FAILED"

    retry = f"http://tesseract.{utils.convert_env(env)}.milezero.com/Tesseract-war/api/processor/retry/{requestId}"
    check = f"http://tesseract.{utils.convert_env(env)}.milezero.com/Tesseract-war/api/request/detail/{requestId}"

    while status != "COMPLETED":
        response = requests.get(url=check).json()

        if response.get("requestStatus") is not None:
            status = response["requestStatus"].get("currentProcessState")

        if status == "COMPLETED":
            return

        if status == "FAILED":
            print(f"We'll have to retry {requestId} ({status}) again after 5s")
            requests.post(url=retry)
            time.sleep(5)


if __name__ == "__main__":
    env = utils.select_env()
    orgId = utils.select_org(env)
    allHubs = hubs.get_all_hubs(env, orgId)
    start_date = datetime.datetime.strptime(
        input("Input the Original Date (yyyy-mm-dd): ").strip(), "%Y-%m-%d"
    )
    # adding 5 hrs because files started failing at 5am UTC
    start_date = datetime.timedelta(hours=5) + start_date
    end_date = datetime.timedelta(days=1) + start_date

    # We don't need the timezone to be set since we're just getting everything into a string
    start_date_str = start_date.strftime("%Y-%m-%dT%H:%M:%SZ").replace(":", "%3A")
    end_date_str = end_date.strftime("%Y-%m-%dT%H:%M:%SZ").replace(":", "%3A")

    with ThreadPoolExecutor() as pool:
        for hub in allHubs:
            hubId = hub["id"]
            state = "FAILED"

            i = 0

            url = f"http://tesseract.{utils.convert_env(env)}.milezero.com/Tesseract-war/api/request/status/{orgId}?startDate={start_date_str}&endDate={end_date_str}&filterByState={state}&hubId={hubId}&pageNumber={i}&pageSize=10000"
            response = requests.get(url=url)
            reqs = set()

            if not response:
                continue

            response = response.json()

            while len(response) > 0:
                print(f"HubId: {hubId} I: {i} Len: {len(response)}")
                for req in response:
                    requestId = req["id"]
                    print(f"Retrying request {requestId}")
                    pool.submit(retry_request, env, requestId)
                    reqs.add(requestId)

                i += 1
                url = f"http://tesseract.{utils.convert_env(env)}.milezero.com/Tesseract-war/api/request/status/{orgId}?startDate={start_date_str}&endDate={end_date_str}&filterByState={state}&hubId={hubId}&pageNumber={i}&pageSize=10000"
                response = requests.get(url=url).json()

    pool.shutdown(True)

    print(f"Failed retries: {len(pending_retries)}")

    with ThreadPoolExecutor() as pool:
        for requestId in pending_retries:
            # iterate through and retry until they pass
            pool.submit(reretry_request, env, requestId)

    pool.shutdown(True)
