from ast import literal_eval

import requests
from utils import utils, associates, fleets, files
import pandas

# Specify the names of the sheets you want to load
sheet_names = ['Sheet1', 'Sheet2']

def load_dataframe_from_sheets(fileName, sheets):
    # Create an empty dictionary to store the DataFrames
    dfs = {}

    # Load each sheet and append the DataFrame to the list
    for sheet in sheets:
        df = pandas.read_excel(fileName, sheet_name=sheet)
        dfs[sheet] = df

    return dfs


def update_fleets():
    envFromData = pandas.read_csv("Fleets Data.csv")["ENV"].values[0]
    fileName = "Fleet Analysis.xlsx"
    orgs = utils.ORGS[envFromData]
    
    allAssociates = []
    allFleets = []
    
    print("Getting Data for all ORGs... ", end="")
    
    for org in orgs.keys():
        allAssociates.extend(
            # searching for associates for each org
            associates.search_associate(envFromData, orgs[org], 0, orgs[org])
        )
        allFleets.extend(
            # searching fo all fleets for each org
            fleets.search_fleet(envFromData, orgs[org])
        )
    
    print("Done")

    print(f"Loaded {len(allAssociates)} associates and {len(allFleets)} fleets")

    print(f"Loading data from '{fileName}'... ", end="")

    dataFrames = load_dataframe_from_sheets(fileName, ["Same Hubs", "Same Description"])
    # dict containing all sheets passed to load_dataframe_from_sheets via parameters
    print("Done")
    
    for sheet in dataFrames.keys():
        print(f"\n>> {sheet}")

        dataFrame = pandas.DataFrame(dataFrames[sheet])

        fleetIDSeries = dataFrame["FleetID"]
        # Same hubs has a column for hubs which same description doesn't have
        # Same description has a column for description which same hubs doesn't have

        for fleetsIDs in fleetIDSeries:
            fleetsIDs = str(fleetsIDs).replace(", ", "\n").splitlines()

            fleetAssociates = {}
            biggestFleet = ""
            biggestFleetCount = 1

            # filling dict with "fleetID": [List of associates with this fleetID]
            print(">> Putting Associates into each Fleet (equal fleets will be ignored)...")

            for fleetID in fleetsIDs:
                fleet = [f for f in allFleets if f["fleetId"] == fleetID]

                associatesList = []
                
                for associate in allAssociates:
                    try:
                        if associate["fleetId"] == fleetID:
                            associatesList.append(associate)
                    except Exception:
                        pass

                fleetAssociates[fleetID] = associatesList
                
                print(f">>>> {fleetID} has {len(associatesList)} associates")
                
                if len(associatesList) > biggestFleetCount and len(fleet) >= 1: 
                    if fleet[0]["active"]:
                        biggestFleet = fleetID
                        biggestFleetCount = len(associatesList)
                    else:
                        print(f">> {fleetID} not found!")


            if biggestFleet == "" and len(fleetAssociates.keys()) > 1:
                for fleetID in fleetAssociates.keys():
                    if biggestFleet == "":
                        fleet = [f for f in allFleets if f["fleetId"] == fleetID]

                        if len(fleet) >= 1:
                            if fleet[0]["active"]:
                                biggestFleet = fleetID



            print(f">>>> Biggest Fleet: '{biggestFleet}' {'will be ignored' if biggestFleet == '' else 'starting update'}")

            for fleetID in fleetAssociates.keys():
                haveFailed = False

                if fleetID != biggestFleet and biggestFleet != "":
                    for associate in fleetAssociates[fleetID]:
                        print(f">>> Updating {associate['associateId']} with {biggestFleet}")

                        associate["fleetId"] = biggestFleet
                        response = associates.update_associate_data(envFromData, associate)

                        print(f">>> Result: {response.status_code}")

                        if response.status_code >= 400:
                            haveFailed = True
                            print(response.text)

                    fleetIDList = [fleet for fleet in allFleets if fleet["fleetId"] == fleetID]
                    # some fleets have duplicate ids, this list will be used to avoid deleting those duplicates
                    # those duplicates fleetIDs are from different orgs anyways

                    if not haveFailed and len(fleetIDList) == 1:
                        print(f">> Deleting {fleetID}")

                        response = fleets.delete_fleet(
                            envFromData, 
                            fleetIDList[0]["orgId"],
                            fleetID
                        )

                        print(f">> Result: {response.status_code}\n")
                        if response.status_code > 400:
                            print(response.text)
                    else:
                        print(f">> {fleetID} won't be deleted! \nFailed? {haveFailed} \nFleets with This ID: {len(fleetIDList)}\n")


def main():
    print("Running script...",)
    logFile = files.create_logs_file()
    files.start_logging(logFile)
    
    update_fleets()
    
    files.stop_logging()
    files.close_logs_file(logFile)

    print("Done!")
    print("Check out the logs to see the full results")


main()
