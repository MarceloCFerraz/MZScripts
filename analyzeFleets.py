from datetime import datetime
import os

from langchain.document_loaders import TextLoader
from langchain.llms import OpenAI
from langchain.indexes import VectorstoreIndexCreator

import xlsxwriter

from utils import aikey, utils, fleets, associates, hubs

os.environ["OPENAI_API_KEY"] = aikey.API_KEY
FILE_NAME = "Fleet Analysis.xlsx"
TXT_FILE = FILE_NAME.replace("xlsx", "txt")



def analyze_data():
    # LLM = OpenAI(openai_api_key="")
    LOADER = TextLoader(f"./{TXT_FILE}")
    INDEX = VectorstoreIndexCreator().from_loaders([LOADER])
    question1 = "What fleet ids have the same hubs attached to them?"
    INDEX.query(question1)

def fill_file_with_data():
    txtFile = open(TXT_FILE, "w")
    workbook = xlsxwriter.Workbook(f"{FILE_NAME}")
    worksheet = workbook.add_worksheet("Fleets Data")

    HEADERS = [
        "ORG", 
        "ENV", 
        "Fleet ID", 
        "State", 
        "Name", 
        "Description", 
        "Parent Fleet", 
        "Parent Fleets", 
        "Creation Date", 
        "Last updated", 
        "Hubs Names", 
        "Hubs Ids", 
        "Associates Names",
        "Associates Ids"
    ]
    txtFile.write(
        HEADERS[0] + "," +
        HEADERS[1] + "," +
        HEADERS[2] + "," +
        HEADERS[3] + "," +
        HEADERS[4] + "," +
        HEADERS[5] + "," +
        HEADERS[6] + "," +
        HEADERS[7] + "," +
        HEADERS[8] + "," +
        HEADERS[9] + "," +
        HEADERS[10] + "," +
        HEADERS[11] + "," +
        HEADERS[12] + "," +
        HEADERS[13] + "\n"
    )

    BOLD = workbook.add_format({"bold": True, "align": "center", "valign": "vcenter"})
    DATE_FORMAT = workbook.add_format({"num_format": "mmmm d yyyy", "align": "center", "valign": "vcenter"})
    CONSOLAS_FONT = workbook.add_format({"font_name": "Consolas", "align": "center", "valign": "vcenter"})
    WRAP_TEXT = workbook.add_format({"text_wrap": True, "font_name": "Consolas", "align": "center", "valign": "vcenter"})
    SIMPLE_ALIGN = workbook.add_format({"align": "center", "valign": "vcenter"})

    for col in range(0, len(HEADERS)):
        worksheet.write(0, col, HEADERS[col].upper(), BOLD)

    env = utils.select_env()
    row = 1  # first line is 0 and it already contains the headers
    col = 0
    for orgName in utils.ORGS[env.upper()].keys():
        print(f"\nGetting data for {orgName}")

        orgId = utils.ORGS[env.upper()][orgName]

        # getting all active org associates
        orgAssociates = associates.search_associate(env, orgId, 6, "ACTIVE")
        print(f"> {len(orgAssociates)} active associates found for {orgName}")

        # getting all fleets for org
        orgFleets = fleets.search_fleet(env, orgId)
        print(f"> {len(orgFleets)} fleets found for {orgName}")

        # getting all hubs for org (avoids extra api calls)
        orgHubs = hubs.search_hubs(env, orgId)
        print(f"> {len(orgHubs)} hubs found for {orgName}")
        
        for fleet in orgFleets:
            fleetId = get_attribute(fleet, "fleetId")

            # print(fleet)
            print(f">> Getting data for fleet {fleetId}")

            fleetName = get_attribute(fleet, "fleetName")
            state = "ACTIVE" if get_attribute(fleet, "active") == True else "INACTIVE"
            description = get_attribute(fleet, "description")
            parentFleetId = get_attribute(fleet, "parentFleetId")
            parentFleets = "\n".join(get_attribute(get_attribute(fleet, "parentFleets"), "fleetIds"))
            try:
                creationDate = datetime.strptime(get_attribute(fleet, "creationDate"), "%Y-%m-%dT%H:%M:%S.%fZ")
                lastUpdatedDate = datetime.strptime(get_attribute(fleet, "lastUpdatedDate"), "%Y-%m-%dT%H:%M:%S.%fZ")
            except Exception:
                creationDate = datetime.strptime(get_attribute(fleet, "creationDate"), "%Y-%m-%dT%H:%M:%SZ")
                lastUpdatedDate = datetime.strptime(get_attribute(fleet, "lastUpdatedDate"), "%Y-%m-%dT%H:%M:%SZ")

            hubIds = get_attribute(fleet, "hubIds")
            fleetHubsNames = ""
            fleetHubsIds = ""

            if hubIds != "":
                for hubId in hubIds:
                    hub = [h for h in orgHubs if h["id"] == hubId]
                    if hub != []:
                        fleetHubsNames += f"{hub[0]['name']}\n" 
                        fleetHubsIds += f"{hub[0]['id']}\n"
            print(repr(fleetHubsNames))
            fleetAssociatesNames = ""
            fleetAssociatesIds = ""
            for associate in orgAssociates:
                associateId = get_attribute(associate, "associateId")
                associateName = get_attribute(get_attribute(associate, "contact"), "name")
                associateFleet = get_attribute(associate, "fleetId")

                if fleetId == associateFleet:
                    fleetAssociatesNames += f"{associateName}\n"
                    fleetAssociatesIds += f"{associateId}\n"
            worksheet.write(row, col, orgName.upper(), BOLD)
            worksheet.write(row, col + 1, env.upper(), BOLD)
            worksheet.write(row, col + 2, fleetId, CONSOLAS_FONT)
            worksheet.write(row, col + 3, state, SIMPLE_ALIGN)
            worksheet.write(row, col + 4, fleetName, SIMPLE_ALIGN)
            worksheet.write(row, col + 5, description, SIMPLE_ALIGN)
            worksheet.write(row, col + 6, parentFleetId, CONSOLAS_FONT)
            worksheet.write(row, col + 7, parentFleets, CONSOLAS_FONT)
            worksheet.write_datetime(row, col + 8, creationDate, DATE_FORMAT)
            worksheet.write_datetime(row, col + 9, lastUpdatedDate, DATE_FORMAT)
            worksheet.write(row, col + 10, fleetHubsNames, SIMPLE_ALIGN)
            worksheet.write(row, col + 11, fleetHubsIds, WRAP_TEXT)
            worksheet.write(row, col + 12, fleetAssociatesNames, SIMPLE_ALIGN)
            worksheet.write(row, col + 13, fleetAssociatesIds, WRAP_TEXT)
            row += 1

            # escaping the new line to print it into txt file
            "\\n".join(parentFleets.splitlines())
            "\\n".join(fleetHubsNames.splitlines())
            "\\n".join(fleetHubsIds.splitlines())
            "\\n".join(fleetAssociatesNames.splitlines())
            "\\n".join(fleetAssociatesIds.splitlines())

            txtFile.write(
                f'{orgName.upper()},' + 
                f'{env.upper()},' +
                f'{fleetId},' +  
                f'{state},' + 
                f'{fleetName},' + 
                f'{description},' + 
                f'{parentFleetId},' + 
                f'"{parentFleets}",' + 
                f'{creationDate},' + 
                f'{lastUpdatedDate},' + 
                f'"{fleetHubsNames}",' + 
                f'"{fleetHubsIds}",' +
                f'"{fleetAssociatesNames}",' +
                f'"{fleetAssociatesIds}"\n'
            )
            print(f">> {fleetId} DONE")
            # Org | Env | Fleet Id | State | Name | Description | Parent Fleet | Parent Fleets | Creation Date | Last updated | Hubs | Active Associates

    worksheet.set_column(0, 0, 12)
    worksheet.set_column(1, 1, 8)
    worksheet.set_column(2, 2, 41)
    worksheet.set_column(3, 3, 10)
    worksheet.set_column(4, 4, 29)
    worksheet.set_column(5, 5, 40)
    worksheet.set_column(6, 7, 41)
    worksheet.set_column(8, 10, 15)
    worksheet.set_column(11, 11, 45)
    worksheet.set_column(12, 12, 30)
    worksheet.set_column(13, 13, 42)
    workbook.close()
    txtFile.close()



def get_attribute(dict, key):
    response = ""

    try:
        response = dict[key]
    except Exception:
        # print(f"{key} not present in object")
        pass

    return response


def main():
    fill_file_with_data()
    analyze_data()


main()