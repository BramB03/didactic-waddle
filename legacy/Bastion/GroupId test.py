import requests
import json
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from datetime import datetime, timedelta, timezone
import json, os
import xml.etree.ElementTree as ET
import requests
from zoneinfo import ZoneInfo

headers = {
    "Content-Type": "application/json"
}

clientToken = os.getenv("DEMO_CLIENTTOKEN")
accessToken = os.getenv("DAVID_ACCESSTOKEN")
client = "Test"
url = "https://api.mews-demo.com/api/connector/v1/"

payloadReservations = {
    "ClientToken": clientToken,
    "AccessToken": accessToken,
    "Client": client,
    "ServiceId": "5291ecd7-c75f-4281-bca0-ae94011b2f3a",
    "CheckRateApplicability": False,
    "Reservations": [
        {
        "Identifier": "1234",
        "State": "Inquired",
        "StartUtc": "2026-01-02T14:00:00Z",
        "EndUtc": "2026-01-03T10:00:00Z",
        "ReleasedUtc": "2026-01-01T10:00:00Z",
        "CustomerId": "d0f282bf-0e49-4ec9-85c9-b22f0091f896",
        "RequestedCategoryId": "01d9c47b-2dea-4e3f-b87e-ae94011b33bb",
        "RateId": "ae08e784-cb62-4922-b701-b2de008e6ea9",
        "Notes": "Test reservation",
        "TimeUnitPrices": [
            {
                "Index": 0,
                "Amount": {
                    "Currency": "EUR",
                    "GrossValue": 20,
                    "TaxCodes": [
                    "NL-2019-R"
                    ]
                }
            }
        ],
        "PersonCounts": [
            {
            "AgeCategoryId": "d7c8b49f-d7e6-4765-8398-ae94011b2f9c",
            "Count": 2
            }
        ]
        }
    ]
}

responseReservations = requests.post(url + "reservations/add", headers=headers, data=json.dumps(payloadReservations))
timeOne = datetime.now(tz=timezone.utc)
if responseReservations.status_code != 200:
    print("Reservations Response:", responseReservations.status_code, responseReservations.text)    
reservation_data = responseReservations.json()
reservation_id = reservation_data.get("Reservations", [{}])[0].get("Reservation").get("GroupId")
print("Extracted Reservation GroupId:", reservation_id)
payloadReservationsUpdate = {
    "ClientToken": clientToken,
    "AccessToken": accessToken,
    "Client": client,
    "ReservationGroupIds": [
        reservation_id
    ],
    "Limitation": {
        "Count": 10
    }
}

responseReservationsUpdate = requests.post(url + "reservations/getAll/2023-06-06", headers=headers, data=json.dumps(payloadReservationsUpdate))
timeTwo = datetime.now(tz=timezone.utc)
print("Reservations Update Response:", responseReservationsUpdate.status_code, responseReservationsUpdate.text)

responseTimeDiff = timeTwo - timeOne
print("Time difference between requests:", responseTimeDiff)