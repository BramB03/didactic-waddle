import requests, json, datetime, sys
from datetime import datetime, timedelta, timezone

headers = {
    "Content-Type": "application/json"
}

'''payload = {
    "ClientToken": "3802A256E16D488796E5B20200B989CE-DD4A90FED8F9CD53DAD2841BCBA407C",
    "AccessToken": "D0ECA51CDA044B719CD6B24C00A17750-A24CADB6D625AAF3F4A7F4B061604F7",
    "Client": "Bastion",
    "ServiceIds": [
        "23abd1ab-9537-4be3-a72b-b2440103bc47"
    ],
    "ActivityStates": [
        "Active"
    ],
    "Extent": {
        "Rates": True,
        "RateGroups": False,
        "AvailabilityBlockAssignments": False
    },
    "Limitation": {
        "Count": 1000
    }
}

response = requests.post(url="https://api.mews.com/api/connector/v1/rates/getAll", headers=headers, data=json.dumps(payload))
ratesData = response.json()
rates = ratesData.get("Rates", [])
rategroups = [
    "32f6e35d-d9f2-45d0-b4f5-b27c01098585",
    "82aa8885-ef25-4d4a-8267-b27c01098586",
    "8faa078f-4c0a-4722-a50b-b27c01098586",
    "5f79f71b-e2ac-4bb5-a91f-b27c01098586",
    "175edc3a-76b8-4ecd-99c2-b27c01098586",
    "0c4f3f89-21ac-4e55-9ed5-b27c01098586",
    "2be2e253-698f-4877-97ba-b27c01098586",
]
rats = []
for rate in rates:
    if rate.get("GroupId") in rategroups:
        print(f"Rate ID: {rate.get('Id')}, Name: {rate.get('Name')}, RateGroupId: {rate.get('RateGroupId')}")
        rats.append(rate.get("Id"))
print(rats)

validUuids = ['ed579694-2d82-42af-a369-b3a1008ceb88', '3512facd-5818-45ad-b974-b28800e1b23b', 'b49c6fcd-d110-43de-8f1d-b27c01098dff', '7511c9e9-13c6-4e43-a9ca-b27c01098df3', 'ddfde19f-7777-4b91-831f-b27c01098de9', 'a440983b-3122-480d-9a8c-b27c01098ddd', 'a997cc53-16a3-4a1a-8ecc-b27c01098dd3', '753464f1-7589-474f-833a-b27c01098dc7', '33cfaa05-149d-4527-b921-b27c01098dbc', '1d6ca27f-bd13-4900-b1d7-b27c01098db1', '1b54caea-79c6-41d6-a067-b27c01098da6', '37c99387-fbb4-46f1-9199-b27c01098d9a', 'bc1b568f-d5c9-474a-b88b-b27c01098d8e', '8c8f546c-2189-479b-bdc8-b27c01098d82', 'b526e88f-70c4-4c9d-a1ff-b27c01098d76', 'c895326e-94cd-41b3-b03d-b27c01098d67', 'f3da0a72-e663-410c-be41-b27c01098d5c', '5ef01a9b-261e-4525-96ec-b27c01098d51', 'd7f6e226-8716-4fd9-9fa6-b27c01098d45', 'f1340094-326b-4d5f-abc5-b27c01098d3a', 'a944de45-437a-4bca-b57a-b27c01098d2f', 'f828a756-6dc5-4f2f-92c9-b27c01098d24', '3572bf7a-70a1-4f32-b172-b27c01098d1a', '4d6f4c1a-d525-46ba-ae67-b27c01098d0f', 'd9e599a3-005b-4e78-965b-b27c01098d04', '3ba4c306-6c75-49f2-9a0a-b27c01098cf8', 'a257d22c-45b0-40a4-905b-b27c01098ca0', '8b2af2ed-2ed8-4d39-8569-b27c01098c94', 'cbdfe249-1111-4b82-b043-b27c01098c89', '9ba251b6-fd96-491c-a3ff-b27c01098c7d', '5a1c0aa4-a2e4-4936-87a4-b27c01098c72', '5948cfb7-6487-453e-97b7-b27c01098c66', 'a6e21c33-90dd-4979-8af5-b27c01098c5b', '6707ad03-656d-4cc8-8862-b27c01098c4f', '0f20338d-0d1b-4246-b036-b27c01098c44', 'af06bb66-6882-47b5-8e3d-b27c01098c39', '4e8b3764-5aea-4ba5-8d8f-b27c01098c2b', 'd89629b9-fdda-41f6-bf7a-b27c01098c1e', '1990f9a4-c93b-4541-9996-b27c01098c13', 'e89feb30-4223-486b-bcbb-b27c01098c07', '3807ae8f-258d-41a5-924a-b27c01098bfa', '5bd63290-b977-4cc9-b901-b27c01098bef', '08b1ea5d-3592-4e97-9f74-b27c01098be3', '77a5609b-b7af-45e9-8d6d-b27c01098bd6', '65201b56-202b-46f1-a35c-b27c01098bcb', '7f1a2c7f-d369-46fe-ae51-b27c01098bc0', '6c32ea79-e6f9-4302-a1ab-b27c01098bb3', 'ca9311cf-f98b-48fb-b5dd-b27c01098ba8', 'efa8ac7f-4914-4d26-9b1e-b27c01098b9c', '46da344b-a759-49fc-be54-b27c01098b92', '51949352-b537-4719-8e16-b27c01098b87', 'baeae6c1-7808-450c-a3dc-b27c01098b7b', 'c4f18818-7b71-44a6-b38f-b27c01098b6e', 'c6383872-8ea5-4154-82ed-b27c01098b63', '558700f8-5320-4b6d-9fd0-b27c01098b58', '80446704-bf7a-4335-8b9f-b27c01098b4b', '6a6f69d7-6fe2-4be9-b28d-b27c01098b40', '7e572c8e-12fa-46de-ba50-b27c01098b33', '7bc57590-54b2-4f92-a193-b27c01098b28', '5476aed8-1cbd-4a4b-9049-b27c01098b1c', '15643209-f54e-4a18-bf74-b27c01098b11', '438321b0-3f67-4b6f-9001-b27c01098b06', '1b6467ec-10e2-48e5-bd13-b27c01098afa', '979f937e-19e2-496e-bdda-b27c01098aef', 'd206577b-bd78-437e-a493-b27c01098ae3', '1bc0fe7c-6908-4d8e-9560-b27c01098ad8', 'a113c566-897c-4f3f-a3bc-b27c01098acc', 'fb063672-570e-4c84-b632-b27c01098abf', '9625fbab-367a-4127-b114-b27c01098ab2', '2bb0e2f5-a816-4040-9c4a-b27c01098aa3', '167fe362-274e-43b2-b79c-b27c01098a3f']

from pathlib import Path

filePath = Path("/workspaces/didactic-waddle/processed_ids_BEST_WESTERN.txt")

matched = []
notMatched = []

with filePath.open("r", encoding="utf-8") as f:
    for lineNumber, line in enumerate(f, start=1):
        line = line.strip()
        if not line:
            continue

        try:
            firstUuid, _, secondUuid = [x.strip() for x in line.split(",")]
        except ValueError:
            raise ValueError(f"Invalid format on line {lineNumber}: {line}")

        if secondUuid in validUuids:
            matched.append(firstUuid)
        else:
            notMatched.append(firstUuid)

print("Matched:", matched)
print("Not matched:", notMatched)
'''

clientToken = "3802A256E16D488796E5B20200B989CE-DD4A90FED8F9CD53DAD2841BCBA407C"
accessToken = "D0ECA51CDA044B719CD6B24C00A17750-A24CADB6D625AAF3F4A7F4B061604F7"
serviceId = ["23abd1ab-9537-4be3-a72b-b2440103bc47"]
propertyName = "BEST_WESTERN"
client = "Bastion VAT migration test script"
url = "https://api.mews.com/api/connector/v1/"
headers = {
    "Content-Type": "application/json"
}

reservationProductList = []
reservationsToCheck = ['61e202ca-b112-4dc9-bd45-b3b001343461', 'bfa737dc-9c69-44ee-831a-b31e00f1e3eb', '5af95973-6f0d-48e9-bb9e-b3b000a035b4', 'd744c20d-38d1-4b12-a3ac-b37c00bd2d3f', 'c80ef270-ab80-4991-b5cd-b3b7010f51ed', 'ff3f77d6-c7bd-4e24-9620-b3a4014d05f3', 'e8154596-65eb-4579-b4d2-b37800b9fe44', '2aa32901-51fc-40aa-b08f-b3a1010c3fa3', '1f08305d-ed93-4fb2-8f0f-b3a700d37b91', '7922a4fa-8abb-4c45-8fb7-b35300cef6ab', 'da4dd704-8eb4-4fed-8e92-b3b70106f782', '557e4121-9c49-4c63-9938-b3ae01465a59', 'dd048676-abc9-434d-b346-b39b00449584', '463e0b4c-cad3-4ae3-99c5-b3ac01484e55', 'db2e19c9-2f56-49af-8e4b-b3ac01484aa6', '777a95a0-eac4-413e-98ad-b31e00f3b2f2', 'f21027e5-622f-49f8-9247-b3af014cf380', '717f87db-1bf0-4688-af51-b39300e4ea13', 'a64c56ae-091a-449c-9904-b38d01259e80', 'b5aaeb8e-8ffb-4be4-b59e-b38f009c0f84', '297ef4cc-72bc-4c92-a56b-b3b800758673', 'aab1662f-8467-40c9-a704-b3ac0181435d', '5c981a23-afef-4ea4-b127-b3b000c60ade', 'a1bb56ac-dec9-4e33-8bd6-b3a201426cb5', '038ea461-374e-4e37-98e2-b3a201426077', 'cff0b2ab-d1d1-4aee-8948-b38c00d047dc', '3f5835e7-62e8-4d80-bfb5-b38c00cf9935', '47550916-f8d4-4a19-a685-b37200d1aa03', 'd316212a-abb9-4967-8bc7-b3b500fbfab0', 'a29a3364-7b76-44d5-bf1c-b39900b6d1fa', '8e90627a-1aea-4bbf-a0b2-b3b600df7328', 'd7b4e0a5-c721-4337-9e2d-b3b600df1583', 'e1e5dd09-7efa-4e6e-9a91-b3b600de6bee', '669757d6-f905-447d-9379-b3b600ddc804', 'dcbeb460-4cca-4446-aae9-b3b00054a182']
for reservationId in reservationsToCheck:
    reservationData = getReservationInformation(
        serviceId,
        reservationId,
        clientToken,
        accessToken,
        client,
        url, 
        headers
    )
    if not reservationData:
        print("No reservation data found for ID:", reservationId)
        continue
        
    nightsData = getReservationNightData(
        reservationId, 
        clientToken, 
        accessToken, 
        client, 
        url, 
        headers
    )
    data_sorted = sorted(
        nightsData,
        key=lambda x: datetime.fromisoformat(x["ConsumedUtc"].replace("Z", "+00:00"))
    )
    for i, item in enumerate(data_sorted):
        item["Index"] = i
        #totalValuebefore += item["GrossValue"]
        

        #item ["increasedBy"] = round(item["GrossValue"] * 0.11009174311927, 2)
        item["GrossValue"] = round(item["GrossValue"] / 1.11009174311927, 2)

        #totalValueafter += item["GrossValue"]
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

print(reservationProductList)