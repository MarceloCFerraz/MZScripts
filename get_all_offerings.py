import json
import os

import requests


def get_offering():
    url = "http://caos.prod.milezero.com/caos-war/api/3f7539c3-ebbb-4d97-ac9f-bc66862c6ab8/offering/list"
    config = requests.get(url=url).json()
    return config


def get_fsgs():
    url = "https://qilin.prod.milezero.com/qilin-war/api/fulfillmentservicegroup/3f7539c3-ebbb-4d97-ac9f-bc66862c6ab8?facilityId=f89af170-a580-413d-af2e-7a913b1b7ab9"

    data = requests.get(url=url).json()
    return data


def get_pull(fsgId):
    url = f"https://qilin.prod.milezero.com/qilin-war/api/pulls/3f7539c3-ebbb-4d97-ac9f-bc66862c6ab8?fsgId={fsgId}"

    data = requests.get(url=url).json()

    return data


def detach_fs_from_fsg(serviceId, fsgId):
    url = f"https://qilin.prod.milezero.com/qilin-war/api/fulfillmentservicegroup/3f7539c3-ebbb-4d97-ac9f-bc66862c6ab8/{fsgId}/{serviceId}"
    data = requests.delete(url=url)

    return data


def delete_pull(pullId):
    url = f"https://qilin.prod.milezero.com/qilin-war/api/pulls/3f7539c3-ebbb-4d97-ac9f-bc66862c6ab8/{pullId}"

    data = requests.delete(url=url)
    return data


def delete_fs(serviceId):
    url = f"https://qilin.prod.milezero.com/qilin-war/api/fulfillmentservices/3f7539c3-ebbb-4d97-ac9f-bc66862c6ab8/{serviceId}"

    data = requests.delete(url=url)
    return data


def delete_fsg(fsgId):
    url = f"https://qilin.prod.milezero.com/qilin-war/api/fulfillmentservicegroup/3f7539c3-ebbb-4d97-ac9f-bc66862c6ab8/{fsgId}"

    data = requests.delete(url=url)
    return data


def save_json_to_file(jsonData, name, identifier):
    # get current file directory and replaces "\" for "/"
    # even in windows this works out just fine
    current_dir = os.path.realpath(os.path.dirname(__name__)).replace("\\", "/")

    # creates "RESULTS" folder directory
    response_dir = current_dir + "/RESULTS"

    os.makedirs(response_dir, exist_ok=True)

    # names the file
    key = f"{name}_{identifier}.json"

    # this is the complete directory and where the file will be saved
    final_dir = os.path.join(response_dir, key)

    result = f"File {final_dir} "

    with open(final_dir, "w") as json_file:
        try:
            json_file.write(jsonData)
            result += "created SUCCESSFULLY!"
        except Exception as e:
            result += f"COULD NOT be created. See exception bellow:\n\n{e}"

    print(result)


def main():
    window = "PT2H"

    offerings = [
        o
        for o in get_offering()["configs"]
        if o["relativeRange"]["slaDuration"] == window
    ]

    if not offerings:
        print("No offerings found")
        return

    fsgs = get_fsgs()["fulfillmentServiceGroups"]
    print(f"Got {len(fsgs)} fulfillment service groups")
    # print([f["groupId"] for f in fsgs])

    for offer in offerings:
        print("\n===============")
        offerId = offer["id"]
        print(f"offeringId: {offerId}")
        print(f"description: {offer['description']}")

        fsg = [fsg for fsg in fsgs if fsg["offerId"] == offerId]

        if not fsg:
            print(f"Fulfillment service group not found for offer {offerId}")
            continue

        fsgId = fsg[0]["groupId"]

        fs = fsg[0]["fulfillmentServices"]
        fsId = fs[0]["fulfillmentService"]["serviceId"]

        pull = get_pull(fsgId)[0]
        pullId = pull["pullId"]

        print("Backing up data")
        save_json_to_file(json.dumps(fsg), "fsg", fsgId)
        save_json_to_file(json.dumps(fs), "fs", fsId)
        save_json_to_file(json.dumps(pull), "pull", pullId)

        print(f"Detaching {fsId} from {fsgId}")
        detach_fs_from_fsg(fsId, fsgId)

        print(f"Deleting Service {fsId}")
        delete_fs(fsId)

        print(f"Deleting Pull {pullId}")
        delete_pull(pullId)

        print(f"Deleting Service Group {fsgId}")
        delete_fsg(fsgId)


if __name__ == "__main__":
    main()
