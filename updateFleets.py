from ast import literal_eval

import requests
from utils import utils, associates, fleets
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


def main():
    envFromData = pandas.read_csv("Fleets Data.csv")["ENV"].values[0]
    fileName = "Fleet Analysis.xlsx"
    orgs = utils.ORGS[envFromData]
    
    allAssociates = []
    allFleets = []
    
    print("Getting Data for all ORGs... ", end="")
    
    for org in orgs.keys():
        allAssociates.extend(
            # searching for 'ACTIVE' associates for each org
            associates.search_associate(envFromData, orgs[org], 6, "ACTIVE")
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
            # loading data from dataframe row where FleetID == fleetIDs
            row_data = dataFrame[dataFrame['FleetID'] == fleetsIDs]

            print("Loading Hubs Data from File... ", end="")
            try:
                # to understand this try/except, see comments above
                hubs_data = row_data['HubsIDs'].iloc[0]
                hubs_data = str(
                    hubs_data.replace(", ", "\n")
                ).splitlines() if pandas.notna(hubs_data) else []

                print("Done")
            except Exception:
                print("Fail")
                print("Loading Description Data from File... ", end="")

                description_data = [row_data['Description'].iloc[0]]

                print("Done")

            fleetsIDs = str(fleetsIDs).replace(", ", "\n").splitlines()

            fleetAssociates = {}
            biggestFleet = ""
            biggestFleetCount = 1

            # filling dict with "fleetID": [List of associates with this fleetID]
            print(">> Putting Associates into each Fleet... ", end="")

            for fleetID in fleetsIDs:
                idsList = []
                
                for associate in allAssociates:
                    try:
                        if associate["fleetId"] == fleetID:
                            idsList.append(associate["associateId"])
                    except Exception:
                        pass

                fleetAssociates[fleetID] = idsList


                
                if len(fleetAssociates[fleetID]) > biggestFleetCount:
                    biggestFleet = fleetID
                    biggestFleetCount = len(fleetAssociates[fleetID])
            
            print("Done")
            print(f">> The fleet with most associates is {biggestFleet} with {biggestFleetCount}")

            for fleetID in fleetAssociates.keys():
                associatesList = fleetAssociates[fleetID]
                if len(associatesList) > biggestFleetCount:
                    biggestFleet = fleetID
                    biggestFleetCount = len(associatesList)

            if biggestFleet == "" and len(fleetAssociates.keys()) > 1:
                biggestFleet = iter(next(fleetAssociates))

            for fleetID in fleetAssociates.keys():
                if fleetID != biggestFleet:
                    haveFailed = False

                    for associate in fleetAssociates[fleetID]:
                        fId = associate["fleetId"]

                        if fId == fleetID:
                            print(f">>> {associate['associateId']} already has {fleetID}")
                        else:
                            print(f">>> Updating {associate} with {fleetID}")
                            response = associates.update_associate_data(envFromData, associate)
                            
                            print(f">>> Result: {response.status_code}")

                            if response.status_code >= 400:
                                haveFailed = True
                    
                    if not haveFailed:
                        print(f">> Deleting {fleetID}")

                        response = fleets.delete_fleet(
                            envFromData, 
                            fleets.search_fleet(
                                envFromData, 
                                [fleet for fleet in allFleets if fleet["fleetId"] == fleetID][0]["orgId"], 
                                fleetID
                            ),
                            fleetID
                        )

                        print(f">> Result: {response.status_code}")


main()
