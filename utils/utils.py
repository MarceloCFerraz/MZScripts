from datetime import datetime

ORGS = {
    "PROD": {
        "CLM": "8a9e84be-9874-4346-baab-26053d35871e",
        "STAPLES": "3c897e84-3957-4958-b54d-d02c01b14f15",
        "HN": "c88987f9-91e8-4561-9f07-df795ef9b8f0",
        "EDG": "ca3ffc06-b583-409f-a249-bdd014e21e31",
        "M3": "e9b34629-061d-4e24-93b1-717c00e2f116",
        "CFM": "8a9e84be-9874-4346-baab-26053d35871e",
        # "WALT'S": "ce8766a5-1d0f-4146-8a7c-98c0879cef10",  # Sandbox
        # "CUB": "6591e63e-6065-442d-87c3-20a5cd98cdba",  # not a client anymore
        "CUBPHARMA": "706660ca-71f6-4c01-a9ff-3a480acebaf4",
        "SHOPRITE-MM": "3f7539c3-ebbb-4d97-ac9f-bc66862c6ab8",
        "SHOPRITE": "3f7539c3-ebbb-4d97-ac9f-bc66862c6ab8",
        # "EMPIRE": "de03ba9f-7baa-4f64-9628-5eb75b970af1",  # Sandbox
        "ESSENDANT": "3d765297-0e0e-4178-843b-0ebdac333c7a",
        # "DELIVERY SOLUTIONS": "1bced832-4e3b-4f21-b803-477869cf02af", # Sandbox
        "LOWES": "8c381810-baf7-4ebe-a5f2-13c28b1ec7a4",
    },
    "STAGE": {
        "CLM": "76c23687-43c4-4fe3-b5f0-4cdd386e7895",
        "STAPLES": "3e59b207-cea5-4b00-8035-eed1ae26e566",
        "HN": "c88987f9-91e8-4561-9f07-df795ef9b8f0",
        "EDG": "4a00ea0a-ebe2-4a77-8631-800e0daa50c5",
        "M3": "28d04fba-012b-46ee-ab9a-d2909672e70e",
        "CFM": "76c23687-43c4-4fe3-b5f0-4cdd386e7895",
        "WALT'S": "f7c63075-2eb4-4056-9fe7-f403278f253b",
        # "CUB": "12d035f7-16c7-4c02-9b38-f1212b6f92f3",  # not a client anymore
        "CUBPHARMA": "6591e63e-6065-442d-87c3-20a5cd98cdba",
        "SHOPRITE-MM": "46474980-b149-4779-b9b5-76ea3d7baa90",
        "SHOPRITE": "397190aa-18ab-4bef-a8aa-d5875d738911",
        "EMPIRE": "09de776e-10cc-437d-9abc-ee5103d3b974",
        "ESSENDANT": "af0db6df-c6fd-4ad3-919c-350501c25bae",
        "DELIVERY SOLUTIONS": "cc2a4805-5b7e-49e1-80a1-a62cf906214d" #,
        # "LOWES": "",  # doesn't have a stage org so far
    }
}
ASSOCIATE_KEY_TYPES = [
    "ORG ID",
    "ASSOCIATE ID",
    "REFERENCE ID",
    "NAME",
    "EMAIL",
    "USERNAME",
    "STATE",
    "TYPE",
    "ASSOCIATE TYPE",
    "SKILL",
    "SKILL RATING VALUE",
    "RATING",
    "FLEET ID",
    "CLUSTER ID",
    "HUB ID",
    "LOCATION ID",
    "WORLDVIEW ID",
    "AVAILABILITY FLEET ID",
    "AVAILABILITY CLUSTER ID",
]


def get_formated_now():
    return str(
        datetime.now().replace(second=0, microsecond=0)
    ).replace(':', '-').replace(' ', 'T')


def find_biggest_divisor(number):
    for i in range(number - 1, 1, -1):
        if number % i == 0 and i != number / 2:
            return i
    return 4
    # default items per line is 4


def print_array_items(array):
    divisor = find_biggest_divisor(len(array))

    for i in range(0, len(array)):
        item = array[i] + "   "
        if 0 < i < len(array) and (i + 1) % divisor == 0:
            item += "\n"
        print(f"{item}", end="")
    print()


def select_env():
    envs = ["PROD", "STAGE"]
    env = ""
    print("SELECT THE ENV")
    print(f"Options: {'   '.join(envs)}")
    while env not in envs:
        env = str(input("> ")).upper().strip()

    return env


def select_org(env):
    orgs = list(ORGS[env].keys())
    org = ""

    print(f"SELECT THE ORG ({env})")
    print("Options: ")
    print_array_items(orgs)

    while org not in orgs:
        org = str(input("> ")).upper().strip()
    return ORGS[env][org] # returns orgId


def get_associate_key_type_index():
    length = int(len(ASSOCIATE_KEY_TYPES))

    for i in range(0, length):
        ASSOCIATE_KEY_TYPES[i] += f" ({i})"

    print("SELECT THE KEY TYPE INDEX")
    print("Options:")
    print_array_items(ASSOCIATE_KEY_TYPES)
    key_type_index = -1

    while key_type_index < 0 or key_type_index > length:
        key_type_index = int(input("> "))

    return key_type_index


def get_associate_key_type(key_type_index):
    return ASSOCIATE_KEY_TYPES[key_type_index]


def calculate_elapsed_time(start, finish):
    elapsed_seconds = (finish - start) // 1000000000

    elapsed_hours = elapsed_seconds // 3600
    if elapsed_hours >= 1:
        elapsed_seconds -= (elapsed_hours * 3600)

    elapsed_minutes = elapsed_seconds // 60
    if elapsed_minutes >= 1:
        elapsed_seconds -= (elapsed_minutes * 60)

    return {"hours": elapsed_hours, "minutes": elapsed_minutes, "seconds": elapsed_seconds}


def print_elapsed_time(start, finish):
    elt = calculate_elapsed_time(start, finish)

    response = "Took "
    for key in elt.keys():
        response += f"{str(elt[key])} {key} " if elt[key] > 0 else ""

    print(response)


def divide_into_batches(lst, batch_size=100):
    batches = []
    for i in range(0, len(lst), batch_size):
        batch = lst[i:i+batch_size]
        batches.append(batch)
    return batches
