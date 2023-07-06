from utils import utils, fleets, associates, hubs
from datetime import datetime
import xlsxwriter


def getAttribute(dict, key):
    response = ""

    try:
        response = dict[key]
    except Exception:
        # print(f"{key} not present in object")
        pass

    return response


workbook = xlsxwriter.Workbook(f"Fleet Analysis.xlsx")
worksheet = workbook.add_worksheet("Fleets Data")

HEADERS = ["ORG", "ENV", "Fleet ID", "State", "Name", "Description", "Parent Fleet", "Parent Fleets", "Creation Date", "Last updated", "Hubs", "Active Associates"]

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
        fleetId = getAttribute(fleet, "fleetId")

        # print(fleet)
        print(f">> Getting data for fleet {fleetId}")

        fleetName = getAttribute(fleet, "fleetName")
        state = "ACTIVE" if getAttribute(fleet, "active") == True else "INACTIVE"
        description = getAttribute(fleet, "description")
        parentFleetId = getAttribute(fleet, "parentFleetId")
        parentFleets = "\n".join(getAttribute(getAttribute(fleet, "parentFleets"), "fleetIds"))
        try:
            creationDate = datetime.strptime(getAttribute(fleet, "creationDate"), "%Y-%m-%dT%H:%M:%S.%fZ")
            lastUpdatedDate = datetime.strptime(getAttribute(fleet, "lastUpdatedDate"), "%Y-%m-%dT%H:%M:%S.%fZ")
        except Exception:
            creationDate = datetime.strptime(getAttribute(fleet, "creationDate"), "%Y-%m-%dT%H:%M:%SZ")
            lastUpdatedDate = datetime.strptime(getAttribute(fleet, "lastUpdatedDate"), "%Y-%m-%dT%H:%M:%SZ")

        hubIds = getAttribute(fleet, "hubIds")
        fleetHubs = ""

        if hubIds != "":
            for hubId in hubIds:
                hub = [h for h in orgHubs if h["id"] == hubId]
                if hub != []:
                    fleetHubs += f"{hub[0]['name']} ({hub[0]['id']})\n"
        
        fleetAssociates = ""
        for associate in orgAssociates:
            associateFleet = getAttribute(associate, "fleetId")

            if fleetId == associateFleet:
                fleetAssociates += f"{associate['associateId']}\n"

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
        worksheet.write(row, col + 10, fleetHubs, WRAP_TEXT)
        worksheet.write(row, col + 11, fleetAssociates, WRAP_TEXT)
        row += 1
        print(f">> {fleetId} DONE")
        # Org | Env | Fleet Id | State | Name | Description | Parent Fleet | Parent Fleets | Creation Date | Last updated | Hubs | Active Associates

worksheet.set_column(0, 0, 12)
worksheet.set_column(1, 1, 8)
worksheet.set_column(2, 2, 41)
worksheet.set_column(3, 3, 10)
worksheet.set_column(4, 4, 40)
worksheet.set_column(5, 5, 40)
worksheet.set_column(6, 7, 41)
worksheet.set_column(8, 9, 18)
worksheet.set_column(10, 10, 55)
worksheet.set_column(11, 11, 41)
workbook.close()
