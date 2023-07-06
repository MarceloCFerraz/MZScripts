from datetime import datetime
import json
import os


def format_json(data):
    return json.dumps(data, indent=2)


def save_json_to_file(jsonData, filePrefix):
    # get current file directory and replaces "\" for "/"
    # even in windows this works out just fine
    current_dir = os.path.realpath(os.path.dirname(__name__)).replace("\\", "/")

    # creates "Responses" folder directory
    response_dir = current_dir + "/RESULTS"

    os.makedirs(response_dir, exist_ok=True)

    # names the file
    KEY = f"{filePrefix}_{datetime.now().strftime('%Y-%m-%d')}.json"

    # this is the complete directory and where the file will be saved
    final_dir = os.path.join(response_dir, KEY)

    result = f"File {KEY} "

    with open(final_dir, "w") as json_file:
        try:
            json_file.write(jsonData)
            result += f"created SUCCESSFULLY!"
        except Exception as e:
            result += f"COULD NOT be created. See exception bellow:\n\n{e}"

    print(result)
