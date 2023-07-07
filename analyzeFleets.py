import os

from langchain.chat_models import ChatOpenAI
from langchain.agents import create_pandas_dataframe_agent
from langchain.agents.agent_types import AgentType

import pandas

from utils import aikey

os.environ["OPENAI_API_KEY"] = aikey.API_KEY


def analyze_data():
    dataFrame = pandas.read_csv("Fleet Analysis.csv")
    chat = ChatOpenAI(model="gpt-3.5-turbo-16k-0613", temperature=0.0)
    agent = create_pandas_dataframe_agent(
        chat, 
        dataFrame, 
        verbose=True,
        agent_type=AgentType.OPENAI_FUNCTIONS
    )

    while True:
        print("Ask your question\n> ", end="")
        try:
            agent.run(input())
        except Exception as e:
            print("Couldn't execute this action. See error below")
            print(e)
        print()


def main():
    analyze_data()


main()