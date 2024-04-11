import datetime
import json
import time
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import cpu_count

import requests

from utils import utils
from utils.files import save_json_to_file

thread_count = cpu_count()
FAILED_REQUESTS = []
DETAILED_REQUESTS = []


def retry(env: str, requestId: str):
    url = f"http://tesseract.{utils.convert_env(env)}.milezero.com/Tesseract-war/api/processor/retry/{requestId}"

    response = requests.post(url=url)

    print(
        f"Retry for Request ID {requestId}: {response.status_code} "
        + f'{response.json().get("message") if response.status_code >= 400 else ""}'
    )


def check_request(env: str, requestId: str):
    url = f"http://tesseract.{utils.convert_env(env)}.milezero.com/Tesseract-war/api/request/detail/{requestId}"

    return requests.get(url=url).json()


def save_failed_request(newReq):
    requestId = newReq["requestStatus"]["id"]
    status = newReq["requestStatus"]["currentProcessState"]

    processing_notes = newReq["requestStatus"]["processingResponse"]
    processing_notes = processing_notes["detail"]["recordDetails"]

    header = f"{len(processing_notes)} warnings"
    messages = processing_notes
    details = newReq["orderStatuses"]

    inner_body = dict(status=status, header=header, messages=messages, details=details)

    response = {requestId: inner_body}

    FAILED_REQUESTS.append(response)


def get_request_file(env: str, requestId: str):
    url = f"http://tesseract.{utils.convert_env(env)}.milezero.com/Tesseract-war/api/request/file/{requestId}"

    return requests.get(url=url).json()


def save_completed_request(req, requestId):
    print(f"{requestId} was completed successfully. Saving its data")

    name = req["fileName"]
    content = req["parsedFileContents"]

    inner_body = dict(file=name, contents=content, status="COMPLETED")

    response = {requestId: inner_body}

    DETAILED_REQUESTS.append(response)


def check_if_failed(env: str, requestId: str):
    print(f"Checking if {requestId} is still failing")
    request = check_request(env, requestId)

    if request is None or request.get("requestStatus") is None:
        print("Couldn't find request details")
        return

    status = request["requestStatus"]["currentProcessState"]
    print(f"{requestId}'s status is {status}")

    count = 0
    max_retries = 3

    while status != "COMPLETED" and status != "FAILED" and count < max_retries:
        print("Waiting before checking request status again")
        time.sleep(5)

        print(f"Re-checking {requestId}: {count + 1}")
        request = check_request(env, requestId)

        if request is None or request.get("requestStatus") is None:
            print("Couldn't find request details")
            return

        status = request["requestStatus"]["currentProcessState"]
        count += 1

    if status != "COMPLETED":
        print(f"Re-checked {count} times, {requestId} status: {status}")
        save_failed_request(request)
    else:
        print(f"Request {requestId} is COMPLETED")
        print("Getting the file data and saving now")

        req = get_request_file(env, request["id"])
        save_completed_request(req, requestId)


def process_requests(env: str, thread_number: int, request_list: list):
    global thread_count

    if len(request_list) == 0:
        return
    # each thread will operate on an interval TO AVOID DATA RACES
    # according to my tests, splitting the integer conversion to a different line already solves the issue where
    # a thread overlaps the job of another thread or leave some request behind
    # don't ask me why, but here's my test: https://github.com/MarceloCFerraz/MZScripts/blob/master/experiments.ipynb
    requests_per_thread = len(request_list) / thread_count
    higher_limit = requests_per_thread * thread_number
    lower_limit = higher_limit - requests_per_thread

    higher_limit = int(higher_limit)
    lower_limit = int(lower_limit)

    print(
        f"Thread {thread_number} is processing requests '{lower_limit}' to '{higher_limit}' (top exclusive). "
        + f"Total = {higher_limit - lower_limit}"
    )

    for i in range(lower_limit, higher_limit):
        req = request_list[i]

        retry(env, req["id"])
        check_if_failed(env, req["id"])


def fetch_requests(url: str):
    response = requests.get(url=url, timeout=300).json()

    try:
        err = response.get("message")

        if err is not None:
            print(f"An error occurred: {err}")
            return []
    except Exception:
        # if there is an error accessing "message", it's because the object is an array, so nothing to worry about
        return []

    return response


if __name__ == "__main__":
    request_list = []
    full = False
    done = False
    page_number = 0
    page_size = 50
    max_requests = thread_count * page_size

    env = utils.select_env()
    orgId = utils.select_org(env)
    start_date = datetime.datetime.strptime(
        input("Input the Original Date (yyyy-mm-dd): ").strip(), "%Y-%m-%d"
    )
    # fetch every all dates in between, including today
    end_date = datetime.timedelta(days=1) + datetime.datetime.now()

    # We don't need the timezone to be set since we're just getting everything into a string
    start_date_str = start_date.strftime("%Y-%m-%dT%H:%M:%SZ").replace(":", "%3A")
    end_date_str = end_date.strftime("%Y-%m-%dT%H:%M:%SZ").replace(":", "%3A")

    state = "FAILED"
    response = ["not empty"]

    url = f"http://tesseract.{utils.convert_env(env)}.milezero.com/Tesseract-war/api/request/status/{orgId}?startDate={start_date_str}&endDate={end_date_str}&filterByState={state}"

    print(f"Checking files from [ {orgId} ] with state [ {state} ]")
    print(f"Dates interval: [ {start_date} ] through [ {end_date} ]")
    print(f"Page size: {page_size}")

    while not done:
        print(f"Page Number: {page_number}")
        updatedUrl = f"{url}&pageNumber={page_number}&pageSize={page_size}"
        response = fetch_requests(updatedUrl)

        print(f"Found {len(response)} requests")

        if not response or len(response) < page_size:
            print("We'll process what have was already saved and quit")
            done = True

        for request in response:
            existing_request = [
                r
                for r in request_list
                # if request is an orderdet
                if (
                    request.get("requestStatusParent") is not None
                    # and the request has a parent already in request_list
                    and [
                        parent
                        for parent in request["requestStatusParent"]
                        if parent["parentId"] == r["id"]
                    ]
                )
                # or if the request itself was already saved (duplicate)
                or r["id"] == request["id"]
            ]
            if not existing_request:
                print(f'Saving {request["id"]}')
                request_list.append(request)

        full = len(request_list) == max_requests or done
        print("Requests list is full" if full else "")

        if not full:
            print("Searching for more requests")
            page_number += 1
            continue

        print(f"Processing {len(request_list)} requests")

        with ThreadPoolExecutor(thread_count) as pool:
            for thread_number in range(1, thread_count + 1):
                pool.submit(process_requests, env, thread_number, request_list)
        pool.shutdown(wait=True)

        request_list = []
        print("Cleared request list")
        page_number += 1

    if len(FAILED_REQUESTS) > 0:
        save_json_to_file(json.dumps(FAILED_REQUESTS), "FAILED_RETRIED_REQUESTS")
    if len(DETAILED_REQUESTS) > 0:
        save_json_to_file(json.dumps(DETAILED_REQUESTS), "SUCCEEDED_RETRIED_REQUESTS")

    print("Quitting program")
