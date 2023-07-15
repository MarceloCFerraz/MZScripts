from datetime import datetime
import json
import os
import sys


def format_json(data):
    return json.dumps(data, indent=2)


def save_json_to_file(jsonData, filePrefix):
    # get current file directory and replaces "\" for "/"
    # even in windows this works out just fine
    current_dir = os.path.realpath(os.path.dirname(__name__)).replace("\\", "/")

    # creates "RESULTS" folder directory
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


def create_dir(dirName):
    if not os.path.isdir(dirName):
        # Create a directory called history
        os.mkdir(dirName)

    return dirName


def create_logs_file():
    dir = create_dir("logs")
    
    # Get the name of the current script file
    script_file = os.path.basename(sys.argv[0])

    # Remove the file extension from the script name
    script_name = os.path.splitext(script_file)[0]

    # Create the log file name
    log_file_name = script_name + f"_log_{str(datetime.now()).replace(':', '-')}.txt"

    # Open the log file to redirect the standard output
    log_file = open(f"./{dir}/{log_file_name}", "w")

    return log_file


def close_logs_file(log_file):
    log_file.close()


def start_logging(log_file):
    # Redirect the standard output to the log file
    sys.stdout = log_file


def stop_logging():
    sys.stdout = sys.__stdout__
