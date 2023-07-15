import requests




def cancel(env, orgId, packageIds):
    # newStatus = "CANCELLED"

    API = f"https://switchboard.{env}.milezero.com/switchboard-war/api/package/cancel"
    
    requestData = {
        "orgId": orgId,
        "packageIds": packageIds,
        # "associate": {
        #     "name": "string",
        #     # "id": "string",
        #     # "type": "string"
        # },
        "notes": "Requested by dispatcher"
    }
    
    try:
        response = requests.post(url=API, json=requestData, timeout=10)
        print(f"> Result: ({response.status_code})\n")
        print(f"{response.text}")
    except Exception as e:
        print(f"> {packageIds} couldn't be CANCELLED. See error bellow")
        print(e)


def getDataLines(fileName):
    file = open(fileName+".txt", "r")
    lines = file.readlines()
    file.close()

    results = []
    
    for line in lines:
        results.append(line.strip())

    # removing duplicates from list
    # this make the list unordered. Comment this line if
    # this impact your workflow somehow
    results = list(set(results))
    
    print("{} lines in file {}\n".format(len(results), fileName))
    return results


packageIds = getDataLines("pids")
cancel("prod", "3c897e84-3957-4958-b54d-d02c01b14f15", packageIds)
