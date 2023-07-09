import os

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
        df = pandas.DataFrame(columns=["User Question", "Agent Response"])
        df.to_csv(f"./{dir}/{filename}", index=False)


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


def analyze_data():
    fleets = pandas.read_csv("Fleets Data.csv")
    
    # agent = setup_agent(fleets)

    # Group the fleets based on unique combinations of 'HubIds' and 'ORG'
    fleets_with_same_hubs = fleets.groupby(['HubsIDs', "ORG"])['FleetID'].apply(list).reset_index()
    fleets_with_same_hubs.to_excel("Fleets With The Same Hubs and Orgs 1.xlsx", index=False)

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
