from datetime import datetime

DEFAULT_SPACING = 30
ORGS = {
    "PROD": {
        "CLM": "8a9e84be-9874-4346-baab-26053d35871e",
        "STAPLES": "3c897e84-3957-4958-b54d-d02c01b14f15",
        "HN": "c88987f9-91e8-4561-9f07-df795ef9b8f0",
        "EDG": "ca3ffc06-b583-409f-a249-bdd014e21e31",
        "M3": "e9b34629-061d-4e24-93b1-717c00e2f116",
        "CFM": "8a9e84be-9874-4346-baab-26053d35871e",
        # "CUB": "6591e63e-6065-442d-87c3-20a5cd98cdba",
        "CUBPHARMA": "706660ca-71f6-4c01-a9ff-3a480acebaf4",
        "SHOPRITE-MM": "3f7539c3-ebbb-4d97-ac9f-bc66862c6ab8",
        "SHOPRITE": "3f7539c3-ebbb-4d97-ac9f-bc66862c6ab8",
        "ESSENDANT": "3d765297-0e0e-4178-843b-0ebdac333c7a",
        "LOWES": "8c381810-baf7-4ebe-a5f2-13c28b1ec7a4",
    },
    "STAGE": {
        "CLM": "76c23687-43c4-4fe3-b5f0-4cdd386e7895",
        "STAPLES": "3e59b207-cea5-4b00-8035-eed1ae26e566",
        "HN": "c88987f9-91e8-4561-9f07-df795ef9b8f0",
        "EDG": "4a00ea0a-ebe2-4a77-8631-800e0daa50c5",
        "M3": "28d04fba-012b-46ee-ab9a-d2909672e70e",
        "CFM": "58953b8f-f14e-4998-ba5b-19e00d3f2221",
        "WALT'S": "f7c63075-2eb4-4056-9fe7-f403278f253b",
        # "CUB": "12d035f7-16c7-4c02-9b38-f1212b6f92f3",
        "CUBPHARMA": "6591e63e-6065-442d-87c3-20a5cd98cdba",
        "SHOPRITE-MM": "46474980-b149-4779-b9b5-76ea3d7baa90",
        "SHOPRITE": "397190aa-18ab-4bef-a8aa-d5875d738911",
        "EMPIRE": "09de776e-10cc-437d-9abc-ee5103d3b974",
        "ESSENDANT": "af0db6df-c6fd-4ad3-919c-350501c25bae",
        "DELIVERY SOLUTIONS": "cc2a4805-5b7e-49e1-80a1-a62cf906214d",
    },
    "INTEG": {
        "HN": "1aaae948-7cbc-4fc2-9cbf-8e17fe8c1457",
        "EDG": "2c221bfd-1a58-4494-b2b5-20dc2407acd9",
        "M3": "1bdc25a0-d75e-4f9e-a648-e16af9d2f5f6",
        "CLM": "33d7ccef-e43e-4e1c-940a-a9120b504888",
        # "CUB": "1aac6c19-e564-4d96-8778-910fadd9a513",
        # "WALT'S": "ce8766a5-1d0f-4146-8a7c-98c0879cef10",
        "CUBPHARMA": "93e0eee5-50e6-4200-86cf-1ab48303bb15",
        "SHOPRITE-MM": "44cf45b0-18f7-4f68-a43f-28fbeee9f8f9",
        "SHOPRITE": "c5ad97fe-db54-4522-a166-2ad3e0a85edb",
        "ESSENDANT": "0ed1589a-30f8-4b87-b458-120149bcd89e",
        "DELIVERY SOLUTIONS": "1bced832-4e3b-4f21-b803-477869cf02af",
        "EMPIRE": "de03ba9f-7baa-4f64-9628-5eb75b970af1",
    },
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
    """
    Finds the biggest divisor of a given number.

    Args:
        number (int): The number to find the divisor for.

    Returns:
        int: The biggest divisor of the number.
    """
    for i in range(number - 1, 1, -1):
        if number % i == 0:
            # prime numbers won't get into here
            return i
    # so we need to return a default value of items per line
    return 3


def print_array_items(array):
    """
    Prints the items in an array, formatting them into lines.

    Args:
        array (list): The array of items to print.

    Returns:
        None
    """
    divisor = find_biggest_divisor(len(array))
    items_per_line = divisor

    for i, item in enumerate(array):
        print(f"{item:^{DEFAULT_SPACING}}", end="")
        if (i + 1) % items_per_line == 0:
            print()

    print()


def print_formatted_message(message, items_count, separator="*"):
    print(
        f"{' {} '.format(message):{separator}^{DEFAULT_SPACING * find_biggest_divisor(items_count)}}"
    )


def select_env():
    """
    Allows the user to select an environment.

    Returns:
        str: The selected environment.
    """
    envs = ORGS.keys()
    env = ""
    print_formatted_message("SELECT THE ENV", len(envs), " ")
    print_formatted_message("Options", len(envs))
    print_array_items(envs)
    while env not in envs:
        env = str(input("> ")).upper().strip()

    return env


def select_org(env):
    """
    Allows the user to select an organization for a specific environment.

    Args:
        env (str): The selected environment.

    Returns:
        str: The selected organization's ID.
    """
    orgs = list(ORGS[env].keys())
    org = ""

    print()
    print_formatted_message(f"SELECT THE ORG ({convert_env(env)})", len(orgs), " ")
    print_formatted_message("Options", len(orgs))
    print_array_items(orgs)

    while org not in orgs:
        org = str(input("> ")).upper().strip()
    return ORGS[env][org]  # returns orgId


def get_formated_now():
    """
    Retrieves the current date and time in a formatted string.

    Returns:
        str: The formatted current date and time.
    """
    return (
        str(datetime.now().replace(second=0, microsecond=0))
        .replace(":", "-")
        .replace(" ", "T")
    )


def get_associate_key_type_index():
    """
    Allows the user to select an index for the associate key type.

    Returns:
        int: The selected index.
    """
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
    """
    Retrieves the associate key type based on the selected index.

    Args:
        key_type_index (int): The selected index.

    Returns:
        str: The associate key type.
    """
    return ASSOCIATE_KEY_TYPES[key_type_index]


def calculate_elapsed_time(start, finish):
    """
    Calculates the elapsed time between two timestamps.

    Args:
        start (int): The start timestamp.
        finish (int): The finish timestamp.

    Returns:
        dict: The elapsed time in hours, minutes, and seconds.
    """
    elapsed_seconds = (finish - start) // 1000000000

    elapsed_hours = elapsed_seconds // 3600
    if elapsed_hours >= 1:
        elapsed_seconds -= elapsed_hours * 3600

    elapsed_minutes = elapsed_seconds // 60
    if elapsed_minutes >= 1:
        elapsed_seconds -= elapsed_minutes * 60

    return {
        "hours": elapsed_hours,
        "minutes": elapsed_minutes,
        "seconds": elapsed_seconds,
    }


def print_elapsed_time(start, finish):
    """
    Prints the elapsed time between two timestamps.

    Args:
        start (int): The start timestamp.
        finish (int): The finish timestamp.

    Returns:
        None
    """
    elt = calculate_elapsed_time(start, finish)

    response = "Took "
    for key in elt.keys():
        response += f"{str(elt[key])} {key} " if elt[key] > 0 else ""

    print(response)


def divide_into_batches(lst, batch_size=100):
    """
    Divides a list into batches of a specified size.

    Args:
        lst (list): The list to divide.
        batch_size (int): The size of each batch. Defaults to 100.

    Returns:
        list: The list of batches.
    """
    batches = []
    for i in range(0, len(lst), batch_size):
        batch = lst[i : i + batch_size]
        batches.append(batch)
    return batches


def select_answer(question=None, answers=None):
    """
    Presents a question to the user and expects a specific answer.

    This function presents a question to the user and expects a specific answer. It ensures that the user's input matches the available answer options.

    Parameters:
    - question (str, optional): The question to be presented. If not provided, a default question will be used.
    - answers (list, optional): The available answer options. If not provided, "Y" or "N" will be used.

    Returns:
    - answer (str): The user's selected answer.
    """
    if answers is None:
        answers = ["Y", "N"]

    if question is None:
        question = (
            ">> Does the associate need to maintain access to all previous hubs? "
        )

    question = question + f"({'/'.join(answers)})"

    answer = ""
    print(question)
    while answer not in answers:
        answer = str(input("> ")).upper().strip()

    return answer


def extract_property(obj, keys):
    """Helper function to extract a property from a dictionary."""
    try:
        prop = obj
        for key in keys:
            prop = prop[key]
        return prop
    except KeyError:
        return None


def convert_env(env):
    if env == "INTEG":
        env = "PROD"

    return env.lower()
