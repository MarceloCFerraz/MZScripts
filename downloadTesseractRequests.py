import json
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import cpu_count

import requests

from utils import files, utils
from utils.files import save_json_to_file

thread_count = cpu_count()
FAILED_REQUESTS = []
DETAILED_REQUESTS = []


def load_request_ids():
    print(
        ">> Please, type the request ids to search one per time.\n"
        + ">> At least one key is needed.\n"
        + ">> No duplicates will be allowed.\n"
        + ">> Leave blank and hit Enter once you're done.\n"
    )
    keys = set()

    while True:
        key = input(">> ")

        if key != "":
            keys.add(key)
        elif len(keys) > 0:
            break  # if key is an empty string and user already saved other keys, means he wants to continue

    return list(keys)


def get_request_details(env: str, requestId: str):
    print("Fetching request details")
    url = f"http://tesseract.{utils.convert_env(env)}.milezero.com/Tesseract-war/api/request/detail/{requestId}"

    response = requests.get(url=url)

    return response.json() if response.status_code < 400 else None


def get_request_file(env: str, requestId: str):
    print("Fetching request file details")
    url = f"http://tesseract.{utils.convert_env(env)}.milezero.com/Tesseract-war/api/request/file/{requestId}"

    response = requests.get(url=url)

    return response.json() if response.status_code < 400 else None


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


def save_detailed_request(req, requestId):
    print(f"{requestId} was completed successfully. Saving its data")

    name = req["fileName"]
    content = req["parsedFileContents"]

    inner_body = dict(file=name, contents=content, status="COMPLETED")

    response = {requestId: inner_body}

    DETAILED_REQUESTS.append(response)


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
        requestId = request_list[i]

        request_file = get_request_file(env, requestId)

        if request_file is None or request_file.get("fileName") is None:
            # print("Request file is not valid")
            request_detail = get_request_details(env, requestId)

            if (
                request_detail is not None
                and request_detail.get("requestStatus") is not None
            ):
                print(
                    f'{requestId} status: {request_detail["requestStatus"]["currentProcessState"]}'
                )

                save_failed_request(request_detail)
        else:
            print(f'File found: {request_file["fileName"]}')
            save_detailed_request(request_file, requestId)


if __name__ == "__main__":
    request_list = []

    env = utils.select_env()
    orgId = utils.select_org(env)

    fileName = (
        input(
            "Type in the file name with the request ids (without the `.txt` extension): "
        )
        .strip()
        .replace(".txt", "")
        .replace("./", "")
        .replace(".\\", "")
    )

    request_list = files.get_data_from_file(fileName)
    print(request_list)

    if not request_list:
        request_list = load_request_ids()

    print(f"Fetching [ {len(request_list)} ] requests from [ {orgId} ]")

    with ThreadPoolExecutor(thread_count) as pool:
        for thread_number in range(1, thread_count + 1):
            pool.submit(process_requests, env, thread_number, request_list)
    pool.shutdown(True)

    if len(FAILED_REQUESTS) > 0:
        save_json_to_file(json.dumps(FAILED_REQUESTS), "FAILED_RETRIED_REQUESTS")
    if len(DETAILED_REQUESTS) > 0:
        save_json_to_file(json.dumps(DETAILED_REQUESTS), "SUCCEEDED_RETRIED_REQUESTS")

    print("Quitting program")
