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

    # Concatenate the DataFrames into a single DataFrame, aligning columns
    combined_df = pandas.concat(dfs.values(), ignore_index=False)

    return combined_df


def main():
    envFromData = pandas.read_csv("Fleets Data.csv")["ENV"].values[0]
    
    orgs = utils.ORGS[envFromData]

    allAssociates = []
    allFleets = []
    
    print("Getting Data for all ORGs")
    for org in orgs.keys():
        allAssociates.extend(
            # searching for 'ACTIVE' associates for each org
            associates.search_associate(envFromData, orgs[org], 6, "ACTIVE")
        )
        allFleets.extend(
            fleets.search_fleet(envFromData, orgs[org])
        )

    fileName = "Fleet Analysis.xlsx"
    print(f"Loading data from '{fileName}'")

    dataFrame = load_dataframe_from_sheets(fileName, ["Same Hubs", "Same Description"])
    # list(assoc for assoc in dataFrame["AssociatesIDs"] if pandas.notna(assoc))


main()

# are fleets from the same org?
# what fleet has less associates?
# update associate with bigger fleet
# delete old fleet