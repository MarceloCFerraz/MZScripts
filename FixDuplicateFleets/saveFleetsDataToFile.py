import sys
import os
from datetime import datetime

import xlsxwriter
import pandas

from utils import utils, fleets, associates, hubs, files



XLSX_FILE = "Fleets Data.xlsx"
CSV_FILE = XLSX_FILE.replace("xlsx", "csv")


def fill_file_with_data(logFile):
    data = {}  # object which will be used to store the complete data and save it to CSV
    # Pandas could also be used to replace XlsxWriter to generate the Excel File but we'd probably lose formatting

    HEADERS = [
        "ORG", 
        "ENV", 
        "FleetID", 
        "State", 
        "Name", 
        "Description", 
        "ParentFleet", 
        "ParentFleets", 
        "CreationDate", 
        "LastUpdated", 
        "HubsNames", 
        "HubsIDs", 
        "AssociatesNames",
        "AssociatesIDs"
    ]

    for header in HEADERS:
        data[header] = []  
        # creating keys for each element in HEADERS. They will be the headers in the CSV file
    
    workbook = xlsxwriter.Workbook(f"{XLSX_FILE}")
    worksheet = workbook.add_worksheet("All Data")


    BOLD = workbook.add_format({"bold": True, "align": "center", "valign": "vcenter"})
    DATE_FORMAT = workbook.add_format({"num_format": "mmmm d yyyy", "align": "center", "valign": "vcenter"})
    CONSOLAS_FONT = workbook.add_format({"font_name": "Consolas", "align": "center", "valign": "vcenter"})
    WRAP_TEXT = workbook.add_format({"text_wrap": True, "font_name": "Consolas", "align": "center", "valign": "vcenter"})
    SIMPLE_ALIGN = workbook.add_format({"align": "center", "valign": "vcenter"})

    for col in range(0, len(HEADERS)):
        worksheet.write(0, col, HEADERS[col].upper(), BOLD)

    files.stop_logging()
    env = utils.select_env()
    files.start_logging(logFile)

    row = 1  # first line is 0 and it already contains the headers
    col = 0
    for orgName in utils.ORGS[env.upper()].keys():
        print(f"\nGetting data for {orgName}")

        orgId = utils.ORGS[env.upper()][orgName]


        # getting all active org associates (sorted by id)
        orgAssociates = sorted(
            associates.search_associate(env, orgId, 0, orgId),
            key= lambda ass: ass["associateId"] 
        )
        
        print(f"> {len(orgAssociates)} active associates found for {orgName}")

        # getting all fleets for org
        orgFleets = fleets.search_fleet(env, orgId)
        print(f"> {len(orgFleets)} fleets found for {orgName}")

        # getting all hubs for org (avoids extra api calls)
        orgHubs = hubs.search_hubs(env, orgId)
        print(f"> {len(orgHubs)} hubs found for {orgName}")
        
        for fleet in orgFleets:
            data["ORG"].append(orgName)
            data["ENV"].append(env)

            fleetId = get_attribute(fleet, "fleetId")
            data["FleetID"].append(fleetId)

            # print(fleet)
            print(f">> Getting data for fleet {fleetId}... ", end="")

            fleetName = get_attribute(fleet, "fleetName")
            data["Name"].append(fleetName)

            state = "ACTIVE" if get_attribute(fleet, "active") == True else "INACTIVE"
            data["State"].append(state)
            
            description = get_attribute(fleet, "description")
            data["Description"].append(description)

            parentFleetId = get_attribute(fleet, "parentFleetId")
            data["ParentFleet"].append(parentFleetId)
            
            parentFleets = "\n".join(get_attribute(get_attribute(fleet, "parentFleets"), "fleetIds"))
            data["ParentFleets"].append(repr(parentFleets))

            try:
                creationDate = datetime.strptime(get_attribute(fleet, "creationDate"), "%Y-%m-%dT%H:%M:%S.%fZ")
                lastUpdatedDate = datetime.strptime(get_attribute(fleet, "lastUpdatedDate"), "%Y-%m-%dT%H:%M:%S.%fZ")
            except Exception:
                creationDate = datetime.strptime(get_attribute(fleet, "creationDate"), "%Y-%m-%dT%H:%M:%SZ")
                lastUpdatedDate = datetime.strptime(get_attribute(fleet, "lastUpdatedDate"), "%Y-%m-%dT%H:%M:%SZ")
            
            data["CreationDate"].append(creationDate)
            data["LastUpdated"].append(lastUpdatedDate)

            hubIds = get_attribute(fleet, "hubIds")
            fleetHubsNames = ""
            fleetHubsIds = ""

            if hubIds != "":
                idsList = []
                for hubId in hubIds:
                    idsList.append(hubId)

                idsList.sort()
                for hubId in idsList:
                    hub = [h for h in orgHubs if h["id"] == hubId]
                    if hub != []:
                        fleetHubsNames += f"{hub[0]['name']}\n" 
                        fleetHubsIds += f"{hub[0]['id']}\n"
            
            data["HubsNames"].append(repr(fleetHubsNames))
            data["HubsIDs"].append(repr(fleetHubsIds))
            
            fleetAssociatesNames = ""
            fleetAssociatesIds = ""
            for associate in orgAssociates:
                associateId = get_attribute(associate, "associateId")
                associateName = get_attribute(get_attribute(associate, "contact"), "name")
                associateFleet = get_attribute(associate, "fleetId")

                if fleetId == associateFleet:
                    fleetAssociatesNames += f"{associateName}\n"
                    fleetAssociatesIds += f"{associateId}\n"

            data["AssociatesNames"].append(repr(fleetAssociatesNames))
            data["AssociatesIDs"].append(repr(fleetAssociatesIds))

            # saving content so far into the .xlsx file
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

            print("Done")
            # Org | Env | Fleet Id | State | Name | Description | Parent Fleet | Parent Fleets | Creation Date | Last updated | Hubs | Active Associates

    # creating a Pandas DataFrame object which can be used to query data and will be used to save it to a file
    dataFrame = pandas.DataFrame(data=data)
    # saving all data into the .csv file
    dataFrame.to_csv(CSV_FILE, sep=",", index=False)
    ## saving all data into a test .xlsx file to check what it would look like to replace XlsxWriter with Pandas
    # dataFrame.to_excel(
    #     XLSX_FILE.replace(".xlsx", " - PD.xlsx"), 
    #     sheet_name="All Data", 
    #     index=False, 
    #     engine="xlsxwriter"
    # )

    # formatting individual column widths
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


def get_attribute(dict, key):
    response = ""

    try:
        response = dict[key]
    except Exception:
        # print(f"{key} not present in object")
        pass

    return response


def main():
    print("Running script...",)
    logFile = files.create_logs_file()
    files.start_logging(logFile)
    
    fill_file_with_data(logFile)
    
    files.stop_logging()
    files.close_logs_file(logFile)

    print("Done!")
    print("Check out the logs to see the full results")


main()
