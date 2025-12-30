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
reservationCount = 1000            # Max aantal reserveringen om te verwerken. Inkorten voor testdoeleinden.
iterationRange = 10                # Aantal iteraties om te verwerken vanaf startdatum.
dayRange = 1                        # Aantal dagen per iteratie. 
start = "2026-01-02T00:00:00Z"      # Startdatum in ISO formaat.
priceIncrease = 0.11009174311927    # Percentage prijsverhoging, bv 0.1 = 10%
url = "https://api.mews.com/api/connector/v1/" # or "https://api.mews.com/api/connector/v1/", remove -demo for production.

expedialistForCutoff = [
    "8bd765c2-22d4-4825-a613-b14100b2f3bd",
    "61269c47-ccff-4622-9fb6-b1120028bfea",
    "d2aa518b-e6ba-4af9-916b-b111000b2df1",
    "9331bb1a-53b3-4ec1-a586-ae2200cd9e8c",
    "9c3e279a-888d-4065-9b61-b0bc00d09b5a",
    "d8b9caff-989d-435c-b592-b0bd01796f2e",
    "1535be07-8ab8-4188-8ea0-b0f4009a7528",
    "87317a85-22b3-47be-9567-b0be0027c8a2",
    "f71658ca-def5-4ffa-adb3-b0c9012ba92b",
    "3eb116c5-e337-4213-81f2-b0cd01709e4f",
    "1035e423-65d0-47e8-a2f3-b0be00e97924",
    "e6645512-f202-4652-afe6-b0be015f3377",
    "b0983e68-2604-441f-abd9-b0c001258605",
    "c5eef547-66f0-4b93-8806-b10701853ed5",
    "f2fa3530-51e5-4789-94ee-b0bd01376b9f",

] # Enter all Expedia travel agency and partner company IDs here.
expediaCutoff = datetime(2025, 11, 30, 23, 0, 0, tzinfo=timezone.utc)
expediaCollectskip = [
    "61269c47-ccff-4622-9fb6-b1120028bfea",  # a-orbitz
    "9c3e279a-888d-4065-9b61-b0bc00d09b5a",  # A-expedia
    "1535be07-8ab8-4188-8ea0-b0f4009a7528",  # A-egencia / a-egencia
    "87317a85-22b3-47be-9567-b0be0027c8a2",  # a-hotel
    "f71658ca-def5-4ffa-adb3-b0c9012ba92b",  # a-expedia affiliates
    "3eb116c5-e337-4213-81f2-b0cd01709e4f",  # a-travelocity
    "c5eef547-66f0-4b93-8806-b10701853ed5",  # A-american
    "87317a85-22b3-47be-9567-b0be0027c8a2",
    "bf17e3ac-8d96-4c59-b654-ae45011688f0",
    "4a1324ca-f7e8-48cd-b0af-b30c00cf4a86",
    "00c09d9e-efc4-4b23-ae6e-ae2200cdad5b"
] # Enter all Expedia Collect travel agency and partner company IDs here as they require a different solution.

segmentId = ["6f72e9f1-b13f-4974-9820-ae1b0095bb4b", "871727d7-841e-49d6-aeeb-b2e400d4eec6", "0baf126f-61cc-451f-8994-b2a000aed974"]

bookingComId = "cd8fa7b5-760b-4f7e-86ea-ae2200cd8c99"
bookingCutoff = datetime(2025, 11, 9, 23, 0, 0, tzinfo=timezone.utc)

# Property specific config
# =====================================================

if url == "https://api.mews-demo.com/api/connector/v1/":
    print("⚠️ Running against DEMO environment. Make sure this is intended. If not, waiting 15 seconds to abort...")
    time.sleep(15)
    clientToken = "E0D439EE522F44368DC78E1BFB03710C-D24FB11DBE31D4621C4817E028D9E1D"
    accessToken = "B59225A566844465B3F1B3AD00D87552-66D83848AD0DB75277653994BBF827D"
    serviceId = "c1bcdc5d-b995-4c18-b9dc-b36400abe878"

elif url == "https://api.mews.com/api/connector/v1/":
    print("⚠️ Running against LIVE environment. Make sure this is intended. If not, waiting 15 seconds to abort...")
    time.sleep(15)
    clientToken = "5634361153F846C59A90AA8000AD91D2-B5F40C389667E8484CE2486E50F9E67"
    accessToken = "1CF408BA85E94AB3978BB3B5009DAB1E-AA1C74104C702AB8E55A16C5ADECE75"
    serviceId = "6fb1f6ca-34af-4264-b6fa-b28e00e3e301"

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
    reservationData = []
    for item in response.json().get("Reservations", []):
        createdStr = datetime.fromisoformat(item.get("CreatedUtc").replace("Z", "+00:00"))

        if item.get("BusinessSegmentId") in segmentId:
            skippedReservations.append((item.get("Id"), "Group rate"))
            skipped_f.write(f"{item.get("Id")} - segmentId / group rate\n")
            skipped_f.flush()
            continue

        if item.get("TravelAgencyId") == bookingComId and createdStr > bookingCutoff:
            skippedReservations.append((item.get("Id"), "Booking.com pre-Nov 10"))
            skipped_f.write(f"{item.get("Id")} - Booking.com post-Nov 10\n")
            skipped_f.flush()
            continue
        elif item.get("TravelAgencyId") in expedialistForCutoff and createdStr > expediaCutoff:
            skippedReservations.append((item.get("Id"), "Expedia pre-Dec 1"))
            skipped_f.write(f"{item.get("Id")} - Expedia post-Dec 1\n")
            skipped_f.flush()
            continue
        elif item.get("PartnerCompanyId") in expedialistForCutoff and createdStr > expediaCutoff:
            skippedReservations.append((item.get("Id"), "Expedia pre-Dec 1"))
            skipped_f.write(f"{item.get("Id")} - Expedia post-Dec 1\n")
            skipped_f.flush()
            continue
        elif item.get("TravelAgencyId") in expediaCollectskip:
            skippedReservations.append((item.get("Id"), "Expedia Collect - product verhoging"))
            skipped_f.write(f"{item.get("Id")} - Expedia Collect/airbnb/hotelbeds/DOTW\n")
            skipped_f.flush()
            continue
        elif item.get("PartnerCompanyId") in expediaCollectskip:
            skippedReservations.append((item.get("Id"), "Expedia Collect - product verhoging"))
            skipped_f.write(f"{item.get("Id")} - Expedia Collect\n")
            skipped_f.flush()
            continue
        elif item.get("Id") in processed_ids:
            skippedReservations.append((item.get("Id"), "Already processed"))
            skipped_f.write(f"{item.get("Id")} - Already processed\n")
            skipped_f.flush()
            continue
        else:
            reservationData.append([item.get("Id"), item.get("RateId")])        
            reservationdIds.append(item.get("Id"))

    return reservationData

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
PROCESSED_FILE = Path("processed_ids_Utrecht.txt")
ERRORED_FILE = Path("errored_ids.txt")
SKIPPED_FILE = Path("skipped_ids_Utrecht.txt")

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
        for itemcombo in reservationsIds:
            reservationId = itemcombo[0]
            rateId = itemcombo[1]
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
                    processed_f.write(f"{reservationId}, {increase_total}, {rateId}\n")
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