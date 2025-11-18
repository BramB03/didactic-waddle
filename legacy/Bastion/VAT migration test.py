import requests, json, time, pytest, os, pprint
from datetime import datetime, timedelta, timezone
from pathlib import Path

def getReservationInformation(serviceId, count, startDate, endDate, clientToken, accessToken, client, url, headers):
    payload = {
        "ClientToken": clientToken,
        "AccessToken": accessToken,
        "Client": client,
        "ServiceIds": [
            serviceId
        ],
        "ScheduledStartUtc": {
            "StartUtc": startDate,
            "EndUtc": endDate
        },
        "States": [
            "Confirmed"
        ],
        "Limitation":{
            "Count":count
        }
    }
    response = requests.post(url + "reservations/getAll/2023-06-06", headers=headers, data=json.dumps(payload))
    if response.status_code != 200:
        print(json.dumps(payload))
        print("Reservations Get Response:", response.status_code, response.text)
    reservationdIds = []
    for item in response.json().get("Reservations", []):
        if item.get("Id") in processed_ids:
            continue
        reservationdIds.append(item.get("Id"))
    return reservationdIds

def getReservationNightData(reservationId, clientToken, accessToken, client, url, headers):
    payload = {
        "ClientToken": clientToken,
        "AccessToken": accessToken,
        "Client": client,
        "ServiceOrderIds": [
            reservationId
        ],
        "Types": [
            "SpaceOrder"
        ],        
        "AccountingStates": [
            "Open"
        ],
        "Limitation": {
            "Count": 100
        }
    }
    response = requests.post(url + "orderItems/getAll", headers=headers, data=json.dumps(payload))
    if response.status_code != 200:
        print("OrderItems Response:", response.status_code, response.text)
    nightsData = response.json().get("OrderItems", [])
    response = [
        {
            "ConsumedUtc": item.get("ConsumedUtc"),
            "GrossValue": item.get("Amount", {}).get("GrossValue")
        }
        for item in nightsData
        if item.get("Amount", {}).get("TaxValues", [{}])[0].get("Code") == oldVatCode
    ]
    return response

def updateReservationNightData(reservationId, payloadPrice, clientToken, accessToken, client, url, headers):
    payload = {
        "ClientToken": clientToken,
        "AccessToken": accessToken,
        "Client": client,
        "Reason": "Testing",
        "Reprice": True,
        "ApplyCancellationFee": False,
        "ReservationUpdates": [
            {
                "ReservationId": reservationId,
                "TimeUnitPrices": {
                    "Value": payloadPrice
                }
            }
        ]
    }
    response = requests.post(url + "reservations/update", headers=headers, data=json.dumps(payload))
    return response

utcBefore = datetime.now(timezone.utc)
# Generic config
# =====================================================
clientToken = os.getenv("DEMO_CLIENTTOKEN")
client = "Test"
url = "https://api.mews-demo.com/api/connector/v1/"
headers = {
    "Content-Type": "application/json"
}
endpointCounter = 0
totalValuebefore = 0
totalValueafter = 0
totalIncrease = 0
reservationCounter = 0
PROCESSED_FILE = Path("processed_ids.txt")
ERRORED_FILE = Path("errored_ids.txt")

# Property specific config
# =====================================================
accessToken = os.getenv("DAVID_ACCESSTOKEN")
serviceId = "5291ecd7-c75f-4281-bca0-ae94011b2f3a"

# Execution specific information
# =====================================================
reservationCount = 50
weekRange = 2
start = "2025-11-11T00:00:00Z"
oldVatCode = "NL-2019-R"

# Generic work
# =====================================================
if PROCESSED_FILE.exists():
    with open(PROCESSED_FILE, "r") as f:
        processed_ids = set(line.strip() for line in f if line.strip())
else:
    processed_ids = set()

if ERRORED_FILE.exists():
    with open(ERRORED_FILE, "r") as f:
        errored_ids = set(line.strip() for line in f if line.strip())
else:
    errored_ids = set()


startUtc = datetime.fromisoformat(start.replace("Z", "+00:00"))
for length in range(weekRange):
    print("Processing week starting at:", startUtc.isoformat())
    endUtc = startUtc + timedelta(days=7)
    reservationsIds = getReservationInformation(
        serviceId, 
        reservationCount, 
        startUtc.isoformat().replace("+00:00", "Z"), 
        endUtc.isoformat().replace("+00:00", "Z"), 
        clientToken, 
        accessToken, 
        client, 
        url, 
        headers
    )
    if not reservationsIds:
        print("No reservations found for this period.")
        startUtc = endUtc
        continue
    endpointCounter +=1
    count = 0
    #Per reservering of in groepen? Start per reservering.
    for reservationId in reservationsIds:
        nightsData = getReservationNightData(
            reservationId, 
            clientToken, 
            accessToken, 
            client, 
            url, 
            headers
        )

        endpointCounter +=1
        count += 1
        if count>reservationCount:
            print("Stopping after reservationCount for testing purposes.")
            break
        data_sorted = sorted(
            nightsData,
            key=lambda x: datetime.fromisoformat(x["ConsumedUtc"].replace("Z", "+00:00"))
        )
        for i, item in enumerate(data_sorted):
            item["Index"] = i
            totalValuebefore += item["GrossValue"]
            item["GrossValue"] = round(item["GrossValue"] * 1.12, 2)  # Example VAT increase of 12%
            totalValueafter += item["GrossValue"]
            item.pop("ConsumedUtc", None)

        payloadPrice = []
        for item in data_sorted:
            mini_payload = {
                "Index": item["Index"],
                "Amount": {
                "Currency": "EUR",
                "GrossValue": item["GrossValue"],
                "TaxCodes": [
                    "NL-2019-S"
                ]
                }
            }
            payloadPrice.append(mini_payload)

        update_response = updateReservationNightData(
            reservationId, 
            payloadPrice, 
            clientToken, 
            accessToken, 
            client, 
            url, 
            headers
        )
        reservationCounter += 1
        endpointCounter +=1
        if update_response.status_code == 200:
            print("Successfully updated reservation:", reservationId)
            processed_ids.add(reservationId)
        else:
            print("Failed to update reservation:", reservationId, "Status Code:", update_response.status_code)
            errored_ids.add(reservationId)
            break

    startUtc = endUtc

with open(PROCESSED_FILE, "w") as f:
    for sid in processed_ids:
        f.write(sid + "\n")
with open(ERRORED_FILE, "w") as f:
    for sid in errored_ids:
        f.write(sid + "\n")

utcAfter = datetime.now(timezone.utc)
timeDiff = utcAfter - utcBefore
print(f"⏱️ Tijd genomen voor uitvoering: {timeDiff}.")
count = len(processed_ids)  # gebruik count als variabelenaam
print(f"✅ Klaar. {count} ID's opgeslagen in {PROCESSED_FILE}.")
print("Total reservations processed:", reservationCounter)
print("Total calls used:", endpointCounter)
print("Total value before VAT update:", totalValuebefore)
print("Total value after VAT update:", totalValueafter)
print("Total increase in value:", totalValueafter - totalValuebefore)
print("Percentage increase:", round(((totalValueafter - totalValuebefore) / totalValuebefore) * 100, 2), "%")