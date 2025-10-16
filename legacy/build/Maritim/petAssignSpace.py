import requests
import json, os
import random
import time

start_time = time.time()

# Variables from input data
'''
spaceId = input_data.get('spaceId', '')
spaceCatId = input_data.get('spaceCatId', '')
startUtc = input_data.get('startUtc', '')
endUtc = input_data.get('endUtc', '')
reservationId = input_data.get('reservationId', '')
'''
spaceId = "8ee42821-b753-4212-b4c4-b24300d8670b"
spaceCatId = "2f7397d9-f930-40bf-9f7d-b24300d866f6"
startUtc = "2025-04-07T13:00:00Z"
endUtc = "2025-04-09T10:00:00Z"
reservationId = "455803ba-4b8b-4e20-9357-b2b800e842e7"

#Get task time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
currentUtcTime = datetime.now(ZoneInfo("Europe/Berlin"))
utcInSixHours = currentUtcTime + timedelta(hours=6)
taskTime = utcInSixHours.strftime("%Y-%m-%dT%H:%M:%SZ")

URL = "https://api.mews-demo.com/api/connector/v1/"
headers = {
    "Content-Type": "application/json"
}

# Input data, to be expanded upon per property. Level 1 is space category, 2 is space id's.
data = {
    "2f7397d9-f930-40bf-9f7d-b24300d866f6": [
        "22918647-f99b-49bb-9e13-b24300d8670b",
        "ebda126f-89ec-4278-b07d-b24300d8670b",
        "6b3b25c0-0fdc-44be-b19d-b24300d8670b",
        "7b4de797-1709-4470-8317-b24300d8670b"
    ],
    "651e5235-ee33-4e55-bbf5-b24300d866f6": [
        "fb23d28a-f520-42d3-bb8e-b24300d8670b"
    ]
}

# Check if the space category exists in the data and if the space ID is in the corresponding list
#What should happen if customer booked space where no pets are alloweD?

if spaceCatId in data and spaceId in data[spaceCatId]:
    #Update reservation to lock into place
    payloadLock = {
        "ClientToken": os.getenv("DEMO_CLIENTTOKEN"),
        "AccessToken": os.getenv("MAR_DUSS_ACCESSTOKEN"),
        "Client": "Zapier",
        "Reason": "Pet Room Lock",
        "CheckOverbooking": False,
        "ReservationUpdates": [
            {
                "ReservationId": reservationId,
                "AssignedResourceLocked": {
                    "Value": "true"
                }
            }
        ]
    }
    payloadLockJson = json.dumps(payloadLock)
    responsePayloadLockJson = requests.post(URL + "reservations/update", data=payloadLockJson, headers=headers)
else:
    #Request space category availability for spaces.
    if spaceCatId not in data:
        payloadTask = {
            "ClientToken": os.getenv("DEMO_CLIENTTOKEN"),
            "AccessToken": os.getenv("MAR_DUSS_ACCESSTOKEN"),
            "Client": "Zapier",
            "Name": "Petroom not available",
            "Description": "Please review room assignment. Guest booked roomtype where pets are not allowed",
            "DeadlineUtc": taskTime,
            "ServiceOrderId": reservationId,
            "DepartmentId": None
        }
        payloadTaskJson = json.dumps(payloadTask)
        responsePayloadTaskJson = requests.post(URL + "tasks/add", data=payloadTaskJson, headers=headers)
    else:
        SpaceList = data[spaceCatId]
        payloadAssignedResource = {
            "ClientToken": os.getenv("DEMO_CLIENTTOKEN"),
            "AccessToken": os.getenv("MAR_DUSS_ACCESSTOKEN"),
            "Client": "Zapier",
            "AssignedResourceIds": SpaceList,
            "CollidingUtc": {
                "StartUtc": startUtc,
                "EndUtc": endUtc
            },
            "Limitation": {
                "Count": 500
            }
        }
        payloadAssignedResourceJson = json.dumps(payloadAssignedResource)
        responsePayloadAssignedResourceJson = requests.post(URL + "reservations/getAll/2023-06-06", data=payloadAssignedResourceJson, headers=headers)
        responseAssignedResourceIds = responsePayloadAssignedResourceJson.json()
        assignedResources = {}
        for reservation in responseAssignedResourceIds['Reservations']:
            resource_id = reservation['AssignedResourceId']
            locked = reservation['AssignedResourceLocked']
            if resource_id not in assignedResources:
                assignedResources[resource_id] = []
            assignedResources[resource_id].append(locked)
        assignedIds = set(assignedResources.keys())
        unassignedResources = [space_id for space_id in SpaceList if space_id not in assignedIds]
        assignedUnlockedResources = [
            resource_id for resource_id, locks in assignedResources.items()
            if all(lock == False for lock in locks)
        ]
        #Check if there are any unlocked resources
        unassignedResources = [resource for resource in SpaceList if resource not in assignedResources]
        if unassignedResources != []:
            payloadUpdateLock = {
                "ClientToken": os.getenv("DEMO_CLIENTTOKEN"),
                "AccessToken": os.getenv("MAR_DUSS_ACCESSTOKEN"),
                "Client": "Zapier",
                "Reason": "Pet Room Lock",
                "CheckOverbooking": False,
                "ReservationUpdates": [
                    {
                        "ReservationId": reservationId,
                        "AssignedResourceId": {
                            "Value": random.choice(unassignedResources)
                        }
                    }
                ]
            }
            payloadUpdateLockJson = json.dumps(payloadUpdateLock)
            time.sleep(3)
            responsePayloadUpdateLockJson = requests.post(URL + "reservations/update", data=payloadUpdateLockJson, headers=headers)
            payloadUpdateLock = {
                "ClientToken": os.getenv("DEMO_CLIENTTOKEN"),
                "AccessToken": os.getenv("MAR_DUSS_ACCESSTOKEN"),
                "Client": "Zapier",
                "Reason": "Pet Room Lock",
                "CheckOverbooking": False,
                "ReservationUpdates": [
                    {
                        "ReservationId": reservationId,
                        "AssignedResourceLocked": {
                            "Value": "true"
                        }
                    }
                ]
            }
            payloadUpdateLockJson = json.dumps(payloadUpdateLock)
            responsePayloadUpdateLockJson = requests.post(URL + "reservations/update", data=payloadUpdateLockJson, headers=headers)
        elif assignedUnlockedResources != []:
            payloadUpdateLock = {
                "ClientToken": os.getenv("DEMO_CLIENTTOKEN"),
                "AccessToken": os.getenv("MAR_DUSS_ACCESSTOKEN"),
                "Client": "Zapier",
                "Reason": "Pet Room Lock",
                "CheckOverbooking": False,
                "ReservationUpdates": [
                    {
                        "ReservationId": reservationId,
                        "AssignedResourceId": {
                            "Value": random.choice(assignedUnlockedResources)
                        }
                    }
                ]
            }
            payloadUpdateLockJson = json.dumps(payloadUpdateLock)
            responsePayloadUpdateLockJson = requests.post(URL + "reservations/update", data=payloadUpdateLockJson, headers=headers)
            time.sleep(3)
            payloadUpdateLock = {
                "ClientToken": os.getenv("DEMO_CLIENTTOKEN"),
                "AccessToken": os.getenv("MAR_DUSS_ACCESSTOKEN"),
                "Client": "Zapier",
                "Reason": "Pet Room Lock",
                "CheckOverbooking": False,
                "ReservationUpdates": [
                    {
                        "ReservationId": reservationId,
                        "AssignedResourceLocked": {
                            "Value": "true"
                        }
                    }
                ]
            }
            payloadUpdateLockJson = json.dumps(payloadUpdateLock)
            responsePayloadUpdateLockJson = requests.post(URL + "reservations/update", data=payloadUpdateLockJson, headers=headers)
        else:
            payloadTask = {
                "ClientToken": os.getenv("DEMO_CLIENTTOKEN"),
                "AccessToken": os.getenv("MAR_DUSS_ACCESSTOKEN"),
                "Client": "Zapier",
                "Name": "Petroom not available",
                "Description": "Please review room assignment. No pet room is available.",
                "DeadlineUtc": taskTime,
                "ServiceOrderId": reservationId,
                "DepartmentId": None
            }
            payloadTaskJson = json.dumps(payloadTask)
            responsePayloadTaskJson = requests.post(URL + "tasks/add", data=payloadTaskJson, headers=headers)

end_time = time.time()
execution_time = end_time - start_time
print(f"Execution time: {execution_time} seconds")        

