import sys, os
import requests
import json
from datetime import datetime, timedelta, timezone
import random
import math
import subprocess
import time
import pytz
from pprint import pprint
from collections import Counter

headers = {
    "Content-Type": "application/json"
}

GuestName = input("What is the guest's name?: ")

payloadSearch = {
    "ClientToken": os.getenv("DEMO_CLIENTTOKEN"),
    "AccessToken": os.getenv("DAVID_ACCESSTOKEN"),
    "Client": "Mews Client",
    "Name": GuestName,
    "ResourceId": None,
    "Extent": {
        "Customers": True,
        "Documents": False,
        "Addresses": False
  }
}

GuestOptions = []

utc_time = datetime.now(timezone.utc)
target_datetime = utc_time.astimezone(timezone(timedelta(hours=2)))
target_datetime_str = target_datetime.strftime('%Y-%m-%dT%H:%M:%S%z')
target_datetime_str = target_datetime_str[:-2] + ':' + target_datetime_str[-2:]

payloadSearch = json.dumps(payloadSearch) # Convert the payload to JSON format
getCustomer = requests.post("https://api.mews-demo.com/api/connector/v1/customers/search", data=payloadSearch, headers=headers) # Send the POST request
getCustomer_data = getCustomer.json() # Parse the JSON response

if getCustomer_data['Customers'] == []:
    print("No customer found")
else:
    for customer_data in getCustomer_data['Customers']:
        reservationNumber = customer_data['Reservation']['Number']
        roomNumber = customer_data['RoomNumber']
        customerId = customer_data['Customer']['Id']
        lastName = customer_data['Customer']['LastName']
        GuestOptions.append([lastName, roomNumber, customerId, reservationNumber])
        
    GuestOptionsTuple = [item for sublist in GuestOptions for item in sublist]

    if len(set(GuestOptionsTuple)) > 4:
        for guestOption in GuestOptions:
            print(guestOption[0], ' - Roomnumber: ',guestOption[1])
            CorrectGuest = input("Enter the roomnumber?: ")
        #
        for guestOption in GuestOptions:
            if guestOption[1] == CorrectGuest:           
                payloadBill = {
                    "ClientToken": os.getenv("DEMO_CLIENTTOKEN"),
                    "AccessToken": os.getenv("DAVID_ACCESSTOKEN"),
                    "Client": "Mews Client",
                    "CustomerIds": [
                        guestOption[2]
                    ],
                    "State": "Open",
                    "Limitation": {
                        "Count": 100,
                    }
                }
                payloadBill = json.dumps(payloadBill) # Convert the payload to JSON format
                getBills = requests.post("https://api.mews-demo.com/api/connector/v1/bills/getAll", data=payloadBill, headers=headers) # Send the POST request
                getBills_data = getBills.json() # Parse the JSON response
                for bill in getBills_data['Bills']:
                    billName = getBills_data['Name']
                    if billName == guestOption[3]:
                        billId = getBills_data['id']
                        payloadOrder = {
                            "ClientToken": os.getenv("DEMO_CLIENTTOKEN"),
                            "AccessToken": os.getenv("DAVID_ACCESSTOKEN"),
                            "ServiceId": "4d039787-d220-4929-af42-afcb0140c022",
                            "AccountId": GuestOptions[2],
                            "BillId": billId,
                            "ConsumptionUtc": target_datetime_str,
                            "Items": [
                                {
                                    "Name": "Cola",
                                    "UnitCount": 3,
                                    "UnitAmount": {
                                        "Currency": "EUR",
                                        "GrossValue": 5,
                                        "TaxCodes": [
                                            "NL-2019-R"
                                        ]
                                    },
                                    "AccountingCategoryId": "a9e5c4e7-37eb-45ad-bc76-b17800c0e0e9"
                                }
                            ]
                        }
                        payloadOrder = json.dumps(payloadOrder) # Convert the payload to JSON format
                        makeOrder = requests.post("https://api.mews-demo.com/api/connector/v1/orders/add", data=payloadOrder, headers=headers) # Send the POST request
                        makeOrder_data = makeOrder.json() # Parse the JSON response
        #
    else:
        GuestOptions = GuestOptions[0]
        payloadBill = {
            "ClientToken": os.getenv("DEMO_CLIENTTOKEN"),
            "AccessToken": os.getenv("DAVID_ACCESSTOKEN"),
            "Client": "Mews Client",
            "CustomerIds": [
                GuestOptions[2]
            ],
            "State": "Open",
            "Limitation": {
                "Count": 100,
            }
        }
        payloadBill = json.dumps(payloadBill) # Convert the payload to JSON format
        getBills = requests.post("https://api.mews-demo.com/api/connector/v1/bills/getAll", data=payloadBill, headers=headers) # Send the POST request
        getBills_data = getBills.json() # Parse the JSON response
        for bill in getBills_data['Bills']:
            billName = bill['Name']
            if billName == GuestOptions[3]:
                print('Bill name used: ', billName)
                billId = bill['Id']
                payloadOrder = {
                    "ClientToken": os.getenv("DEMO_CLIENTTOKEN"),
                    "AccessToken": os.getenv("DAVID_ACCESSTOKEN"),
                    "ServiceId": "4d039787-d220-4929-af42-afcb0140c022",
                    "AccountId": GuestOptions[2],
                    "BillId": billId,
                    "ConsumptionUtc": target_datetime_str,
                    "Items": [
                        {
                            "Name": "Cola",
                            "UnitCount": 3,
                            "UnitAmount": {
                                "Currency": "EUR",
                                "GrossValue": 5,
                                "TaxCodes": [
                                    "NL-2019-R"
                                ]
                            },
                            "AccountingCategoryId": "a9e5c4e7-37eb-45ad-bc76-b17800c0e0e9"
                        }
                    ]
                }
                payloadOrder = json.dumps(payloadOrder) # Convert the payload to JSON format
                makeOrder = requests.post("https://api.mews-demo.com/api/connector/v1/orders/add", data=payloadOrder, headers=headers) # Send the POST request
                makeOrder_data = makeOrder.json() # Parse the JSON response
    print('Order created')
    
