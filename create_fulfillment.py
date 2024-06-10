import requests, json, pprint

pp = pprint.PrettyPrinter(indent=2)

# post
create_fs_url = "http://qilin.prod.milezero.com/qilin-war/api/fulfillmentservices/3f7539c3-ebbb-4d97-ac9f-bc66862c6ab8"

# post
create_fsg_url = "http://qilin.prod.milezero.com/qilin-war/api/fulfillmentservicegroup/3f7539c3-ebbb-4d97-ac9f-bc66862c6ab8"

# attach_fs_url -- 0 is groupId of fsg 1 is serviceId of fs
# post
attach_fs_url = "http://qilin.prod.milezero.com/qilin-war/api/fulfillmentservicegroup/3f7539c3-ebbb-4d97-ac9f-bc66862c6ab8/{0}/{1}?priority=1"

# post
create_pull_url = "http://qilin.prod.milezero.com/qilin-war/api/pulls/3f7539c3-ebbb-4d97-ac9f-bc66862c6ab8"

headers = {'content-type': 'application/json'}

fs_template = {
      "mzServiceId": "01ef1451-43cd-47a6-badf-2b32a80c4822",
      "serviceName": "",
      "strategy": "BATCH",
      "provider": {
        "providerId": "28c15814-d6b9-4a44-adb6-ea7149f57a0e",
        "providerName": "shoprite",
        "providerService": "NXT"
      },
      "isMZManaged": True,
      "fleetId": "",
      "regionId": "adf00699-c3fc-4046-a8ce-8903b72605e9",
      "currency": "USD",
      "fulfillmentScheduleMetadata": {
        "deliveryWindowOpen": "08:00",
        "deliveryWindowClose": "19:00",
        "criticalEntryTime": "23:59",
        "processingDays": [
          "TUESDAY",
          "THURSDAY",
          "MONDAY",
          "WEDNESDAY",
          "SUNDAY",
          "SATURDAY",
          "FRIDAY"
        ]
      },
      "fulfillmentCharge": {
        "ratePerPackage": 0,
        "count": 0,
        "overageRatePerPackage": 0
      },
      "fulfillmentRestrictions": {
        "volumeCountCap": 0,
        "valueCap": 0,
        "codCap": 5000,
        "currency": "USD",
        "dimWeightRestrictions": {
          "height": 0,
          "width": 0,
          "length": 0,
          "weight": 0,
          "dimensionUnits": "cm"
        },
        "deliveryCapabilities": {
          "commercial": True,
          "residential": True,
          "rural": True
        }
      },
      "disabled": False,
      "handlingServices": [
        {
          "mzServiceId": "365e3c42-f397-4e7d-bc74-6085cad55303",
          "properties": {
            "ACCEPT_COD_CASH": "true",
            "REQUIRE_SIGNATURE": "true",
            "ACCEPT_COD_CARD": "true",
            "ACCEPT_HAZMAT": "false"
          }
        },
        {
          "mzServiceId": "365e3c42-f397-4e7d-bc74-6085cad55303",
          "properties": {
            "ACCEPT_COD_CASH": "false",
            "REQUIRE_SIGNATURE": "true",
            "ACCEPT_COD_CARD": "false",
            "ACCEPT_HAZMAT": "false"
          }
        },
        {
          "mzServiceId": "6084dad5-ac0d-4025-9c74-95367b6c3b50",
          "properties": {
            "ACCEPT_COD_CASH": "false",
            "REQUIRE_SIGNATURE": "false",
            "ACCEPT_COD_CARD": "false",
            "ACCEPT_HAZMAT": "false"
          }
        }
      ]
    }

fsg_template = {
      "offerId": "",
      "groupName": "",
      "strategy": "BATCH",
      "facilityId": "",
      "isPullRequired": True,
      "disabled": False,
      "requiredHandlingServices": {},
      "fulfillmentServices": []
    }


pull_template = {
  "fulfillmentServiceGroupId": "",
  "startTime": "08:00",
  "endTime": "06:00",
  "processingDays": [
    "TUESDAY",
    "THURSDAY",
    "MONDAY",
    "WEDNESDAY",
    "SATURDAY",
    "SUNDAY",
    "FRIDAY"
  ],
  "timeZone": "America/New_York",
  "description": "",
  "active": True
}

fulfillment_hubs = [
    {
        "fleetId": "97ed6c53-a6ae-4be6-8445-ea01cb906f99",
        "hubId": "f89af170-a580-413d-af2e-7a913b1b7ab9",
        "windows": [
            {
                "serviceName": "shoprite NXT 136 9AM",
                "offerId": "ac20139f-9618-479e-8464-fa089022e57c"
            },
            {
                "serviceName": "shoprite NXT 136 10AM",
                "offerId": "a634feac-8fdd-406a-9b16-555fc8ec7222"
            },
            {
                "serviceName": "shoprite NXT 136 11AM",
                "offerId": "1c736919-bd1e-4436-81e1-e74aa218fb3b"
            },
            {
                "serviceName": "shoprite NXT 136 12PM",
                "offerId": "b3485977-f34a-4837-97da-f6d1d4e96ea2"
            },
            {
                "serviceName": "shoprite NXT 136 1PM",
                "offerId": "5e7ac44b-ce3f-4b54-9b88-64c0c6de4997"
            },
            {
                "serviceName": "shoprite NXT 136 2PM",
                "offerId": "f15b3cc3-2076-40c1-b34c-51953dbb60a9"
            },
            {
                "serviceName": "shoprite NXT 136 3PM",
                "offerId": "ddc538b2-4d9a-4d60-b36b-3ece786873db"
            },
            {
                "serviceName": "shoprite NXT 136 4PM",
                "offerId": "87ba69f4-865a-4486-9e26-d4c388b424b3"
            },
            {
                "serviceName": "shoprite NXT 136 5PM",
                "offerId": "771352ef-4979-4ebb-bb63-db8125a00806"
            }
        ]
    }
]


def post_fs():
    # pp.pprint(fs_template)
    response = requests.post(url=create_fs_url, data=json.dumps(fs_template), headers=headers)
    if response.status_code == 200:
        print(fs_template["serviceName"])
        print("Service created")
        fs = response.json()["fulfillmentServiceId"]
        return fs
    else:
        print("Error creating fulfillment service")
        print(fs_template["serviceName"])
        quit()


def post_fsg():
    response = requests.post(url=create_fsg_url, data=json.dumps(fsg_template), headers=headers)
    if response.status_code == 200:
        print(fsg_template["groupName"])
        print("Service Group created")
        fsg = response.json()["groupId"]
        return fsg
    else:
        print("Error creating fulfillment service group")
        print(fsg_template["groupName"])
        quit()

def attach_fs(group, service):
    url = attach_fs_url.format(group, service)
    response = requests.post(url=url, headers=headers)
    if response.status_code == 204:
        print("Service attached to group")
        return
    else:
        print("Error attaching service to group")
        print(group)
        print(service)
        quit()

def create_pull():
    response = requests.post(url=create_pull_url, data=json.dumps(pull_template), headers=headers)
    if response.status_code == 200:
        print(pull_template["description"])
        print("Pull created")
        return
    else:
        print("Error creating pull")
        print(pull_template["description"])
        quit()


def create_fulfillment():
    for hub in fulfillment_hubs:
        fs_template["fleetId"] = hub["fleetId"]
        fsg_template["facilityId"] = hub["hubId"]
        for window in hub["windows"]:
            fs_template["serviceName"] = window["serviceName"]
            fs_id = post_fs()
            fsg_template["offerId"] = window["offerId"]
            fsg_template["groupName"] = window["serviceName"]
            group_id = post_fsg()
            attach_fs(group_id, fs_id)
            pull_template["fulfillmentServiceGroupId"] = group_id
            pull_template["description"] = window["serviceName"] + " PULL"
            create_pull()

if __name__ == '__main__':
    create_fulfillment()


