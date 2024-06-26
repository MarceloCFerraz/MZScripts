from ast import literal_eval

import pandas

from utils import files


def is_valid_description(row):
    # hubsNames, hubsIDs, associatesNames and associatesIDs are stored in the csv file as repr string.
    # repr strings can't have their \n chars replaced directly, the only way of doing so is below
    hubNames = str(literal_eval(row["HubsNames"]))

    for hubName in hubNames.splitlines():
        if hubName not in row["Description"]:
            # print(f"{row['Description']} doesn't contain {hubName}")
            return True
    return False


def analyze_data():
    print("Loadin data from CSV file...", end=" ")
    fleets = pandas.read_csv("Fleets Data.csv", sep=",")
    # Pandas DataFrame containing all data
    print("Done")

    analysis_file = "Fleet Analysis.xlsx"
    writer = pandas.ExcelWriter(analysis_file, engine="xlsxwriter")

    # agent = setup_agent(fleets)

    # Group the fleets based on unique combinations of 'HubIds' and 'ORG'
    sheet_name = "Same Hubs"
    print(f"Generating {sheet_name} Sheet for {analysis_file}...", end=" ")

    aggregations = {
        "ORG": list,
        # this could be the first found
        # but some different orgs have the same fleet/hub id and i wan to know
        # when that is the case
        "FleetID": list,
        "State": list,
        "AssociatesIDs": list,
    }
    fleets_with_same_hubs = fleets.groupby("HubsIDs").agg(aggregations).reset_index()
    # First group data by hub ids

    fleets_with_same_hubs = fleets_with_same_hubs[
        fleets_with_same_hubs["FleetID"].apply(lambda id: len(id) > 1)
    ]
    # Then filters by the number of fleet ids in previous response
    # only a set of fleets with the same hubs are relevant

    fleets_with_same_hubs.to_excel(writer, sheet_name=sheet_name, index=False)
    print("Done")

    # Filter the 'fleets' DataFrame to include only rows with duplicated FleetIDs
    sheet_name = "Same IDs"
    print(f"Generating {sheet_name} Sheet for {analysis_file}...", end=" ")

    aggregations = {
        "ORG": list,
        "Description": list,
    }
    fleets_with_same_ids = fleets.groupby("FleetID").agg(aggregations).reset_index()
    # First group data by hub ids

    fleets_with_same_ids = fleets_with_same_ids[
        fleets_with_same_ids["Description"].apply(lambda x: len(x) > 1)
    ]
    fleets_with_same_ids.to_excel(writer, sheet_name=sheet_name, index=False)
    print("Done")

    # Filter the 'fleets' DataFrame to include only rows with duplicated Descriptions
    sheet_name = "Same Description"
    print(f"Generating {sheet_name} Sheet for {analysis_file}...", end=" ")

    aggregations = {"ORG": list, "FleetID": list, "State": list, "AssociatesIDs": list}
    fleets_with_same_description = (
        fleets.groupby("Description").agg(aggregations).reset_index()
    )
    fleets_with_same_description = fleets_with_same_description[
        fleets_with_same_description["FleetID"].apply(lambda x: len(x) > 1)
    ]
    fleets_with_same_description.to_excel(writer, sheet_name=sheet_name, index=False)
    print("Done")

    # Filter the 'fleets' DataFrame to include only rows whose descriptions do not contain a
    # reference to at least one HubName from the HubsNames
    sheet_name = "Bad Description"
    print(f"Generating {sheet_name} Sheet for {analysis_file}...", end=" ")

    fleets_with_poor_description = fleets[
        fleets.apply(
            is_valid_description,
            axis=1,
            # axis=1 indicates that the function should be applied to each row of the DataFrame.
            # if axis=0 were specified, the lambda function would be applied column-wise,
            # executing the function on each column of the DataFrame.
        )
    ][["ORG", "Description", "HubsNames", "FleetID", "AssociatesIDs"]]
    fleets_with_poor_description.to_excel(writer, sheet_name=sheet_name, index=False)
    print("Done")

    print(f"Saving {analysis_file}... ", end=" ")
    writer.close()
    print("Done")

    # prompt(history, agent)


def prompt(history, agent):
    while True:
        user_question = get_validated_input("Ask your question: ")
        try:
            response = agent.run(user_question)
            # print(f"SYSTEM: {response}")
            # print(f"SYSTEM: {response['message']['content']}")

            # Store the user question and agent response in history
            history.loc[len(history)] = [user_question, response["message"]["content"]]

            # Save updated history to CSV file
            history.to_csv("./history/question_history.csv", index=False)
        except Exception as e:
            print("Couldn't execute this action. See error below")
            print(e)
        print()


def get_validated_input(prompt):
    while True:
        user_input = input(prompt)
        if user_input.strip():
            return user_input.strip()
        else:
            print("Invalid input. Please try again.")


def main():
    print(
        "Running script...",
    )
    logFile = files.create_logs_file()
    files.start_logging(logFile)

    analyze_data()

    files.stop_logging()
    files.close_logs_file(logFile)

    print("Done!")
    print("Check out the logs to see the full results")


main()
