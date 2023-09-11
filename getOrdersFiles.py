import requests
import pandas
from utils import utils

# fileName: Staples_8764_ORDERDET_20230902_PROD_US0436373.csv

def get_original_data(env, requestId, token):
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
    #         [
    # # {
    # #     "number": 0,
    # #     "code": "TE200",
    # #     "message": "SUCCESS",
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
            difference = len(content) - len(headers)
            

        for j in range(0, len(content)):
            dictionary[headers[j]].append(content[j])

        dictionary["CODE"].append(data[i]['code'])
        dictionary["MESSAGE"].append(data[i]['message'])
    
    # print(dictionary)
    
    return dictionary


def get_mz_dict(dataset):
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
    env = utils.select_env()

    fileName = input("Type in the file name ('file' column in orders page): ")
    token = input("Paste the Authentication token: ")
    requestId = input("Type in the requestId (requestFile?): ")

    # env =  "PROD"
    # fileName = "Staples_8764_ORDERDET_20230902_PROD_US0436373"
    # requestId = "ad2a170b-d98e-46f7-8eda-486a2970a507"
    
    # token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdXRob3JpemF0aW9uIjp7Imdyb3VwcyI6WyJTdGFwbGVzIiwiU3RhcGxlcyBNaWxlVmlzaW9uIl0sInJvbGVzIjpbIk1pbGVWaXNpb25fVXNlciJdLCJwZXJtaXNzaW9ucyI6W119LCJvcmdhbml6YXRpb24iOnsib3JnTmFtZSI6IjIyNTU1ZTBkLWYyZGItNDQ1YS04ZjNhLTViMzBlMmNmNDNiMiIsIm9yZ0lkIjoiM2M4OTdlODQtMzk1Ny00OTU4LWI1NGQtZDAyYzAxYjE0ZjE1IiwiQWxhYm8iOnsib3JnTmFtZSI6IjIyNTU1ZTBkLWYyZGItNDQ1YS04ZjNhLTViMzBlMmNmNDNiMiIsIm9yZ0lkIjoiM2M4OTdlODQtMzk1Ny00OTU4LWI1NGQtZDAyYzAxYjE0ZjE1In19LCJvYmplY3RzIjp7ImRyaXZlcklkIjoiYmE1NWU0M2EtMzg4ZC00NWYwLWI0NjgtYzk2ZDc4N2JhNzk5In0sImlzcyI6Imh0dHBzOi8vbWlsZXplcm8uYXV0aDAuY29tLyIsInN1YiI6ImF1dGgwfDVhMjlkNjk1N2E0NTA2NWU0ZDdhZTNkMSIsImF1ZCI6Ijd1bVVMbWxDVEpyM3NPbno1aXdwbkNYblhjNUxlMUxDIiwiaWF0IjoxNjkzOTI5NTY2LCJleHAiOjE2OTM5NjU1NjZ9.6NX4QLitq0aZvYnJ8Wo4Eci7zZXkMUiDuH-tsjWo1us"

    original_data = get_original_data(env, requestId, token)

    original_dict = get_original_dict(original_data)
    original_df = pandas.DataFrame(data=original_dict)

    parentId = input("Type in the parentId (request?): ")
    # parentId = "8e6eefcf-5f2a-4024-bd77-eb9399a7c5f5"

    mz_data = get_mz_data(env, parentId, token)
    mz_dict = get_mz_dict(mz_data)
    mz_df = pandas.DataFrame(data=mz_dict)

    print("Saving original file...")
    original_df.to_csv(f"Original {fileName}.csv", index=False)

    print("Saving MZ file...")
    mz_df.to_csv(f"MZ {fileName}.csv", index=False)

    print("Finishing script...")


main()
