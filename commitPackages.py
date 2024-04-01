from utils import files, packages, utils


def load_inputs(
    env=None,
    orgId=None,
    fileName=None,
    pids=None,
):
    if env is None:
        env = utils.select_env()

    if orgId is None:
        orgId = utils.select_org(env)

    if fileName is None:
        # The file name must be to the requester's hub name (e.g. 8506)
        if utils.select_answer(">> Do you have a file with the package keys?") == "Y":
            fileName = (
                input(">> Type the file name: ")
                .strip()
                .replace(".txt", "")
                .replace("./", "")
                .replace(".\\", "")
            )
            # if user wants to read packages from a file, get them now
            pids = files.get_data_from_file(fileName)

    if pids is None:
        pids = packages.get_list_of_keys("pi")

    main(
        env,
        orgId,
        pids,
    )


def main(
    env,
    orgId,
    keys,
):
    packages.commit_packages(env, orgId, keys)


if __name__ == "__main__":
    load_inputs()
