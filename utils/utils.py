ORGS = {
    "PROD": {
        "STAPLES": "3c897e84-3957-4958-b54d-d02c01b14f15",
        "HN": "c88987f9-91e8-4561-9f07-df795ef9b8f0",
        "EDG": "ca3ffc06-b583-409f-a249-bdd014e21e31",
        "CUB": "6591e63e-6065-442d-87c3-20a5cd98cdba",
        "CUBPHARMA": "706660ca-71f6-4c01-a9ff-3a480acebaf4",
        "SHOPRITE": "3f7539c3-ebbb-4d97-ac9f-bc66862c6ab8",
        "LOWES": "8c381810-baf7-4ebe-a5f2-13c28b1ec7a4",
    },
    "STAGE": {
        "STAPLES": "3e59b207-cea5-4b00-8035-eed1ae26e566",
        "HN": "c88987f9-91e8-4561-9f07-df795ef9b8f0",
        "EDG": "4a00ea0a-ebe2-4a77-8631-800e0daa50c5",
        "CUB": "12d035f7-16c7-4c02-9b38-f1212b6f92f3",
        "CUBPHARMA": "6591e63e-6065-442d-87c3-20a5cd98cdba",
        "SHOPRITE": "397190aa-18ab-4bef-a8aa-d5875d738911"  #,
        # "LOWES": "",
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
