import requests, json, time, pytest, os, pprint
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Rule Examples
# =====================================================

'''
Booking.com vanaf 10 november 0.00 uur.
Logica:
if travelagencyId == "" and createdUtc before November 10th 00:00:00Z:
'''

# Execution specific information
# =====================================================
reservationCount = 3                # Max aantal reserveringen om te verwerken. Inkorten voor testdoeleinden.
iterationRange = 10                 # Aantal iteraties om te verwerken vanaf startdatum.
dayRange = 1                        # Aantal dagen per iteratie. 
start = "2026-01-01T00:00:00Z"      # Startdatum in ISO formaat.
priceIncrease = 0.11009174311927    # Percentage prijsverhoging, bv 0.1 = 10%
url = "https://api.mews-demo.com/api/connector/v1/" # or "https://api.mews.com/api/connector/v1/", remove -demo for production.

# Property specific config
# =====================================================

if url == "https://api.mews-demo.com/api/connector/v1/":
    print("⚠️ Running against DEMO environment. Make sure this is intended. If not, waiting 15 seconds to abort...")
    time.sleep(15)
    clientToken = "3802A256E16D488796E5B20200B989CE-DD4A90FED8F9CD53DAD2841BCBA407C"
    accessToken = "7500F90A29B442E0BFE3B24C00989464-FAC676C1542EDE861E5891A135E1B38"
    serviceId = "065aba6e-2533-4985-9aef-b241009333a8"

elif url == "https://api.mews.com/api/connector/v1/":
    print("⚠️ Running against LIVE environment. Make sure this is intended. If not, waiting 15 seconds to abort...")
    time.sleep(15)
    clientToken = "E0D439EE522F44368DC78E1BFB03710C-D24FB11DBE31D4621C4817E028D9E1D"
    accessToken = "8BD94EED3ACA4C218CAFB39B00BDF407-259ED45886DCC70D6703A3F07041780"
    serviceId = "023362ca-b557-4655-b228-afc7009cfe0a"



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
            "Count":1000
        }
    }
    response = requests.post(url + "reservations/getAll/2023-06-06", headers=headers, data=json.dumps(payload))
    if response.status_code != 200:
        print(json.dumps(payload))
        print("Reservations Get Response:", response.status_code, response.text)
    reservationdIds = []
    bookingCutoff = datetime(2025, 11, 9, 23, 0, 0, tzinfo=timezone.utc)
    connectorCutoff = datetime(2025, 11, 12, 23, 0, 0, tzinfo=timezone.utc)
    for item in response.json().get("Reservations", []):
        createdStr = datetime.fromisoformat(item.get("CreatedUtc").replace("Z", "+00:00"))
        
        if item.get("TravelAgencyId") == "d988b779-31e5-4716-b21b-b24100a3a684" and createdStr > bookingCutoff:
            skippedReservations.append((item.get("Id"), "Booking.com pre-Nov 10"))
            skipped_f.write(f"{item.get("Id")} - Booking.com post-Nov 10\n")
            skipped_f.flush()
            continue
        elif item.get("Id") in processed_ids:
            skippedReservations.append((item.get("Id"), "Already processed"))
            skipped_f.write(f"{item.get("Id")} - Already processed\n")
            skipped_f.flush()
            continue
        else:
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
            "GrossValue": item.get("Amount", {}).get("GrossValue"),
            "TaxCode": item.get("Amount", {}).get("TaxValues", [])[0].get("Code")
        }
        for item in nightsData
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

client = "Test"
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
SKIPPED_FILE = Path("skipped_ids.txt")

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

if SKIPPED_FILE.exists():
    with open(SKIPPED_FILE, "r") as f:
        skipped_ids = set(line.strip() for line in f if line.strip())
else:
    skipped_ids = set()

startUtc = datetime.fromisoformat(start.replace("Z", "+00:00"))
skippedReservations = []
with open(PROCESSED_FILE, "a") as processed_f, \
     open(ERRORED_FILE, "a") as errored_f, \
     open(SKIPPED_FILE, "a") as skipped_f:

    for length in range(iterationRange):
        print("Processing week starting at:", startUtc.isoformat())
        endUtc = startUtc + timedelta(days=dayRange)
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
        endpointCounter += 1
        count = 0

        # Per reservation
        for reservationId in reservationsIds:
            # Just in case, skip if already processed in this run or previous
            if reservationId in processed_ids:
                continue

            nightsData = getReservationNightData(
                reservationId, 
                clientToken, 
                accessToken, 
                client, 
                url, 
                headers
            )

            endpointCounter += 1
            count += 1
            if count > reservationCount:
                print("Stopping after reservationCount for testing purposes.")
                break

            data_sorted = sorted(
                nightsData,
                key=lambda x: datetime.fromisoformat(x["ConsumedUtc"].replace("Z", "+00:00"))
            )
            for i, item in enumerate(data_sorted):
                item["Index"] = i
                totalValuebefore += item["GrossValue"]
                item["GrossValue"] = round(item["GrossValue"] * (1 + priceIncrease), 2)
                item ["increasedBy"] = round(item["GrossValue"] * priceIncrease, 2)
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
                            item["TaxCode"]
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
            endpointCounter += 1

            if update_response.status_code == 200:
                print("Successfully updated reservation:", reservationId)
                if reservationId not in processed_ids:
                    processed_ids.add(reservationId)
                    increase_total = sum(item["increasedBy"] for item in data_sorted)
                    processed_f.write(f"{reservationId}, €{increase_total}\n")
                    processed_f.flush()
            else:
                print("Failed to update reservation:", reservationId, "Status Code:", update_response.status_code)
                if reservationId not in errored_ids:
                    errored_ids.add(reservationId)
                    errored_f.write(reservationId + "\n")
                    errored_f.flush()
                # optional: also log to skipped file with reason
                reason = f"Update failed with status {update_response.status_code}"
                skippedReservations.append((reservationId, reason))
                skipped_f.write(f"{reservationId} - {reason}\n")
                skipped_f.flush()
                break

        startUtc = endUtc

utcAfter = datetime.now(timezone.utc)
timeDiff = utcAfter - utcBefore
print(f"⏱️ Tijd genomen voor uitvoering: {timeDiff}.")
count = len(processed_ids)
print(f"✅ Klaar. {count} ID's opgeslagen in {PROCESSED_FILE}.")
print("Total reservations processed:", reservationCounter)
print("Total calls used:", endpointCounter)
print("Total value before VAT update:", totalValuebefore)
print("Total value after VAT update:", totalValueafter)
print("Total increase in value:", totalValueafter - totalValuebefore)
print("Percentage increase:", round(((totalValueafter - totalValuebefore) / totalValuebefore) * 100, 2), "%")