import datetime
import json
import time
from concurrent.futures import ThreadPoolExecutor

import requests

from utils import utils
from utils.files import save_json_to_file

# from multiprocessing import cpu_count


# thread_count = cpu_count()
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
    print("Saved failed data")


def get_request_file(env: str, requestId: str):
    url = f"http://tesseract.{utils.convert_env(env)}.milezero.com/Tesseract-war/api/request/file/{requestId}"

    return requests.get(url=url).json()


def save_completed_request(req, requestId):
    print(f"{requestId} was completed successfully. Saving its data")

    name = req["fileName"]
    content = req["parsedFileContents"]

    inner_body = dict(file=name, contents=content, status="COMPLETED")

    response = {requestId: inner_body}

    print(response)
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
        # retry(env, requestId)
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
    # START DELETING FROM HERE
    # let`s call the number of requests per thread `rt`
    # the thread identifier number will be called `tn`,
    # the lower limit of the interval will be called `ll`
    # and the higher limit `hl`
    # -> rt = requests len / thread count
    # -> hl = rt * tn
    # -> ll = hl - rt
    # if hl is higher than rt, also need to convert to a positive number
    # Example:
    # assuming there are 5 threads (i know this is impossible), each identified by a number (1 - 5),
    # and the requests len is 250, same as the max (5 threads * 50 reqs per page)
    # -> rt = 250 / 5 = 50
    # -> hl = 50 * tn
    # -> ll = hl - rt
    # thread 1 =>   0 - 50      -> hl = 50 * 1 = 50     -> ll =  50 - 50 = 0
    # thread 2 =>  50 - 100     -> hl = 50 * 2 = 100    -> ll = 100 - 50 = 50
    # thread 3 => 100 - 150     -> hl = 50 * 3 = 150    -> ll = 150 - 50 = 100
    # thread 4 => 150 - 200     -> hl = 50 * 4 = 200    -> ll = 200 - 50 = 150
    # thread 5 => 200 - 250     -> hl = 50 * 5 = 250    -> ll = 250 - 50 = 200
    # if we're dealing with a number of requests that's less than the maximum allowed,
    # the logic above won't work 100%. that's because rt won't be an integer, so the high and
    # low level calculations won't work as expected.
    # Example: requests = 172; Max = 250; threads = 5
    # -> rt = 172 / 5 = 34,4
    # -> hl = 34,4 * tn (result will be int)
    # -> ll = hl - rt (result will be int)
    # thread 1 =>   0 - 34      -> hl = 34,4 * 1 = 34,4  = 34 (int)   -> ll =  34 - 34,4 = -0,4  = 0 (int)
    # thread 2 =>  33 - 68      -> hl = 34,4 * 2 = 68,8  = 68 (int)   -> ll =  68 - 34,4 = 33,6  = 33 (int)
    # thread 3 =>  68 - 103     -> hl = 34,4 * 3 = 103,2 = 103 (int)  -> ll = 103 - 34,4 = 68,6  = 68 (int)
    # thread 4 => 102 - 137     -> hl = 34,4 * 4 = 137,6 = 137 (int)  -> ll = 137 - 34,4 = 102,6 = 102 (int)
    # thread 5 => 137 - 172     -> hl = 34,4 * 5         = 172 (int)  -> ll = 172 - 34,4 = 137,6 = 137 (int)
    # as we can see, thread 2 overlaps the last element of thread 1 and the same occurs for 4 and 3
    # the good thing is we can easily identify when that's occurring:
    # -> when tn is even and when requests len > max len
    # so we could easily overcome this by treating this edge case with an if statement,
    # STOP DELETING HERE
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
    # global done, full, request_list, thread_count, page_size, page_number, threads_done
    # print(f"Thread {thread_number} is fetching request ids")

    response = requests.get(url=url, timeout=300).json()

    try:
        err = response.get("message")

        if err is not None:
            print(f"An error occurred: {err}")
            # print(f"An error occurred in thread {thread_number}: {err}")
            return []
            # done = True  # this can probably stop other threads
    except AttributeError:
        # if there is an error accessing "message", it's because the object is an array, so nothing to worry about
        pass

    return response

    # if response != []:
    #     for request in response:
    #         existing_request = [
    #             r
    #             for r in request_list
    #             if r["id"] != request["requestStatusParent"]["parentId"]
    #         ]
    #         if existing_request == []:
    #             # Orderdet files reference their parent orders file in requestStatusParen.parentId and parentName properties
    #             # This if is only checking if the parent is already in the set of requests.
    #             # If it is, (maybe) there'se no need to add this one too as it would only generate duplicate data for us to review
    #             request_list.append(request)

    #     # threads should not process everything at once. The idea is, fetch some data until a certain limit, process it and then fetch more data
    #     # For example, if pagenumber is 50 and we have 5 cores, the max number of requests is 250.
    #     # When 250 are reached, pause and process them before continuing
    #     full = len(request_list) == max_requests
    # else:
    #     print("No requests found, we're done here")
    #     done = True
    #     full = True

    # # if full and len(request_list) > 0:
    # # process_requests(env, thread_number)

    # # while len(threads_done) < thread_count:
    # #     # make all threads wait until all threads have processed their stuff before continuing
    # #     time.sleep(0.1)
    # # full = False
    # # threads_done = []
    # # request_list = []


if __name__ == "__main__":
    thread_count = 8
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
                # Orderdet files reference their parent orders file in requestStatusParen.parentId and parentName properties
                # This if statement is only checking if the parent is already in the set of requests.
                # If it is, (maybe) there'se no need to add the orderdet too as it would only generate duplicate data for us to review
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

    print(FAILED_REQUESTS)
    save_json_to_file(json.dumps(FAILED_REQUESTS), "FAILED_RETRIED_REQUESTS")
    print(DETAILED_REQUESTS)
    save_json_to_file(json.dumps(DETAILED_REQUESTS), "SUCCEEDED_RETRIED_REQUESTS")
