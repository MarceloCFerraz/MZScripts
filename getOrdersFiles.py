import csv
import requests
import pandas
from utils import utils

# fileName: Staples_8764_ORDERDET_20230902_PROD_US0436373.csv

def get_original_data(env, requestId, token):
    """
    Retrieves the original data on the file from staples SFTP/EDI, using the provided request ID and authentication token.

    Parameters:
    - env (str): The environment from which to retrieve the data.
    - requestId (str): The ID of the request for the original data.
    - token (str): The authentication token for accessing the data.

    Returns:
    - response (dict): The JSON response containing the original data.
    """
    # requestId: ad2a170b-d98e-46f7-8eda-486a2970a507 (arquivo original)
    # https://milevision.milezero.com/mv/uploads/requestfile?requestId=ad2a170b-d98e-46f7-8eda-486a2970a507
    
    print("Getting original Data...")

    url = "https://milevision{0}.milezero.com/mv/uploads/requestfile?requestId={1}"

    if env == "STAGE":
        url = url.format("-stage", requestId)
    else:
        url = url.format("", requestId)

    response = requests.get(
        url=url, 
        timeout=30, 
        headers={
            'Accept': 'application/json',
            'Authentication': token
        }
    )

    if response.status_code >= 400:
        print(response.status_code)
        print(response.text)
        
        response.raise_for_status

    return response.json()


def get_mz_data(env, parentId, token):
    """
    Retrieves the data from the converted MZ file format, using the provided parent ID and authentication token.

    Parameters:
    - env (str): The environment from which to retrieve the data.
    - parentId (str): The ID of the parent for the MZ data.
    - token (str): The authentication token for accessing the data.

    Returns:
    - response (dict): The JSON response containing the MZ data.
    """
    # parentId: 8e6eefcf-5f2a-4024-bd77-eb9399a7c5f5 (arquivo gerado)
    # https://milevision.milezero.com/mv/uploads/request?requestId=8e6eefcf-5f2a-4024-bd77-eb9399a7c5f5
    
    print("Getting MZ Data...")

    url = "https://milevision{0}.milezero.com/mv/uploads/request?requestId={1}"

    if env == "STAGE":
        url = url.format("-stage", parentId)
    else:
        url = url.format("", parentId)

    response = requests.get(
        url=url, 
        timeout=30, 
        headers={
            'Accept': 'application/json',
            'Authentication': token
        }
    )

    if response.status_code >= 400:
        print(response.status_code)
        print(response.text)
        
        response.raise_for_status

    return response.json()


def get_data_in_string(data_string):
    """
    Converts a comma-separated string into a list of individual data elements.

    Parameters:
    - data_string (str): The comma-separated string to be converted.

    Returns:
    - dataset (list): The list of individual data elements.
    """
    dataset = []
    data = ""

    for i in range(0, len(data_string)):
        char = data_string[i]

        if char == ",":
            # print(data)
            dataset.append(data)
            data = ""
        else:
            data += char

    # print(data)
    dataset.append(data)

    return dataset


def fix_product_description(content, difference):
    """
    Fixes the product description by combining multiple elements into a single element.

    Parameters:
    - content (list): The list of content elements.
    - difference (int): The difference between the length of content and headers.

    Returns:
    - new_list (list): The updated list with fixed product descriptions.
    """
    print("Fixing difference between columns and items...")
    new_list = []
    
    i = 0
    
    while i in range(0, len(content)):
        if i != 7:
            new_list.append(content[i])
            i += 1
        else:
            c = content[i]
            while difference != 0:
                i += 1
                c += " - " + content[i]
                difference -= 1
            
            i += 1
            new_list.append(c)
    
    # print(new_list)
    return new_list


def get_original_dict(data):
    """
    Parses the original data and converts it into a dictionary.

    Parameters:
    - data (list): The list of original data elements.

    Returns:
    - dictionary (dict): The dictionary representation of the original data.
    """
    # [
    # # {
    # #     "number": 0,
    # #     "code": "TE200",
    # #     "message": "SUCCESS",
    # #     "content": Country Code,Company Brand Code, POS Instance Number,Movex Code,Department Code,,    Sales Order Number,Product Code,Product Description,Quantity Sold,Sales Type,Sales Total,Amount Due,Pickup Location,Scannable ID,Weight,CODE,MESSAGE
    # #                AUS,         01,                 NXB,                01,                        NXB,P86683940*001,     CARTON,      CARTON - 1.0,OUTBOUND,0.0,0.0,,618668394001,236.54,P86683940*001,2023-11-08,TE200,SUCCESS
    # #     "content": "Country Code,Company Brand Code,POS Instance Number,Movex Code,Department Code,Sales Order Number,Product Code,Product Description,Quantity Sold,Sales Type,Sales Total,Amount Due,Pickup Location,Scannable ID,Carton Weight,Stock Required,Signature Required,Team Required,Length,Width,Height"
    # # },
    # ]
    
    print("Parsing original data...")

    dictionary = {}
    headers = get_data_in_string(data[0]['content'])

    for header in headers:
        dictionary[header] = []
    dictionary["CODE"] = []
    dictionary["MESSAGE"] = []

    for i in range(1, len(data)):
        content = get_data_in_string(data[i]['content'])
        # print(content)

        difference = len(content) - len(headers)

        if difference != 0:
            content = fix_product_description(content, difference)
            # difference = len(content) - len(headers)
            # print(difference)

        for j in range(0, len(content)):
            dictionary[headers[j]].append(content[j])

        dictionary["CODE"].append(data[i]['code'])
        dictionary["MESSAGE"].append(data[i]['message'])
    
    # print(dictionary)
    
    return dictionary

def save_csv_file(fileName, data):
    """
    Saves the provided data as a CSV file with the given filename.

    Args:
    - fileName (str): The name of the CSV file to be saved.
    - data (list): The data to be saved in the CSV file.

    Returns:
    - None
    """

    if len(data) < 1:
        print(f"Nothing to save on '{fileName}'")
    else:
        with open(fileName+".csv", 'w', newline='') as file:
            writer = csv.writer(file)
            
            for i in range (0, len(data)):
                row = get_data_in_string(data[i].get('content'))
                writer.writerow(row)

        print("File '{}' saved successfully".format(fileName))


def get_mz_dict(dataset):
    """
    Parses the MZ data and converts it into a dictionary.

    Parameters:
    - dataset (list): The list of MZ data elements.

    Returns:
    - dictionary (dict): The dictionary representation of the MZ data.
    """
    # [
    #     {
    #         "refId": "0517614062334001001",
    #         "rowType": "SHIPMENT",
    #         "orderId": "9ce8f812-f2ec-4b10-8fbe-126212df3c9c",
    #         "shipmentId": "40189fa3-3135-42d9-8e71-a75a2be450cc",
    #         "scannableId": null,
    #         "name": "ROUND ONE ENTERTAINMENT",
    #         "consignee": null,
    #         "addressLine1": "1191 GALLERIA BLVD",
    #         "addressLine2": null,
    #         "city": "ROSEVILLE",
    #         "state": "CA",
    #         "postalCode": "95678",
    #         "country": "US",
    #         "latitude": null,
    #         "longitude": null,
    #         "contents": "CARTON - COFFEEMATE FR VANILLA SS 360CT",
    #         "weight": null,
    #         "paymentDue": 0,
    #         "status": "FAILED",
    #         "creationTime": "",
    #         "shipDate": null,
    #         "lastProcessedTime": "1693885483844",
    #         "errorCode": "IN500",
    #         "errorMessage": "Internal Error"
    #     },
    # ]
    print("Parsing MZ Data...")

    dictionary = {}
    headers = []

    for key in dataset[0].keys():
        dictionary[key] = []
        headers.append(key)
    
    for i in range(0, len(dataset)):
        data = dataset[i]
        
        for header in headers:
            dictionary[header].append(data[header])
        
    # print(dictionary)

    return dictionary


def main():
    """
    The main function that orchestrates the data retrieval and processing.

    This function prompts the user to enter the environment, request ID, parent ID, and authentication token for accessing the data. It then retrieves the original and MZ data from the specified environment using the provided IDs and token. The original and MZ data are parsed into dictionaries. Finally, the dictionaries are saved as CSV files.

    Parameters:
    - None

    Returns:
    - None
    """
    env = utils.select_env()

    # env =  "PROD"
    # fileName = "Staples_8109_ORDERDET_20231003_PROD_US0446800"
    
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdXRob3JpemF0aW9uIjp7Imdyb3VwcyI6WyJFbmRlYXZvdXIiLCJFbmRlYXZvdXIgTWlsZVZpc2lvbiJdLCJyb2xlcyI6WyJNaWxlVmlzaW9uX1VzZXIiXSwicGVybWlzc2lvbnMiOltdfSwib3JnYW5pemF0aW9uIjp7IkFsYWJvIjp7Im9yZ05hbWUiOiJiMDgyOGU4My1iY2FlLTRkMGEtOTY5YS1lNTA5YjI1MzY3NTAiLCJvcmdJZCI6IjJjMjIxYmZkLTFhNTgtNDQ5NC1iMmI1LTIwZGMyNDA3YWNkOSJ9fSwib2JqZWN0cyI6eyJkcml2ZXJJZCI6ImMxZTQ4MTU5LWEyZTktNDI2Ni05MWRjLTdjNGU4YTI1MmVlMyJ9LCJpc3MiOiJodHRwczovL21pbGV6ZXJvLmF1dGgwLmNvbS8iLCJzdWIiOiJhdXRoMHw1YmUxNTBlNjk0NTc1NzdkNWEwMzNlYjQiLCJhdWQiOiI3dW1VTG1sQ1RKcjNzT256NWl3cG5DWG5YYzVMZTFMQyIsImlhdCI6MTY5OTQwMTIyMiwiZXhwIjoxNjk5NDM3MjIyfQ._UaxAEtBlmXuQ0yFljV4AIQTD4dpa9myEHzPPbTCqBI"

    fileName = input("Type in the file name ('file' column in orders page): ")
    # token = input("Paste the Authentication token: ")
    requestId = input("Type in the requestId (requestFile?): ")
    # requestId = "0d194a2e-5bdf-4968-831a-cf9d8a064327"
    
    original_data = get_original_data(env, requestId, token)

    print("Saving original file...")
    save_csv_file(f"Original {fileName}", original_data)

    # original_dict = get_original_dict(original_data)
    # original_df = pandas.DataFrame(data=original_dict)
    # original_df.to_csv(f"Original {fileName}.csv", index=False)

    parentId = input("Type in the parentId (request?): ")
    # parentId = "4bbb089a-6272-41e6-98e0-f78caed62383"

    mz_data = get_mz_data(env, parentId, token)
    mz_dict = get_mz_dict(mz_data)
    mz_df = pandas.DataFrame(data=mz_dict)

    print("Saving MZ file...")
    # save_csv_file(f"MZ {fileName}", mz_data)
    mz_df.to_csv(f"MZ {fileName}.csv", index=False)

    print("Finishing script...")


main()
