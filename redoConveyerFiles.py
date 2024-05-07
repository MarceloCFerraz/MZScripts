import logging
from datetime import datetime
from time import sleep

import pytz
import requests


def utc_to_tz(timezone="America/New_York"):
    tzInfo = pytz.timezone(timezone)
    return datetime.now(tz=tzInfo)


def getCpt(orgId, hubName):
    cptResponse = requests.get(
        url="http://sortationservices.prod.milezero.com/SortationServices-war/api/wave/cpt/{}/{}".format(
            orgId, hubName
        )
    )
    return cptResponse.json()["cpt"]


def getDateInFormat(dt, format):
    return dt.strftime(format)


# if timeout happens, retry 3 times after 200ms sleep
def getData(orgId, startDate, hubName):
    tries = 3
    for i in range(tries):
        try:
            logging.info("Search Parameters %s, %s, %s", orgId, hubName, startDate)
            response = requests.get(
                "http://reportsgen.prod.milezero.com/ReportsGen-war/api/reports/{}/conveyer/generate?useLive={}&startDate={}&node={}".format(
                    orgId, "true", startDate, hubName
                )
            )
            return response.json()["lines"]
        except Exception as e:
            if i < tries - 1:
                sleep(2)
                logging.error("Retrying for hub %s", hubName)
                logging.error("Error: %s", e)
                continue
            else:
                logging.exception("Exception occurred")


def filter_duplicate_entries(lines: list):
    unique_entries = set()

    for line in lines:
        entry = line.split()[0]
        unique_entries.add(entry)

    return list(unique_entries)


def utc_to_time(native, timezone="America/New_York"):
    return native.replace(tzinfo=pytz.utc).astimezone(pytz.timezone(timezone))


def getConveyerData(orgId, hubsList, fileNamePrefix):
    day = "05032024"

    # File is ftpied 6 times:
    #     15:45, 17:45, 18:45, 19:45, 20:45, 21:45 ET
    # Chris wants copies of the files from 16:45 - 19:45 EDT (15 - 18:45 EST and 17 - 20:45 BRST)
    times = ["175920", "184511", "194526"]
    # https://build.dev.milezero.com/job/ConveyerReport/6738/console
    # https://build.dev.milezero.com/job/ConveyerReport/6739/console
    # https://build.dev.milezero.com/job/ConveyerReport/6740/console
    for time in times:
        dt = utc_to_time(datetime.strptime(day + time + "UTC", "%m%d%Y%H%M%S%Z"))
        # dt = utc_to_time(datetime.now(timezone("UTC")))
        # for dt in dates:
        dFormatFileName = "%m%d%Y_%H%M%S"
        fileName = fileNamePrefix + str(getDateInFormat(dt, dFormatFileName)) + ".txt"
        conveyerFile = open(fileName, "w")
        logging.info(fileName)
        slackMsg = ""
        startDate = ""
        for hubName in hubsList:
            startDate = getCpt(orgId, hubName)
            lines = getData(orgId, startDate, hubName)
            if lines is not None:
                filtered_lines = filter_duplicate_entries(lines)
                slackMsg += (
                    "Hub:" + hubName + ", orders " + str(len(filtered_lines)) + "\n"
                )
                for line in filtered_lines:
                    # print(line)
                    conveyerFile.write(line)
                    conveyerFile.write("\n")
        conveyerFile.close()
        logging.info("Ftpying %s", fileName)
        logging.info(slackMsg)


namesList = [
    "FLRB_",
    "FLRB1_",
    "FLRB2_",
    "FLRB3_",
    "FLRB4_",
    "FLRB5_",
    "FLRB6_",
    "FLRB7_",
    "FLRB8_",
    "FLRB9_",
    "FLRB10_",
]
fileNamesDict = {
    "FLRB_": ["8974", "3748", "8026", "8743", "8232"],
    "FLRB1_": ["8286", "8027", "8069", "3913"],
    "FLRB2_": ["8246", "8801", "8500"],
    "FLRB3_": ["3772", "8005", "8613"],
    "FLRB4_": ["8221", "8971", "8028"],
    "FLRB5_": ["8101", "8228", "8857", "8488", "8087"],
    "FLRB6_": ["8077", "8033", "8103", "3905"],
    "FLRB7_": ["8281", "3880", "8109"],
    "FLRB8_": ["8744", "8102", "8220", "8673"],
    "FLRB9_": ["8764", "8006", "8740", "3920"],
    "FLRB10_": ["8883", "8081", "8506", "3909"],
}

orgId = "3c897e84-3957-4958-b54d-d02c01b14f15"


logging.basicConfig(
    format="%(asctime)s - %(message)s", level=logging.DEBUG, datefmt="%Y-%m-%d %H:%M:%S"
)

for fileName in namesList:
    getConveyerData(orgId, fileNamesDict[fileName], fileName)
