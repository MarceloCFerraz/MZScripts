# https://stackoverflow.com/questions/21252460/python-how-to-check-if-program-gets-aborted-by-user-while-running
from time import sleep
from datetime import datetime
import requests, signal, sys

API = "http://alamo.prod.milezero.com/alamo-war/api/"
GET_QUEUES = f"{API}queues/3c897e84-3957-4958-b54d-d02c01b14f15/overviews"
QUEUES_CLEARED = []


def getQueues():
    return requests.get(url=GET_QUEUES, timeout=5).json()["overviews"]


def dequeue(hubName):
    dequeue = f"{API}queues/3c897e84-3957-4958-b54d-d02c01b14f15/dequeue?key={hubName}&keyType=HUB_NAME&DequeueMode=DEFAULT"
    print(f">> Clearing {hubName} ({datetime.now()})")

    return requests.post(url=dequeue, timeout=5)


def getSingleQueue(hubName):
    get_single_queue = f"{API}queue/overview?key={hubName}&keyType=HUB_NAME"

    return requests.get(url=get_single_queue, timeout=5).json()


def exit(signum, frame):
    print(f"The script cleared {len(QUEUES_CLEARED)} queues")
    print(f"Cleared Queues: \n"+
          ", ".join(QUEUES_CLEARED))
    
    print("Aborting script...")
    sys.exit()


def main():
    print("=========== CTRL + C to stop script ===========")

    while True:
        print(f"Getting Queues ({datetime.now()})")
        queues = getQueues()
        for queue in queues:
            hubName = queue["hubName"]
            queueName = queue["queueName"]
            state = queue["lock"]["state"]

            print(f"Queue {queueName} for {hubName} is {state}")

            if state == "LOCKED":
                pending = queue["pending"]
                planning = queue["planning"]
                failed = queue["failed"]
                sum = pending + planning + failed

                print(f">> Pending: {pending}\n"+
                      f">> Planning: {planning}\n"+
                      f">> Failed: {failed}\n")
                
                if sum == 0:
                    print(">> Ignored")
                else:
                    result = dequeue(hubName=hubName)
                    QUEUES_CLEARED.append(hubName)
                    print(f">> {result}")

        print("\nWaiting 1 minute before re-searching...\n")
        sleep(60)

signal.signal(signal.SIGINT, exit)
main()