from utils import utils, associates


def main():
    userName = input("What is your name?\n> ")
    env = utils.select_env()
    orgId = utils.select_org(env)

    print("TYPE THE ASSOCIATE ID")
    associateId = input("> ")

    associate = associates.get_associate_data(env=env, orgId=orgId, associateId=associateId)

    if associate is not None:
        print("Associate Found!")
        print("Inverting State...")
        print(f"{associates.change_associate_state(env=env, associateData=associate, userName=userName)}")


main()
