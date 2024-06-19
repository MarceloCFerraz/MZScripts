import requests

import replanPackages

import replanPackages

# from datetime import datetime


def get_packages(page: int):
    url = f"https://milevision.milezero.com/mv/search/text?node=3903&start=2024-06-19&end=2024-06-19&lastUpdatedStart=2024-03-19&lastUpdatedEnd=2024-06-19&page={page}&text=0000000839&trackingNum=&orderNum=&barcode=&locationName=&recipient=&address=&city=&postal=&routeName=&driverId=&externalCustomerId=&referenceOne=&referenceTwo=&size=20"
    headers = {
        "accept": "application/json, text/javascript, */*; q=0.01",
        "accept-language": "en-US,en;q=0.9,pt;q=0.8",
        "authentication": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdXRob3JpemF0aW9uIjp7Imdyb3VwcyI6WyJTdGFwbGVzIiwiU3RhcGxlcyBNaWxlVmlzaW9uIl0sInJvbGVzIjpbIk1pbGVWaXNpb25fVXNlciJdLCJwZXJtaXNzaW9ucyI6W119LCJvcmdhbml6YXRpb24iOnsib3JnTmFtZSI6IjIyNTU1ZTBkLWYyZGItNDQ1YS04ZjNhLTViMzBlMmNmNDNiMiIsIm9yZ0lkIjoiM2M4OTdlODQtMzk1Ny00OTU4LWI1NGQtZDAyYzAxYjE0ZjE1IiwiQWxhYm8iOnsib3JnTmFtZSI6IjIyNTU1ZTBkLWYyZGItNDQ1YS04ZjNhLTViMzBlMmNmNDNiMiIsIm9yZ0lkIjoiM2M4OTdlODQtMzk1Ny00OTU4LWI1NGQtZDAyYzAxYjE0ZjE1In19LCJvYmplY3RzIjp7ImRyaXZlcklkIjoiYmE1NWU0M2EtMzg4ZC00NWYwLWI0NjgtYzk2ZDc4N2JhNzk5In0sImlzcyI6Imh0dHBzOi8vbWlsZXplcm8uYXV0aDAuY29tLyIsInN1YiI6ImF1dGgwfDVhMjlkNjk1N2E0NTA2NWU0ZDdhZTNkMSIsImF1ZCI6Ijd1bVVMbWxDVEpyM3NPbno1aXdwbkNYblhjNUxlMUxDIiwiaWF0IjoxNzE4ODEyMTIyLCJleHAiOjE3MTg4NDgxMjJ9.kLsMuh5Vnmg-c_f6V1HM6VAF61vh5oQFDwXUAUzDBRY",
        "newrelic": "eyJ2IjpbMCwxXSwiZCI6eyJ0eSI6IkJyb3dzZXIiLCJhYyI6IjExNjczNDciLCJhcCI6IjExMjAzMDExMzMiLCJpZCI6IjE0ODA2ZWMzM2FmZWMyZWEiLCJ0ciI6ImZkNmQzYzg3OThjZmZmNDVkNGNiYWYwYzVlMDM2ODc3IiwidGkiOjE3MTg4MTM2NjQ1NDQsInRrIjoiMTA2ODM0NiJ9fQ==",
        "priority": "u=1, i",
        "sec-ch-ua": '"Chromium";v="124", "Microsoft Edge";v="124", "Not-A.Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Linux"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "traceparent": "00-fd6d3c8798cfff45d4cbaf0c5e036877-14806ec33afec2ea-01",
        "tracestate": "1068346@nr=0-1-1167347-1120301133-14806ec33afec2ea----1718813664544",
        "x-newrelic-id": "VQcBVlVXDxABVFBRDgYHUVAE",
        "x-requested-with": "XMLHttpRequest",
        "cookie": "loginTokens=3c897e84-3957-4958-b54d-d02c01b14f15:eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJvcmdhbml6YXRpb24iOnsib3JnTmFtZSI6IjIyNTU1ZTBkLWYyZGItNDQ1YS04ZjNhLTViMzBlMmNmNDNiMiIsIm9yZ0lkIjoiM2M4OTdlODQtMzk1Ny00OTU4LWI1NGQtZDAyYzAxYjE0ZjE1IiwiQWxhYm8iOnsib3JnTmFtZSI6IjIyNTU1ZTBkLWYyZGItNDQ1YS04ZjNhLTViMzBlMmNmNDNiMiIsIm9yZ0lkIjoiM2M4OTdlODQtMzk1Ny00OTU4LWI1NGQtZDAyYzAxYjE0ZjE1In19LCJvYmplY3RzIjp7ImRyaXZlcklkIjoiNWExNTVjNTUtM2FhMC00MTNjLTgzYjgtN2Q1YjFhOGE3ZjMwIn0sImlzcyI6Imh0dHBzOi8vbWlsZXplcm8uYXV0aDAuY29tLyIsInN1YiI6ImF1dGgwfDY2NjczNWI5Y2MwNzBhY2U4ZTQyMDM0MCIsImF1ZCI6Ijd1bVVMbWxDVEpyM3NPbno1aXdwbkNYblhjNUxlMUxDIiwiaWF0IjoxNzE4Mjk4NDMyLCJleHAiOjE3MTgzMzQ0MzJ9.fR9dXFMUHmTOGa1gc9wel6LBhp0W6TeaEUyn__UlO7E; JSESSIONID=node0cl2cc8xdhbo751a44xhyqpth6851.node0; auth0.ssodata=%22{%5C%22lastUsedConnection%5C%22:%5C%22Username-Password-Authentication%5C%22%2C%5C%22lastUsedSub%5C%22:%5C%22auth0|5a29d6957a45065e4d7ae3d1%5C%22}%22; _ga=GA1.1.285174487.1714518859; _ga_7Z5PRZZTDR=GS1.1.1718753546.137.0.1718753546.0.0.0; _ga_8K23LKBCXP=GS1.1.1718753546.84.1.1718753546.0.0.0; mz_auth_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdXRob3JpemF0aW9uIjp7Imdyb3VwcyI6WyJTdGFwbGVzIiwiU3RhcGxlcyBNaWxlVmlzaW9uIl0sInJvbGVzIjpbIk1pbGVWaXNpb25fVXNlciJdLCJwZXJtaXNzaW9ucyI6W119LCJvcmdhbml6YXRpb24iOnsib3JnTmFtZSI6IjIyNTU1ZTBkLWYyZGItNDQ1YS04ZjNhLTViMzBlMmNmNDNiMiIsIm9yZ0lkIjoiM2M4OTdlODQtMzk1Ny00OTU4LWI1NGQtZDAyYzAxYjE0ZjE1IiwiQWxhYm8iOnsib3JnTmFtZSI6IjIyNTU1ZTBkLWYyZGItNDQ1YS04ZjNhLTViMzBlMmNmNDNiMiIsIm9yZ0lkIjoiM2M4OTdlODQtMzk1Ny00OTU4LWI1NGQtZDAyYzAxYjE0ZjE1In19LCJvYmplY3RzIjp7ImRyaXZlcklkIjoiYmE1NWU0M2EtMzg4ZC00NWYwLWI0NjgtYzk2ZDc4N2JhNzk5In0sImlzcyI6Imh0dHBzOi8vbWlsZXplcm8uYXV0aDAuY29tLyIsInN1YiI6ImF1dGgwfDVhMjlkNjk1N2E0NTA2NWU0ZDdhZTNkMSIsImF1ZCI6Ijd1bVVMbWxDVEpyM3NPbno1aXdwbkNYblhjNUxlMUxDIiwiaWF0IjoxNzE4ODEyMTIyLCJleHAiOjE3MTg4NDgxMjJ9.kLsMuh5Vnmg-c_f6V1HM6VAF61vh5oQFDwXUAUzDBRY",
        "Referer": "https://milevision.milezero.com/mv/partner.jsp?node=3903&t=1718813649678",
        "Referrer-Policy": "strict-origin-when-cross-origin",
    }

    response = requests.get(url, headers=headers)
    return response


if __name__ == "__main__":
    pids = set()
    page = 1

    while True:
        old_len = len(pids)

        print("Page: ", page)
        print("Packages: ", old_len)
        response = get_packages(page)
        try:
            packages = response.json()["packages"]
            if not packages or len(packages) == 0:
                print(f"Page {page} is empty")
                break
        except Exception:
            print(f"Page {page} is empty")
            break

        for package in packages:
            # print(datetime.fromtimestamp(package["deliveryTimeWindow"]["start"]))
            # print(datetime.fromtimestamp(package["deliveryTimeWindow"]["end"]))
            pid = package["packageId"]
            pids.add(pid)

        if len(pids) == old_len:
            break

        page += 1

    print(f"Total packages: {len(pids)}")
    print(pids)

    print("Resubmitting packages")
    replanPackages.main(
        env="prod",
        orgId="3c897e84-3957-4958-b54d-d02c01b14f15",
        keys=list(pids),
        keyType="pi",
        next_delivery_date="2024-06-20",
    )
