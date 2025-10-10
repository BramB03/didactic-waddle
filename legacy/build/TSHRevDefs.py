headers = {
"Content-Type": "application/json"
}
URL = "https://api.mews-demo.com/api/connector/v1/"


def enterpriseSelection():
    credentialOptions = [
        {
            "label": "The David AZ - Demo",
            "clientToken": "E0D439EE522F44368DC78E1BFB03710C-D24FB11DBE31D4621C4817E028D9E1D",
            "accessToken": "BEC33DAD4C57410C9E6DB09600C7FB9B-310471532A30162E5B6F0EB4F4AD2BF",
            "clientId": "prod_client_id"
        },
        {
            "label": "The David Westerpark - Demo",
            "clientToken": "E0D439EE522F44368DC78E1BFB03710C-D24FB11DBE31D4621C4817E028D9E1D",
            "accessToken": "1E338DE5B1574A7AA69CB14900944A81-9A9848C981545BF61055DB1219495DA",
            "serviceOneId": "78825e4d-c115-4954-9cfb-b12b008f0a0b",
            "serviceTwoId": "218a3e81-26a2-495c-88bb-b2fb00af5a67",
            "serviceThreeId": "12b84ca9-9103-429a-b38e-b2fb00af678c",
            "serviceTshId": "873a6387-a7f7-4dbc-ac87-b329008c571e",
            "clientId": "sandbox_client_id",
            "URL": "https://api.mews-demo.com/api/connector/v1/",
            "headers": headers
        }
    ]

    print("Select a credential set:")
    for idx, option in enumerate(credentialOptions, start=1):
        print(f"{idx}. {option['label']}")

    while True:
        try:
            choice = int(input("Enter number (1–{}): ".format(len(credentialOptions))))
            if 1 <= choice <= len(credentialOptions):
                selected = credentialOptions[choice - 1]
                break
            else:
                print("Invalid number. Try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    return {
        "ClientToken": selected.get("clientToken"),
        "AccessToken": selected.get("accessToken"),
        "Client": selected.get("clientId"),
        "ServiceOneId": selected.get("serviceOneId"),
        "ServiceTwoId": selected.get("serviceTwoId"),
        "ServiceThreeId": selected.get("serviceThreeId"),
        "ServiceTshId": selected.get("serviceTshId"),
        "URL": selected.get("URL"),
        "headers": selected.get("headers")
    }

def showMenu(credentials):
    options = [
        {"label": "Remove blocks", "action": removeBlocks},
        {"label": "Add blocks", "action": addBlocks},
    ]

    for idx, option in enumerate(options, start=1):
        print(f"{idx}. {option['label']}")

    while True:
        try:
            choice = int(input(f"Enter number (1–{len(options)}): "))
            if 1 <= choice <= len(options):
                selectedAction = options[choice - 1]["action"]
                selectedAction(credentials)
                break
            else:
                print("Invalid number. Try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def removeBlocks(credentials):
    import requests
    import json
    print("Removing resource blocks...")
    payload = {
        "ClientToken": credentials['ClientToken'],
        "AccessToken": credentials['AccessToken'],
        "CollidingUtc": {
            "StartUtc": "2025-06-01T00:00:00Z",
            "EndUtc": "2025-08-30T00:00:00Z"
        },
        "Extent": {
            "Inactive": False
        },
        "Limitation": {"Count": 100}
    }
    jsonPayload = requests.post(
        credentials['URL'] + "resourceBlocks/getAll",
        json=payload,
        headers=credentials['headers']
    )
    print("Status Code:", jsonPayload.status_code)
    resourceBlockIds = jsonPayload.json().get("ResourceBlocks", [])
    print("Resource Blocks:", resourceBlockIds)
    ids = []
    for resourceBlock in resourceBlockIds:
        id = resourceBlock.get("Id")
        ids.append(id)

    print("Removing...")

    payloadDelete = {
        "ClientToken": credentials['ClientToken'],
        "AccessToken": credentials['AccessToken'],
        "ResourceBlockIds": ids
    }
    jsonPayloadDelete = requests.post(
        credentials['URL'] + "resourceBlocks/delete",
        json=payloadDelete,
        headers=credentials['headers']
    )
    print("Delete Status Code:", jsonPayloadDelete.status_code)

def addBlocks(credentials):
    from datetime import datetime, timedelta
    resourceIds = [
        {'Id': '21dd95d1-0348-45e0-a0c4-b329008c3ba5', 'Name': '32'},
        {'Id': '1062398e-fd5f-47c1-9c3e-b329008c3ba5', 'Name': '25'},
        {'Id': '66fdbb26-8251-404b-85a1-b329008c3ba5', 'Name': '34'},
        {'Id': '9fb1ffec-5a6f-465c-8c69-b329008c3ba5', 'Name': '24'},
        {'Id': '1214e4a3-b875-4d59-845c-b329008c3ba5', 'Name': '35'},
        {'Id': '706e4efd-5a5e-43a9-9a12-b329008c3ba5', 'Name': '23'},
        {'Id': 'f0690c62-afaa-4646-b8ec-b329008c3ba5', 'Name': '31'},
        {'Id': '39df5e41-ac49-44fd-a57a-b329008c3ba5', 'Name': '22'},
        {'Id': '35560efe-7735-49be-90a6-b329008c3ba5', 'Name': '21'},
        {'Id': 'ed3b9972-1cbf-41ca-8db6-b329008c3ba5', 'Name': '33'}
        ]

    offSet = list(getUtcOffsetTimes("Europe/Amsterdam"))

    for i in range(0, 10):
        dataBlock = []
        for resource in resourceIds:
            data = {
                "ResourceId": resource['Id'],
                "StartUtc": offSet[0],
                "EndUtc": offSet[1],
                "Name": "Blocked",
                "Type": "OutOfOrder",
            }
            dataBlock.append(data)
                
        addResourceBlock(
            credentials['ClientToken'],
            credentials['AccessToken'],
            dataBlock
        )

        offSet[0] = (datetime.strptime(offSet[0], '%Y-%m-%dT%H:%M:%S.%fZ') + timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        offSet[1] = (datetime.strptime(offSet[1], '%Y-%m-%dT%H:%M:%S.%fZ') + timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    print(f"Added resource blocks...")

def getResourceIds(ClientToken, AccessToken, ServiceId):
    import requests
    import json

    payload = {
        "clientToken": ClientToken,
        "accessToken": AccessToken,
        "ServiceId": ServiceId,
        "Extent": {
            "Resources": True,
        },
        "Limitation": { "Count": 100 }
    }
    jsonPayload = json.dumps(payload)
    requestResourceIds = requests.post(URL + "resources/getAll", data=jsonPayload, headers=headers)
    resourceIds = []
    if requestResourceIds.status_code == 200:
        for id in requestResourceIds.json().get("Resources", []):
            name = id.get("Name")
            id = id.get("Id")
            resourceIds.append({
                "Name": name,
                "Id": id
            })
        return resourceIds
    else:
        print("Error fetching resource IDs:", requestResourceIds.status_code, requestResourceIds.text)
        return None

def getUtcOffsetTimes(timezone):
    from datetime import datetime, timedelta
    import pytz

    utc_now = datetime.now(pytz.utc)
    local_tz = pytz.timezone(timezone)  # Adjust to your local timezone
    local_now = utc_now.astimezone(local_tz)
    utc_offset = local_now.utcoffset().total_seconds() / 3600  # Convert to hours
    utcStart = utc_now.replace(hour=16, minute=0, second=0) - timedelta(hours=utc_offset)
    utcEnd = utc_now.replace(hour=10, minute=0, second=0) - timedelta(hours=utc_offset) + timedelta(days=1)
    utcStart = utcStart.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    utcEnd = utcEnd.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    return utcStart, utcEnd

def addResourceBlock(ClientToken, AccessToken, Block):
    import requests
    import json
    print("Adding block...")
    payload = {
        "ClientToken": ClientToken,
        "AccessToken": AccessToken,
        "ResourceBlocks": Block
    }
    jsonPayload = json.dumps(payload)
    requestAddResourceBlock = requests.post(URL + "resourceBlocks/add", data=jsonPayload, headers=headers)
    if requestAddResourceBlock.status_code == 200:
        print("Resource block added successfully.")
    else:
        print("Error adding resource block:", requestAddResourceBlock.status_code, requestAddResourceBlock.text)
    