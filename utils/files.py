from datetime import datetime
from utils import utils
import json
import os
import sys


def get_data_from_file(fileName):
    with open(fileName+".txt", "r") as file:
        lines = file.readlines()
    
    results = []
    
    for line in lines:
        if line != "":
            results.append(line.strip())

    # removing duplicates from list
    # this make the list unordered. Comment this line if
    # this impact your workflow somehow
    results = list(set(results))
    
    print("{} unique lines in file {}\n".format(len(results), fileName))
    return results


def format_json(data):
    return json.dumps(data, indent=2)


def save_txt_file(data, filePrefix):
    # get current file directory and replaces "\" for "/"
    # even in windows this works out just fine
    current_dir = os.path.realpath(os.path.dirname(__name__)).replace("\\", "/")

    # creates "RESULTS" folder directory
    response_dir = current_dir + "/RESULTS"

    os.makedirs(response_dir, exist_ok=True)

    # names the file
    KEY = f"{filePrefix}_{utils.get_formated_now()}.txt"

    # this is the complete directory and where the file will be saved
    final_dir = os.path.join(response_dir, KEY)

    result = f"File {KEY} created SUCCESSFULLY!"

    with open(final_dir, "w") as txt:
        for line in data:
            txt.write(line + "\n")

    print(result)


def save_json_to_file(jsonData, filePrefix):
    # get current file directory and replaces "\" for "/"
    # even in windows this works out just fine
    current_dir = os.path.realpath(os.path.dirname(__name__)).replace("\\", "/")

    # creates "RESULTS" folder directory
    response_dir = current_dir + "/RESULTS"

    os.makedirs(response_dir, exist_ok=True)

    # names the file
    KEY = f"{filePrefix}_{utils.get_formated_now()}.json"

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
        os.mkdir(dirName)

    return dirName


def create_logs_file(prefix=None, suffix=None):
    dir = create_dir("logs")
    
    # Get the name of the current script file
    script_file = os.path.basename(sys.argv[0])

    # Remove the file extension from the script name
    script_name = os.path.splitext(script_file)[0]

    # Create the log file name
    log_file_name = script_name + f"_log_{utils.get_formated_now()}.txt"
    if prefix:
        log_file_name = prefix + "_" + log_file_name
    if suffix:
        log_file_name += "_" + suffix

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


def save_package_ids_to_file(packageIDs, fileName):
    with open(fileName, "w") as txt:
        for packageID in packageIDs:
            txt.write(packageID + "\n")
