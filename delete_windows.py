import requests

data = {
    "50b5ba06-1a36-4707-b3f8-e4c6d54dfb5b": {
        "group": "e1739102-1cfc-4aba-9a92-b9bc51444fd5",
        "service": "6017302b-b1fb-41bc-b406-053e24a7fdf8",
        "pull": "4f87f6ef-98a8-49b7-b2e5-cae23fe9e54e",
    },
    "771352ef-4979-4ebb-bb63-db8125a00806": {
        "group": "fdaa1f50-0013-41b1-8f42-38032f65f42f",
        "service": "9d9b9380-a286-44b0-a55f-f7d90267e825",
        "pull": "d419098f-f76b-4944-845b-92f8ef634f39",
    },
    "ac20139f-9618-479e-8464-fa089022e57c": {
        "group": "e05ffac4-a5ce-4fef-9d7e-c15b7e98cca5",
        "service": "339348df-5036-472a-b7e7-3f7103a74e98",
        "pull": "32de157c-be5e-41c2-ac0b-8fc4a478d0be",
    },
    "a634feac-8fdd-406a-9b16-555fc8ec7222": {
        "group": "bcfcdf6f-ec5b-408b-9113-2d16cdbb5949",
        "service": "95511920-efa2-4c08-9f3b-73d7a47c59ef",
        "pull": "ed6287ec-c1ae-4002-a1a8-46f8a73333b2",
    },
    "1c736919-bd1e-4436-81e1-e74aa218fb3b": {
        "group": "8d692b08-a8c8-41b2-933a-1c741767cd2d",
        "service": "f6754d34-692d-4037-ada9-0bb1ff3b310b",
        "pull": "d42634d0-90c4-4155-9f79-90444b561a64",
    },
    "5e7ac44b-ce3f-4b54-9b88-64c0c6de4997": {
        "group": "7f1a7878-7c0f-4c57-8691-85e79c719c1a",
        "service": "b26b322e-357f-4ca5-a98f-442d5349c25b",
        "pull": "2e1858f2-4023-4b5c-b90e-204eb45a2f13",
    },
    "87ba69f4-865a-4486-9e26-d4c388b424b3": {
        "group": "a5a186ab-29a8-46ab-bdcf-e8e531d0f4e8",
        "service": "4d7cd9b0-5d45-4fed-bd27-d2f7052fce7f",
        "pull": "b0199cfd-906a-46fa-aa14-73841be5e899",
    },
    "b3485977-f34a-4837-97da-f6d1d4e96ea2": {
        "group": "f86f057a-3257-44ec-ad38-d616036ab62f",
        "service": "2c9de997-88d1-49e9-bfdc-b1a747a32677",
        "pull": "1e0f7001-9e3f-47c4-a9b5-c06d3b8e6821",
    },
    "f15b3cc3-2076-40c1-b34c-51953dbb60a9": {
        "group": "3cd519e2-2c6a-4fcf-bc20-49106d1ec5ed",
        "service": "0a29e557-6f03-46aa-ad58-7fb365dcce56",
        "pull": "470cf62e-1380-43c4-92a4-19d4b4efc69a",
    },
    "ddc538b2-4d9a-4d60-b36b-3ece786873db": {
        "group": "bcfcdf6f-ec5b-408b-9113-2d16cdbb5949",
        "service": "95511920-efa2-4c08-9f3b-73d7a47c59ef",
        "pull": "d2964a47-cb9f-4828-a7d3-5103e632dcd1",
    },
}

hub_id = "f96ad188-e56b-4aea-8969-c1b9f870f200"
org_id = "3f7539c3-ebbb-4d97-ac9f-bc66862c6ab8"

for offer in data.keys():
    fsg = data[offer]["group"]
    fs = data[offer]["service"]
    pull = data[offer]["pull"]

    # un-attach fulfillment serviceId from group endpoint: http://qilin.prod.milezero.com/qilin-war/#!/fulfillment_service_group/removeServicesFromFulfillmentServiceGroup
    print(f"Detaching {fs} from {fsg}")
    url = f"https://qilin.prod.milezero.com/qilin-war/api/fulfillmentservicegroup/{org_id}/{fsg}/{fs}"
    response = requests.delete(url=url)
    print(response.status_code)
    print(response.text if response.status_code >= 400 else "")

    # delete fulfillment serviceId endpoint: http://qilin.prod.milezero.com/qilin-war/#!/fulfillment_service/deleteFulfillmentService
    print(f"Deleting Service {fs}")
    url = f"https://qilin.prod.milezero.com/qilin-war/api/fulfillmentservices/{org_id}/{fs}"
    response = requests.delete(url=url)
    print(response.status_code)
    print(response.text if response.status_code >= 400 else "")

    # delete pullId endpoint: http://qilin.prod.milezero.com/qilin-war/#!/pulls/deletePull
    print(f"Deleting Pull {pull}")
    url = f"https://qilin.prod.milezero.com/qilin-war/api/pulls/{org_id}/{pull}"
    response = requests.delete(url=url)
    print(response.status_code)
    print(response.text if response.status_code >= 400 else "")

    # delete fulfillment service group endpoint: http://qilin.prod.milezero.com/qilin-war/#!/fulfillment_service_group/deleteFulfillmentServiceGroup
    print(f"Deleting Service Group {fsg}")
    url = f"https://qilin.prod.milezero.com/qilin-war/api/fulfillmentservicegroup/{org_id}/{fsg}"
    response = requests.delete(url=url)
    print(response.status_code)
    print(response.text if response.status_code >= 400 else "")

    print("========================")
