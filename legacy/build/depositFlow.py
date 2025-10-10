from datetime import datetime, timedelta, timezone
import requests
import json
import sys
import pprint
from collections import defaultdict

# Get the current UTC time
now_utc = datetime.now(timezone.utc)

# Adjust to the start to midnight UTC by setting hours, minutes and seconds to zero.
# Adjust the hours incase of a difference bewteen due to the timezone
endUtc = now_utc.replace(hour=0,minute=0, second=0, microsecond=0)

# Calculate the start of the timeframe by setting minutes to 59 and seconds to 59
startUtc = endUtc - timedelta(days=1)
endUtc = endUtc - timedelta(seconds=1) + timedelta(days=1) #remove day+1, is for testing only
startUtc = startUtc.isoformat()
endUtc = endUtc.isoformat()

ClientToken = "E0D439EE522F44368DC78E1BFB03710C-D24FB11DBE31D4621C4817E028D9E1D"
AccessToken = "BEC33DAD4C57410C9E6DB09600C7FB9B-310471532A30162E5B6F0EB4F4AD2BF"
URL = "https://api.mews-demo.com/api/connector/v1/"

headers = {
    "Content-Type": "application/json"
}

payloadPayments = {
    "ClientToken": ClientToken,
    "AccessToken": AccessToken,
    "Client": "Sample Client 1.0.0",
    "CreatedUtc": {
        "StartUtc": startUtc,
        "EndUtc": endUtc
    },
    "AccountingStates": [
        "Open"
    ],
    "States": [
        "Charged"
    ],
    "Limitation": {
        "Count": 1000
    }
}

json_payloadPayments = json.dumps(payloadPayments) # Convert the payload to JSON format
getPayments = requests.post(URL + "payments/getAll", data=json_payloadPayments, headers=headers) # Send the POST request
if getPayments.status_code != 200:
    Error = "getPayments" + str(getPayments)
    sys.exit(Error)
getPaymentsJson = getPayments.json() 
filteredPaymentsRes = [
    {
        "ReservationId": payment["ReservationId"],
        "Amount": payment["Amount"]["GrossValue"],
        "Currency": payment["Amount"]["Currency"]
    }
    for payment in getPaymentsJson["Payments"]
    if payment["ReservationId"] is not None
]
reservationIds = []
for i in filteredPaymentsRes:
    reservationIds.append(i["ReservationId"])
    

filteredPaymentsNoRes = [
    {
        "AccountId": payment["AccountId"],
        "Amount": payment["Amount"]["GrossValue"],
        "Currency": payment["Amount"]["Currency"]
    }
    for payment in getPaymentsJson["Payments"]
    if payment["ReservationId"] is None
]

payloadReservations = {
    "ClientToken": ClientToken,
    "AccessToken": AccessToken,
    "Client": "Sample Client 1.0.0",
    "ServiceIds": [
        "5291ecd7-c75f-4281-bca0-ae94011b2f3a"
    ],
    "ReservationIds": reservationIds,
    "State": [
        "Confirmed"
    ],
    "Limitation": {
        "Count": 1000
    }
}

json_payloadReservations = json.dumps(payloadReservations) # Convert the payload to JSON format
getReservations = requests.post(URL + "reservations/getAll/2023-06-06", data=json_payloadReservations, headers=headers) # Send the POST request
if getReservations.status_code != 200:
    Error = "getReservations" + str(getReservations)
    sys.exit(Error)
getReservationsJson = getReservations.json() 

filteredReservations = [
    {
        "ReservationId": Reservations["Id"],
        "StartUtc": Reservations["StartUtc"],
    }
    for Reservations in getReservationsJson["Reservations"]
]

dict = {item['ReservationId']: item['StartUtc'] for item in filteredReservations}

# Merge lists based on ReservationId
merged_list = []
for item in filteredPaymentsRes:
    res_id = item['ReservationId']
    if res_id in dict:
        date_str = dict[res_id]
        month_number = datetime.strptime(date_str[:10], "%Y-%m-%d").strftime("%m")
        item['Month'] = month_number
    item['Amount'] = item['Amount'] * -1
    merged_list.append(item)

# Aggregate by month
aggregated_data = defaultdict(lambda: {'TotalAmount': 0.0, 'Currency': 'EUR'})
for item in merged_list:
    month = item['Month']
    aggregated_data[month]['TotalAmount'] += item['Amount']
    aggregated_data[month]['Currency'] = item['Currency']

# Convert aggregated data to list
aggregated_list = [{'Month': month, 'TotalAmount': data['TotalAmount'], 'Currency': data['Currency']} for month, data in aggregated_data.items()]
# Output the merged list
print(json.dumps(aggregated_list, indent=4))
