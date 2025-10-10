from datetime import datetime, timedelta, time
from zoneinfo import ZoneInfo
import pprint, json, requests, sys
from collections import defaultdict

ogProductIds = ["6d8a2818-1eb7-495c-82c5-b30100e347c4","0b1543cf-ad07-4f3b-a621-b30f00eae103","3375115b-5f7f-4c3c-8f4d-b2ae008a66bb","1c567a53-70cf-406e-8dd7-b2ae0088f870"]

# Current time in Stockholm
nowStockholm = datetime.now(ZoneInfo("Europe/Helsinki"))
midnightStockholm = datetime.combine(nowStockholm.date(), time.min, tzinfo=ZoneInfo("Europe/Helsinki"))
lastMidnightUtc = midnightStockholm.astimezone(ZoneInfo("UTC"))
nextMidnightStockholm = midnightStockholm + timedelta(days=1)
thisMidnightUtc = nextMidnightStockholm.astimezone(ZoneInfo("UTC"))
lastMidnightIso = lastMidnightUtc.strftime("%Y-%m-%dT%H:%M:%SZ")
thisMidnightIso = thisMidnightUtc.strftime("%Y-%m-%dT%H:%M:%SZ")
utcMidnightPlus7 = lastMidnightUtc + timedelta(hours=7)
utcMidnightPlus7Iso = utcMidnightPlus7.strftime("%Y-%m-%dT%H:%M:%SZ")

ageCategoryMap = {
    "db1c74ba-a223-43ec-83c9-b101008aa8b2": "child",
    "ba240c04-7158-4909-a4e1-affe00a57696": "adult"
}
infantId = "fd27f938-812c-43cb-8585-affe00a57967"

URL = "https://api.mews-demo.com/api/connector/v1/"
headers = {
    "Content-Type": "application/json"
}

clientToken = "E0D439EE522F44368DC78E1BFB03710C-D24FB11DBE31D4621C4817E028D9E1D"
accessToken = "133F1ED981804738A045B061008A726C-A06E372F46FA4E3ABAB5951839547ED"
enterpriseID = "ec0be015-3e1e-4b91-b0f0-affe00a564e8"
hotelServiceID = "ca2ecc15-e479-47db-95ea-affe00a57696"
packageServiceID = "17cc75d8-f78e-43d9-b207-b2eb0092b394"

payloadReservations = {
    "ClientToken": clientToken,
    "AccessToken": accessToken,
    "EnterpriseId": enterpriseID,
    "Client": "Zapier",
    "ServiceIds": [
        hotelServiceID
    ],
    "States": [
        "Started"
    ],
    "ScheduledEndUtc": {
        "StartUtc": lastMidnightIso,
        "EndUtc": thisMidnightIso
    },
    "Limitation": {
        "Count": 1000
    }
}

jsonPayloadReservations = json.dumps(payloadReservations)
responsePayloadReservations = requests.post(URL + "reservations/getAll/2023-06-06", data=jsonPayloadReservations, headers=headers)
getReservations = responsePayloadReservations.json()

#if not getReservations['Reservations']:
    #return {'Response':'No reservations'}

reservations_checkout_tomorrow = [
    reservation['AccountId'] for reservation in getReservations['Reservations']
]

accountMap = {"accounts": {}}
productIds = []

for reservation in getReservations["Reservations"]:
    accRoot = accountMap["accounts"].setdefault(
        reservation["AccountId"],
        {"reservations": {}}
    )
    accRoot["reservations"].setdefault(reservation["Id"], {})

payloadOrderItems = {
    "ClientToken": clientToken,
    "AccessToken": accessToken,
    "EnterpriseId": enterpriseID,
    "Client": "Zapier",
    "ServiceIds": [
        packageServiceID,
        hotelServiceID
    ],
    "AccountingStates": [
        "Open"
    ],
    "Types": [
        "ProductOrder"
    ],
    "AccountIds": reservations_checkout_tomorrow,
    "Limitation": {
        "Count": 1000
    }
}

jsonPayloadOrderItems = json.dumps(payloadOrderItems)
responsePayloadOrderItems = requests.post(URL + "orderItems/getAll", data=jsonPayloadOrderItems, headers=headers)
getOrderItems = responsePayloadOrderItems.json()

handOff = []

for item in getOrderItems["OrderItems"]:
    if (
        item["RevenueType"] == "Product"
        and isinstance(item.get("Data"), dict)
        and isinstance(item["Data"].get("Product"), dict)
        and item["Data"]["Product"].get("ProductId") in ogProductIds
    ):
        accountId = item.get("AccountId"),
        serviceOrderId = item.get("ServiceOrderId"),
        handOff.append((accountId, serviceOrderId))

text = {'OrderItems': [{'Id': 'b9da0356-d40e-4ab4-859f-b3690084ce33', 'EnterpriseId': 'ec0be015-3e1e-4b91-b0f0-affe00a564e8', 'AccountId': 'db2de5c8-7138-43f7-955e-b369007fe533', 'AccountType': 'Customer', 'ServiceId': '17cc75d8-f78e-43d9-b207-b2eb0092b394', 'ServiceOrderId': 'ade2adec-1757-4339-a1f7-b3690084ce15', 'Notes': None, 'BillId': None, 'AccountingCategoryId': '4944bc0f-d99c-4afd-8c5f-b30100e26b5a', 'BillingName': 'B2 - 89€ - Adult', 'ExternalIdentifier': None, 'UnitCount': 1, 'UnitAmount': {'Currency': 'SEK', 'NetValue': 71.2, 'GrossValue': 89.0, 'TaxValues': [{'Code': 'SE-S', 'Value': 17.8}], 'Breakdown': {'Items': [{'TaxRateCode': 'SE-S', 'NetValue': 71.2, 'TaxValue': 17.8}]}}, 'Amount': {'Currency': 'SEK', 'NetValue': 71.2, 'GrossValue': 89.0, 'TaxValues': [{'Code': 'SE-S', 'Value': 17.8}], 'Breakdown': {'Items': [{'TaxRateCode': 'SE-S', 'NetValue': 71.2, 'TaxValue': 17.8}]}}, 'OriginalAmount': {'Currency': 'SEK', 'NetValue': 71.2, 'GrossValue': 89.0, 'TaxValues': [{'Code': 'SE-S', 'Value': 17.8}], 'Breakdown': {'Items': [{'TaxRateCode': 'SE-S', 'NetValue': 71.2, 'TaxValue': 17.8}]}}, 'RevenueType': 'Product', 'CreatorProfileId': '8e1bf839-5f9d-4ccd-903a-b2990103ae10', 'UpdaterProfileId': '8e1bf839-5f9d-4ccd-903a-b2990103ae10', 'CreatedUtc': '2025-10-01T08:03:31Z', 'UpdatedUtc': '2025-10-01T08:03:31Z', 'ConsumedUtc': '2025-10-01T08:03:20Z', 'CanceledUtc': None, 'ClosedUtc': None, 'StartUtc': '2025-09-30T22:00:00Z', 'ClaimedUtc': None, 'AccountingState': 'Open', 'Type': 'ProductOrder', 'Options': {'CanceledWithReservation': False}, 'Data': {'Discriminator': 'Product', 'Rebate': None, 'Product': {'ProductId': '6d8a2818-1eb7-495c-82c5-b30100e347c4', 'AgeCategoryId': None, 'ProductType': None}, 'AllowanceDiscount': None, 'AllowanceProfits': None}, 'TaxExemptionReason': None, 'TaxExemptionLegalReference': None}], 'Cursor': 'b9da0356-d40e-4ab4-859f-b3690084ce33'}
pprint.pprint(text)