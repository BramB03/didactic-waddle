import json
import requests
import pprint
from datetime import datetime

headers = {
    "Content-Type": "application/json"
}
URL = "https://api.mews-demo.com/api/connector/v1/"

clientToken = "E0D439EE522F44368DC78E1BFB03710C-D24FB11DBE31D4621C4817E028D9E1D"
accessToken = "BEC33DAD4C57410C9E6DB09600C7FB9B-310471532A30162E5B6F0EB4F4AD2BF"
reservationId = "7b8bde89-38aa-4a8f-91eb-b31b00e2afaf"

payloadOrderItems = {
    "ClientToken": clientToken,
    "AccessToken": accessToken,
    "Client": "Zapier",
    "ReservationIds": [
        reservationId
    ]
}

jsonPayloadOrderItems = json.dumps(payloadOrderItems)
getOrderItemsJson = requests.post(URL + "reservations/getAllItems", data=jsonPayloadOrderItems, headers=headers)
orderItems = getOrderItemsJson.json()

gross_values = []

for reservation in orderItems.get('Reservations', []):
    for item in reservation.get('Items', []):
        if item.get('Type') == 'ServiceRevenue':
            gross_value = item.get('Amount', {}).get('GrossValue', 0)
            name = item.get('Name', '').replace('Night ', '')
            gross_values.append((name, gross_value))

gross_values.sort(key=lambda x: datetime.strptime(x[0], '%d/%m/%Y'))
payloadSub = []

for i in range(len(gross_values)):
    payloadMini = {
        "Index": i,
        "Amount": {
            "Currency": "EUR",
            "GrossValue": gross_values[i][1],
            "TaxCodes": [
            "NL-2019-S"
            ]
        }
    }
    payloadSub.append(payloadMini)


payloadReservationUpdate = {
    "ClientToken": clientToken,
    "AccessToken": accessToken,
    "Client": "Zapier",
    "Reason": "Testing",
    "ReservationUpdates": [
        {
            "ReservationId": reservationId,
            "TimeUnitPrices": {
                "Value": payloadSub
            }
        }
    ]
}

jsonPayloadReservationUpdate = json.dumps(payloadReservationUpdate)
getReservationUpdate = requests.post(URL + "reservations/getAllItems", data=jsonPayloadReservationUpdate, headers=headers)
reservationUpdate = getReservationUpdate.json()
