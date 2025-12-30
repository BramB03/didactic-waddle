import requests, json, time, pytest, os, pprint
from datetime import datetime, timedelta, timezone
from pathlib import Path

'''
Booking.com vanaf 10 november 0.00 uur.
Logica:
if travelagencyId == "" and createdUtc before November 10th 00:00:00Z:
Webtarieven bastion (CWI / Open API), vanaf 13 november 0:00 uur
if origin == "Connector" and createdUtc before November 13th 00:00:00Z:
'''

def getReservationInformation(serviceId, count, startDate, endDate, clientToken, accessToken, client, url, headers):
    serviceId = None
    payload = {
        "ClientToken": clientToken,
        "AccessToken": accessToken,
        "Client": client,
        "ServiceIds": serviceId,
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
    reservationData = []
    bookingCutoff = datetime(2025, 11, 9, 23, 0, 0, tzinfo=timezone.utc)
    connectorCutoff = datetime(2025, 11, 12, 23, 0, 0, tzinfo=timezone.utc)
    expediaCutoff = datetime(2025, 11, 30, 23, 0, 0, tzinfo=timezone.utc)
    BWdateCutOff = datetime(2025, 12, 2, 23, 0, 0, tzinfo=timezone.utc)
    for item in response.json().get("Reservations", []):
        createdStr = datetime.fromisoformat(item.get("CreatedUtc").replace("Z", "+00:00"))
        if item.get("RateId") in BWdateRateCutOff and createdStr > BWdateCutOff:
            skippedReservations.append((item.get("Id"), "BW date after 3 dec"))
            print(f"Skipping {item.get('Id')} - BW date after 3 dec")
            skipped_f.write(f"{item.get('Id')} - BW date after 3 dec\n")
            skipped_f.flush()
            continue
        if item.get("RateId") in BWdateRateCutOff_filtered:
            skippedReservations.append((item.get("Id"), "BW date before 3 dec - gross rate"))
            print(f"Skipping {item.get('Id')} - BW date before 3 dec - gross rate")
            skipped_f.write(f"{item.get('Id')} - BW date before 3 dec - gross rate\n")
            skipped_f.flush()
            continue
        if item.get("RateId") in BWrateCutOff:
            skippedReservations.append((item.get("Id"), "BW rate productchange"))
            print(f"Skipping {item.get('Id')} - BW rate productchange")
            skipped_f.write(f"{item.get('Id')} - BW rate productchange\n")
            skipped_f.flush()
            continue
        if item.get("TravelAgencyId") == "d988b779-31e5-4716-b21b-b24100a3a684" and createdStr > bookingCutoff:
            skippedReservations.append((item.get("Id"), "Booking.com pre-Nov 10"))
            skipped_f.write(f"{item.get("Id")} - Booking.com post-Nov 10\n")
            skipped_f.flush()
            continue
        elif item.get("Origin") == "Connector" and createdStr > connectorCutoff:
            skippedReservations.append((item.get("Id"), "Webtarieven  pre-Nov 13"))
            skipped_f.write(f"{item.get("Id")} - Webtarieven  post-Nov 13\n")
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
            skipped_f.write(f"{item.get("Id")} - Expedia Collect\n")
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

        #reservationData.append([item.get("Id"), item.get("RateId")]) # review

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
        "Reason": "BTW 2026 aanpassing",
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
#clientToken = os.getenv("DEMO_CLIENTTOKEN")
#accessToken = os.getenv("DAVID_ACCESSTOKEN")
#serviceId = "5291ecd7-c75f-4281-bca0-ae94011b2f3a"

client = "Bastion VAT migration test script"
url = "https://api.mews.com/api/connector/v1/"
headers = {
    "Content-Type": "application/json"
}

# Property specific config
# =====================================================
#  Hotels WebsiteToken
clientToken = "-"
accessToken = "-"
serviceId = ["23abd1ab-9537-4be3-a72b-b2440103bc47"]
propertyName = "BEST_WESTERN"

# Execution specific information
# =====================================================
reservationCount = 1000 # Max aantal reserveringen om te verwerken. Inkorten voor testdoeleinden.
iterationRange = 320 # Aantal iteraties om te verwerken vanaf startdatum.
dayRange = 1 # Aantal dagen per iteratie. 
start = "2026-02-11T00:00:00Z"

endpointCounter = 0
totalValuebefore = 0
totalValueafter = 0
totalIncrease = 0
reservationCounter = 0
PROCESSED_FILE = Path(f"processed_ids_{propertyName}.txt")
ERRORED_FILE = Path(f"errored_ids_{propertyName}.txt")
SKIPPED_FILE = Path(f"skipped_ids_{propertyName}.txt")

expedialistForCutoff = ["b3adc573-64a7-4ce0-81e2-b24200e39390", "161edaed-b1ba-4989-8619-b24e010af3e4", "7ee34673-b35b-4576-8d7b-b24100a398e6", "af175a04-1887-4dc4-8c72-b2fe00a4f2bc?tab", "3cdf0d89-bf15-4566-8984-b24100a4a0ea" , "591326a2-ef2c-4311-b556-b242015d826e", "928f1e4d-7a5b-47b6-80a4-b24100a41e24"]
expediaCollectskip = ["7ee34673-b35b-4576-8d7b-b24100a398e6", "af175a04-1887-4dc4-8c72-b2fe00a4f2bc", "3cdf0d89-bf15-4566-8984-b24100a4a0ea", "591326a2-ef2c-4311-b556-b242015d826e"]
BWrateCutOff = [
    "a997cc53-16a3-4a1a-8ecc-b27c01098dd3",
    "33cfaa05-149d-4527-b921-b27c01098dbc",
    "1b54caea-79c6-41d6-a067-b27c01098da6",
    "bc1b568f-d5c9-474a-b88b-b27c01098d8e",
    "3ba4c306-6c75-49f2-9a0a-b27c01098cf8",
    "cbdfe249-1111-4b82-b043-b27c01098c89",
    "5948cfb7-6487-453e-97b7-b27c01098c66",
    "6707ad03-656d-4cc8-8862-b27c01098c4f",
    "0f20338d-0d1b-4246-b036-b27c01098c44",
    "af06bb66-6882-47b5-8e3d-b27c01098c39",
    "d89629b9-fdda-41f6-bf7a-b27c01098c1e",
    "1990f9a4-c93b-4541-9996-b27c01098c13",
    "e89feb30-4223-486b-bcbb-b27c01098c07",
    "3807ae8f-258d-41a5-924a-b27c01098bfa",
    "08b1ea5d-3592-4e97-9f74-b27c01098be3",
    "5476aed8-1cbd-4a4b-9049-b27c01098b1c",
    "15643209-f54e-4a18-bf74-b27c01098b11",
    "438321b0-3f67-4b6f-9001-b27c01098b06",
    "1bc0fe7c-6908-4d8e-9560-b27c01098ad8",
    "9625fbab-367a-4127-b114-b27c01098ab2",
]
BWdateRateCutOff = ['ed579694-2d82-42af-a369-b3a1008ceb88', '3512facd-5818-45ad-b974-b28800e1b23b', 'b49c6fcd-d110-43de-8f1d-b27c01098dff', '7511c9e9-13c6-4e43-a9ca-b27c01098df3', 'ddfde19f-7777-4b91-831f-b27c01098de9', 'a440983b-3122-480d-9a8c-b27c01098ddd', 'a997cc53-16a3-4a1a-8ecc-b27c01098dd3', '753464f1-7589-474f-833a-b27c01098dc7', '33cfaa05-149d-4527-b921-b27c01098dbc', '1d6ca27f-bd13-4900-b1d7-b27c01098db1', '1b54caea-79c6-41d6-a067-b27c01098da6', '37c99387-fbb4-46f1-9199-b27c01098d9a', 'bc1b568f-d5c9-474a-b88b-b27c01098d8e', '8c8f546c-2189-479b-bdc8-b27c01098d82', 'b526e88f-70c4-4c9d-a1ff-b27c01098d76', 'c895326e-94cd-41b3-b03d-b27c01098d67', 'f3da0a72-e663-410c-be41-b27c01098d5c', '5ef01a9b-261e-4525-96ec-b27c01098d51', 'd7f6e226-8716-4fd9-9fa6-b27c01098d45', 'f1340094-326b-4d5f-abc5-b27c01098d3a', 'a944de45-437a-4bca-b57a-b27c01098d2f', 'f828a756-6dc5-4f2f-92c9-b27c01098d24', '3572bf7a-70a1-4f32-b172-b27c01098d1a', '4d6f4c1a-d525-46ba-ae67-b27c01098d0f', 'd9e599a3-005b-4e78-965b-b27c01098d04', '3ba4c306-6c75-49f2-9a0a-b27c01098cf8', 'a257d22c-45b0-40a4-905b-b27c01098ca0', '8b2af2ed-2ed8-4d39-8569-b27c01098c94', 'cbdfe249-1111-4b82-b043-b27c01098c89', '9ba251b6-fd96-491c-a3ff-b27c01098c7d', '5a1c0aa4-a2e4-4936-87a4-b27c01098c72', '5948cfb7-6487-453e-97b7-b27c01098c66', 'a6e21c33-90dd-4979-8af5-b27c01098c5b', '6707ad03-656d-4cc8-8862-b27c01098c4f', '0f20338d-0d1b-4246-b036-b27c01098c44', 'af06bb66-6882-47b5-8e3d-b27c01098c39', '4e8b3764-5aea-4ba5-8d8f-b27c01098c2b', 'd89629b9-fdda-41f6-bf7a-b27c01098c1e', '1990f9a4-c93b-4541-9996-b27c01098c13', 'e89feb30-4223-486b-bcbb-b27c01098c07', '3807ae8f-258d-41a5-924a-b27c01098bfa', '5bd63290-b977-4cc9-b901-b27c01098bef', '08b1ea5d-3592-4e97-9f74-b27c01098be3', '77a5609b-b7af-45e9-8d6d-b27c01098bd6', '65201b56-202b-46f1-a35c-b27c01098bcb', '7f1a2c7f-d369-46fe-ae51-b27c01098bc0', '6c32ea79-e6f9-4302-a1ab-b27c01098bb3', 'ca9311cf-f98b-48fb-b5dd-b27c01098ba8', 'efa8ac7f-4914-4d26-9b1e-b27c01098b9c', '46da344b-a759-49fc-be54-b27c01098b92', '51949352-b537-4719-8e16-b27c01098b87', 'baeae6c1-7808-450c-a3dc-b27c01098b7b', 'c4f18818-7b71-44a6-b38f-b27c01098b6e', 'c6383872-8ea5-4154-82ed-b27c01098b63', '558700f8-5320-4b6d-9fd0-b27c01098b58', '80446704-bf7a-4335-8b9f-b27c01098b4b', '6a6f69d7-6fe2-4be9-b28d-b27c01098b40', '7e572c8e-12fa-46de-ba50-b27c01098b33', '7bc57590-54b2-4f92-a193-b27c01098b28', '5476aed8-1cbd-4a4b-9049-b27c01098b1c', '15643209-f54e-4a18-bf74-b27c01098b11', '438321b0-3f67-4b6f-9001-b27c01098b06', '1b6467ec-10e2-48e5-bd13-b27c01098afa', '979f937e-19e2-496e-bdda-b27c01098aef', 'd206577b-bd78-437e-a493-b27c01098ae3', '1bc0fe7c-6908-4d8e-9560-b27c01098ad8', 'a113c566-897c-4f3f-a3bc-b27c01098acc', 'fb063672-570e-4c84-b632-b27c01098abf', '9625fbab-367a-4127-b114-b27c01098ab2', '2bb0e2f5-a816-4040-9c4a-b27c01098aa3', '167fe362-274e-43b2-b79c-b27c01098a3f']
BWdateRateCutOff_filtered = [
    "ed579694-2d82-42af-a369-b3a1008ceb88",
    "3512facd-5818-45ad-b974-b28800e1b23b",
    "b49c6fcd-d110-43de-8f1d-b27c01098dff",
    "7511c9e9-13c6-4e43-a9ca-b27c01098df3",
    "ddfde19f-7777-4b91-831f-b27c01098de9",
    "a440983b-3122-480d-9a8c-b27c01098ddd",
    "753464f1-7589-474f-833a-b27c01098dc7",
    "1d6ca27f-bd13-4900-b1d7-b27c01098db1",
    "37c99387-fbb4-46f1-9199-b27c01098d9a",
    "8c8f546c-2189-479b-bdc8-b27c01098d82",
    "b526e88f-70c4-4c9d-a1ff-b27c01098d76",
    "c895326e-94cd-41b3-b03d-b27c01098d67",
    "f3da0a72-e663-410c-be41-b27c01098d5c",
    "5ef01a9b-261e-4525-96ec-b27c01098d51",
    "d7f6e226-8716-4fd9-9fa6-b27c01098d45",
    "f1340094-326b-4d5f-abc5-b27c01098d3a",
    "a944de45-437a-4bca-b57a-b27c01098d2f",
    "f828a756-6dc5-4f2f-92c9-b27c01098d24",
    "3572bf7a-70a1-4f32-b172-b27c01098d1a",
    "4d6f4c1a-d525-46ba-ae67-b27c01098d0f",
    "d9e599a3-005b-4e78-965b-b27c01098d04",
    "a257d22c-45b0-40a4-905b-b27c01098ca0",
    "8b2af2ed-2ed8-4d39-8569-b27c01098c94",
    "9ba251b6-fd96-491c-a3ff-b27c01098c7d",
    "5a1c0aa4-a2e4-4936-87a4-b27c01098c72",
    "a6e21c33-90dd-4979-8af5-b27c01098c5b",
    "4e8b3764-5aea-4ba5-8d8f-b27c01098c2b",
    "5bd63290-b977-4cc9-b901-b27c01098bef",
    "77a5609b-b7af-45e9-8d6d-b27c01098bd6",
    "65201b56-202b-46f1-a35c-b27c01098bcb",
    "7f1a2c7f-d369-46fe-ae51-b27c01098bc0",
    "6c32ea79-e6f9-4302-a1ab-b27c01098bb3",
    "ca9311cf-f98b-48fb-b5dd-b27c01098ba8",
    "efa8ac7f-4914-4d26-9b1e-b27c01098b9c",
    "46da344b-a759-49fc-be54-b27c01098b92",
    "51949352-b537-4719-8e16-b27c01098b87",
    "baeae6c1-7808-450c-a3dc-b27c01098b7b",
    "c4f18818-7b71-44a6-b38f-b27c01098b6e",
    "c6383872-8ea5-4154-82ed-b27c01098b63",
    "558700f8-5320-4b6d-9fd0-b27c01098b58",
    "80446704-bf7a-4335-8b9f-b27c01098b4b",
    "6a6f69d7-6fe2-4be9-b28d-b27c01098b40",
    "7e572c8e-12fa-46de-ba50-b27c01098b33",
    "7bc57590-54b2-4f92-a193-b27c01098b28",
    "1b6467ec-10e2-48e5-bd13-b27c01098afa",
    "979f937e-19e2-496e-bdda-b27c01098aef",
    "d206577b-bd78-437e-a493-b27c01098ae3",
    "a113c566-897c-4f3f-a3bc-b27c01098acc",
    "fb063672-570e-4c84-b632-b27c01098abf",
    "2bb0e2f5-a816-4040-9c4a-b27c01098aa3",
    "167fe362-274e-43b2-b79c-b27c01098a3f",
]

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
                

                item ["increasedBy"] = round(item["GrossValue"] * 0.11009174311927, 2)
                item["GrossValue"] = round(item["GrossValue"] * 1.11009174311927, 2)

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