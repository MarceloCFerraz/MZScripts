from datetime import datetime
from utils import utils
import json
import os
import sys


def get_data_from_file(fileName):
    """
    Retrieves data from a text file and removes duplicates.

    Parameters:
        fileName (str): The name of the file (without the extension).

    Returns:
        list: The unique lines of data from the file.
    """
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
    """
    Formats JSON data with indentation.

    Parameters:
        data (dict): The JSON data to format.

    Returns:
        str: The formatted JSON data.
    """
    return json.dumps(data, indent=2)


def save_txt_file(data, filePrefix):
    """
    Saves a list of data to a text file.

    Parameters:
        data (list): The data to save.
        filePrefix (str): The prefix for the file name.

    Returns:
        None
    """
    # get current file directory and replaces "\" for "/"
    # even in windows this works out just fine
    current_dir = os.path.realpath(os.path.dirname(__name__)).replace("\\", "/")

    # creates "RESULTS" folder directory
    response_dir = current_dir #+ "/RESULTS"

    os.makedirs(response_dir, exist_ok=True)

    # names the file
    key = f"{filePrefix}.txt"#_{utils.get_formated_now()}.txt"

    # this is the complete directory and where the file will be saved
    final_dir = os.path.join(response_dir, key)

    result = f"File {key} created SUCCESSFULLY!"

    with open(final_dir, "w") as txt:
        for line in data:
            txt.write(line + "\n")

    print(result)


def save_json_to_file(jsonData, filePrefix):
    """
    Saves JSON data to a file.

    Parameters:
        jsonData (str): The JSON data to save.
        filePrefix (str): The prefix for the file name.

    Returns:
        None
    """
    # get current file directory and replaces "\" for "/"
    # even in windows this works out just fine
    current_dir = os.path.realpath(os.path.dirname(__name__)).replace("\\", "/")

    # creates "RESULTS" folder directory
    response_dir = current_dir + "/RESULTS"

    os.makedirs(response_dir, exist_ok=True)

    # names the file
    key = f"{filePrefix}_{utils.get_formated_now()}.json"

    # this is the complete directory and where the file will be saved
    final_dir = os.path.join(response_dir, key)

    result = f"File {key} "

    with open(final_dir, "w") as json_file:
        try:
            json_file.write(jsonData)
            result += f"created SUCCESSFULLY!"
        except Exception as e:
            result += f"COULD NOT be created. See exception bellow:\n\n{e}"

    print(result)


def create_dir(dirName):
    """
    Creates a directory if it doesn't already exist.

    Parameters:
        dirName (str): The name of the directory.

    Returns:
        str: The name of the created directory.
    """
    if not os.path.isdir(dirName):
        os.mkdir(dirName)

    return dirName


def create_logs_file(prefix=None, suffix=None):
    """
    Creates a log file for logging program output.

    Parameters:
        prefix (str): Optional prefix for the log file name.
        suffix (str): Optional suffix for the log file name.

    Returns:
        file: The log file object.
    """
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
    """
    Closes the log file.

    Parameters:
        log_file (file): The log file object.

    Returns:
        None
    """
    log_file.close()


def start_logging(log_file):
    """
    Starts redirecting the standard output to the log file.

    Parameters:
        log_file (file): The log file object.

    Returns:
        None
    """
    # Redirect the standard output to the log file
    sys.stdout = log_file


def stop_logging():
    """
    Stops redirecting the standard output to the log file.

    Parameters:
        None

    Returns:
        None
    """
    sys.stdout = sys.__stdout__


def save_package_ids_to_file(packageIDs, fileName):
    """
    Saves a list of package IDs to a file.

    Parameters:
        packageIDs (list): The list of package IDs.
        fileName (str): The name of the file.

    Returns:
        None
    """
    with open(fileName, "w") as txt:
        for packageID in packageIDs:
            txt.write(packageID + "\n")
