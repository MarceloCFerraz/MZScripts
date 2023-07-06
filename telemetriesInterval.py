# https://stackoverflow.com/questions/127803/how-do-i-parse-an-iso-8601-formatted-date
# https://stackoverflow.com/questions/1345827/how-do-i-find-the-time-difference-between-two-datetime-objects-in-python
import sys
import requests
from datetime import datetime, timezone
from dateutil import parser

API = "http://lmx.prod.milezero.com/lmx-war/api/"
ORGS = {
    "STAPLES": {
        "PROD": "3c897e84-3957-4958-b54d-d02c01b14f15" 
    }
}


def getTelemetries(associateId, startTime, endTime):
    endpoint = f"{API}lmxtelemetry/org/{ORGS['STAPLES']['PROD']}/owner/{associateId}?startTime={str(startTime).replace(':', '%3A')}&endTime={str(endTime).replace(':', '%3A')}"

    print(f"\n{startTime} to {endTime}")
    print(f"Retrieving Telemetries for {associateId}")

    return requests.get(url=endpoint, timeout=10).json()["events"]
    


def main(associateId, startTime, endTime):
    telemetries = getTelemetries(associateId=associateId, startTime=startTime, endTime=endTime)

    print("> Telemetries gathered")
    print("\n> Searching...")

    count = 0

    previous_stamp = parser.isoparse( # python 3.6
        str(telemetries[0]["timestamp"])
    )

    for telemetry in telemetries:
        timestamp = parser.isoparse( # python 3.6
            str(telemetry["timestamp"])
        )

        dif = timestamp - previous_stamp
        total_seconds = dif.total_seconds()

        if total_seconds > 300: # get only stamps with difference greater than 5 minutes
            count += 1
            print(f">> {previous_stamp.date()} {previous_stamp.time()} - {timestamp.date()} {timestamp.time()} ({dif})")
        
        previous_stamp = timestamp
    if count == 0:
        print("\nNo difference greater than 5 minutes was found in the reported interval!")


associateId = input("insert associateId: ")
startTime = str(input("insert startTime (zulu format -> yyyy-mm-ddTHH:mm:ssZ): "))
endTime = str(input("insert endTime (zulu format -> yyyy-mm-ddTHH:mm:ssZ): "))
main(associateId, startTime, endTime)