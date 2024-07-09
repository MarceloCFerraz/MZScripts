from utils import associates, files, utils


def main(env, orgId, user_name):
    answer = utils.select_answer(question=">> Do you have an associate ID? ")

    if answer == "Y":
        associate = associates.get_associate_by_id(env, orgId, False)
    else:
        associate = associates.get_associate_by_name_or_email(env, orgId, False)

    if associate is None:
        print("Associate not found! Quitting program")
        return

    new_account_type = input(">> What would you like to be the new account type?\n> ")
    bkp = associate
    associate["associateType"] = new_account_type

    response = associates.update_associate_data(env, associate, user_name)

    if not response:
        print(
            "There was an error updating the associate, nothing was returned by the API"
        )
        return

    if response.status_code >= 400:
        print("There was an error updating the associate, check the error below:")
        print(response.text)
        return

    print(
        f"Updated {associate['associateId']} from {bkp['associateType']} to {new_account_type}"
    )
    files.save_json_to_file(associate, "CHANGE_ASSOCIATE_ACCOUNT_TYPE")


if __name__ == "__main__":
    env = utils.select_env()
    orgId = utils.select_org(env)
    user_name = input("What is your name?\n> ")

    main(env, orgId, user_name)
