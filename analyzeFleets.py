import os
from ast import literal_eval

import pandas

from langchain.chat_models import ChatOpenAI
from langchain.agents import create_pandas_dataframe_agent
from langchain.agents.agent_types import AgentType

from utils import aikey


os.environ["OPENAI_API_KEY"] = aikey.API_KEY


def verify_question_history_file():
    dir = verify_history_dir()
    filename = "question_history.csv"

    if not os.path.isfile(filename):
        # Create an empty question history file
        fleets = pandas.DataFrame(columns=["User Question", "Agent Response"])
        fleets.to_csv(f"./{dir}/{filename}", index=False)


def verify_history_dir():
    dirName = "history"

    if not os.path.isdir(dirName):
        # Create a directory called history
        os.mkdir(dirName)

    return dirName


def print_initial_and_history_messages(initial_messages):
    # Print initial system messages
    for message in initial_messages["messages"]:
        if message["role"] == "system":
            print("SYSTEM:", message["content"])


def setup_initial_messages():
    # Load historical questions and answers from CSV file
    history = pandas.read_csv("./history/question_history.csv")

    # Extract user questions and agent responses
    user_questions = history["User Question"].tolist()
    agent_responses = history["Agent Response"].tolist()

    # Initialize ChatOpenAI agent with historical context
    initial_messages = {
        "messages": [
            {"role": "system", "content": "Welcome! You are about to interact with an experienced data scientist and analyst."},
            {"role": "system", "content": "As an expert in the field, I can provide insights and recommendations on your data science questions."},
            {"role": "system", "content": "Feel free to ask me anything related to data analysis, machine learning, or statistical modeling."},
            {"role": "system", "content": "Please ask your questions in complete sentences."},
            {"role": "system", "content": "If you need assistance at any point, feel free to ask."},
            {"role": "system", "content": "Here's what we've discussed so far:"}
        ]
    }

    for question, response in zip(user_questions, agent_responses):
        initial_messages["messages"].append({"role": "user", "content": question})
        initial_messages["messages"].append({"role": "assistant", "content": response})

    print_initial_and_history_messages(initial_messages)

    return initial_messages


def setup_chat():
    chat = ChatOpenAI(
        model="gpt-3.5-turbo-16k-0613",
        temperature=0.0 #,
        # model_kwargs=setup_initial_messages()
    )

    return chat

def setup_agent(dataFrame):
    verify_question_history_file()

    agent = create_pandas_dataframe_agent(
        setup_chat(),
        dataFrame,
        verbose=True,
        agent_type=AgentType.OPENAI_FUNCTIONS
    )

    return agent


def is_valid_description(row):
    # hubsNames, hubsIDs, associatesNames and associatesIDs are stored in the csv file as repr string. 
    # repr strings can't have their \n chars replaced directly, the only way of doing so is below
    hubNames = str(literal_eval(row["HubsNames"])).replace("'", "")  

    for hubName in hubNames.splitlines():
        if hubName not in row["Description"]:
            # print(f"{row['Description']} doesn't contain {hubName}")
            return True
    return False


def analyze_data():
    print("Loadin data from CSV file...", end=" ")
    fleets = pandas.read_csv("Fleets Data.csv")  # Pandas DataFrame containing all data
    print("Done")

    analysis_file = "Fleet Analysis.xlsx"
    writer = pandas.ExcelWriter(analysis_file, engine='xlsxwriter')
    
    # agent = setup_agent(fleets)

    # Group the fleets based on unique combinations of 'HubIds' and 'ORG'
    sheet_name = "Same Hubs"
    print(f"Generating {sheet_name} Sheet for {analysis_file}...", end=" ")

    fleets_with_same_hubs = fleets.groupby(
        ['ORG', 'HubsIDs']
    )['FleetID'].apply(list).reset_index()
    fleets_with_same_hubs.to_excel(writer, sheet_name=sheet_name, index=False)
    print("Done")

    # Filter the 'fleets' DataFrame to include only rows with duplicated FleetIDs
    sheet_name = "Same IDs"
    print(f"Generating {sheet_name} Sheet for {analysis_file}...", end=" ")

    fleets_with_same_ids = fleets.groupby(
        ['ORG', 'FleetID']
    )['Description'].apply(list).reset_index()
    # fleets[
    #     fleets['FleetID'].duplicated(keep=False)
    # ][['ORG', 'Description', 'FleetID']]  # Sheet Headers in order
    fleets_with_same_ids.to_excel(writer, sheet_name=sheet_name, index=False)
    print("Done")

    # Filter the 'fleets' DataFrame to include only rows with duplicated Descriptions
    sheet_name = "Same Description"
    print(f"Generating {sheet_name} Sheet for {analysis_file}...", end=" ")

    fleets_with_same_description = fleets.groupby(
        ['ORG', 'Description']
    )['FleetID'].apply(list).reset_index()
    # fleets[
    #     fleets['Description'].duplicated(keep=False)
    # ][['ORG', 'Description', 'FleetID']]
    fleets_with_same_description.to_excel(writer, sheet_name=sheet_name, index=False)
    print("Done")

    # Filter the 'fleets' DataFrame to include only rows whose descriptions do not contain a
    # reference to at least one HubName from the HubsNames
    sheet_name = "Bad Description"
    print(f"Generating {sheet_name} Sheet for {analysis_file}...", end=" ")
    
    fleets_with_poor_description = fleets[
        fleets.apply(
            is_valid_description,
            axis=1  
            # axis=1 indicates that the function should be applied to each row of the DataFrame. 
            # if axis=0 were specified, the lambda function would be applied column-wise, 
            # executing the function on each column of the DataFrame.
        )
    ][['ORG', 'Description', 'HubsNames', 'FleetID']]
    fleets_with_poor_description.to_excel(writer, sheet_name=sheet_name, index=False)
    print("Done")

    print(f"Saving {analysis_file}... ", end=" ")
    writer.close()
    print("Done")

    # # Group the fleets based on unique combinations of 'HubIds' and 'ORG'
    # grouped2 = fleets.groupby(['HubsIDs', 'ORG']).apply(
    #     lambda x: {
    #         'FleetIDs': x['FleetID'].tolist(),
    #         'Associates': x[['AssociatesNames', 'AssociatesIDs']].to_dict('records')
    #     }
    # ).reset_index(name='GroupedData')
    # grouped2.to_excel("Fleets With The Same Hubs and Orgs 2.xlsx", index=False)

    # # Iterate over the groups and print the details
    # for hubs_ids, org, fleet_ids in fleets_with_same_hubs.items():
    #     print("Hub ID:", hubs_ids)
    #     print("ORG:", org)
    #     print("Fleet IDs:", fleet_ids)
    #     print("Hub Names:", fleets.loc[(fleets['HubsIDs'] == hubs_ids) & (fleets['ORG'] == org), 'HubsNames'].iloc[0])
    #     print("Associate Names:", fleets.loc[(fleets['HubsIDs'] == hubs_ids) & (fleets['ORG'] == org), 'AssociatesNames'].tolist())
    #     print("Associate IDs:", fleets.loc[(fleets['HubsIDs'] == hubs_ids) & (fleets['ORG'] == org), 'AssociatesIDs'].tolist())
    #     print()
    
    # prompt(history, agent)


def prompt(history, agent):
    while True:
        user_question = get_validated_input("Ask your question: ")
        try:
            
            response = agent.run(user_question)
            # print(f"SYSTEM: {response}")
            # print(f"SYSTEM: {response['message']['content']}")
            
            # Store the user question and agent response in history
            history.loc[len(history)] = [user_question, response['message']['content']]
            
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
    analyze_data()


main()
