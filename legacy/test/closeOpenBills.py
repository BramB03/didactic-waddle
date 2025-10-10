import sys
import requests
import json
from datetime import datetime, timedelta, timezone
import random
import math
import pytz
import time
import pprint

startTime = time.time()
print("Start time: ", startTime)

logMessages = []

now_utc = datetime.now(timezone.utc)
now_utc_iso8601 = now_utc.strftime('%Y-%m-%dT%H:%M:%SZ')
now_utc_datetime = datetime.strptime(now_utc_iso8601, "%Y-%m-%dT%H:%M:%SZ")
nowUpdate = now_utc_datetime.replace(hour=10, minute=0, second=0)

headers = {
"Content-Type": "application/json"
}
URL = "https://api.mews-demo.com/api/connector/v1/"

ClientToken = "E0D439EE522F44368DC78E1BFB03710C-D24FB11DBE31D4621C4817E028D9E1D"
AccessToken = "BEC33DAD4C57410C9E6DB09600C7FB9B-310471532A30162E5B6F0EB4F4AD2BF"
Client = "Demo - Bram"
delta = -365

for i in range(0, 12):
    DeltaTwo = delta + 85
    start_day_delta = timedelta(days=delta)
    end_day_delta = timedelta(days=DeltaTwo)
    start_utc_datetime = nowUpdate + start_day_delta
    end_utc_datetime = nowUpdate + end_day_delta
    startFormatted = start_utc_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")
    print(startFormatted)
    endFormatted = end_utc_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")
    print(endFormatted)
    payloadBase = {
        "ClientToken": ClientToken,
        "AccessToken": AccessToken,
        "Client": Client,
        "State": "Open",
        "CreatedUtc": {
            "StartUtc": startFormatted,
            "EndUtc": endFormatted
        },
        "Limitation": {
            "Count": 1000
        }
    }

    json_payloadBase = json.dumps(payloadBase) # Convert the payload to JSON format
    getConfig = requests.post(URL + "bills/getAll", data=json_payloadBase, headers=headers) # Send the POST request
    if getConfig.status_code != 200:
        Error = "Getconfig" + str(getConfig)
        logMessages.append(str(Error))
    getConfig_data = getConfig.json() # Parse the JSON response
    delta = delta - 85
    if not getConfig_data['Bills']:
        print("No open bills found in the specified date range.")
        continue

    billsIds = []
    for bill in getConfig_data['Bills']:
        billId = bill['Id']
        accountId = bill['AccountId']
        billsIds.append([billId, accountId])

    index = 0
    for i in range(len(billsIds)):
        index += 1
        if index % 10 == 0:
            elapsedTime = time.time() - startTime
            print(f"Index: {index} | Elapsed time: {elapsedTime:.2f} seconds. Sleeping...")
            time.sleep(1)
            pprint.pprint("Log: " + str(logMessages))
            print("Resuming after sleep...")
        
        payloadGetPayments = {
            "ClientToken": ClientToken,
            "AccessToken": AccessToken,
            "Client": Client,
            "BillIds": [billsIds[i][0]],
            "Limitation": {
                "Count": 1000
            }
        }

        json_payloadGetPayments = json.dumps(payloadGetPayments)  # Convert the payload to JSON format
        getPayments = requests.post(URL + "payments/getAll", data=json_payloadGetPayments, headers=headers)  # Send the POST request
        if getPayments.status_code != 200:
            getPaymentItems = getPayments.json()
            Error = "GetPayments: " + str(getPaymentItems) + ", " + str(billsIds[i][0])
            logMessages.append(str(Error))
            continue
        getPaymentItems = getPayments.json()
        paymentItems = 0
        if not getPaymentItems['Payments']:
            for paymentItem in getPaymentItems['Payments']:
                paymentItemId = paymentItem['Amount']['GrossValue']
                paymentItems += paymentItemId
        
        getPayments_data = getPayments.json()  # Parse the JSON response
        payloadBillGetOrderItems = {
            "ClientToken": ClientToken,
            "AccessToken": AccessToken,
            "Client": Client,
            "BillIds": [billsIds[i][0]],
            "Limitation": {
                "Count": 1000
            }
        }

        json_payloadBillGetOrderItems = json.dumps(payloadBillGetOrderItems)  # Convert the payload to JSON format
        getOrderItems = requests.post(URL + "orderItems/getAll", data=json_payloadBillGetOrderItems, headers=headers)  # Send the POST request
        if getOrderItems.status_code != 200:
            Error = "GetOrderItems" + str(getOrderItems) + ", " + str(billsIds[i][0])
            logMessages.append(str(Error))
            continue
        getOrderItems_data = getOrderItems.json()  # Parse the JSON response
        orderItemsTotal = 0
        if not getOrderItems_data['OrderItems']:
            for orderItem in getOrderItems_data['OrderItems']:
                orderItemId = orderItem['Amount']['GrossValue']
                orderItemsTotal += orderItemId
            orderItemsTotal = round(orderItemsTotal, 2)

        openValue = orderItemsTotal + paymentItems

        if not getOrderItems_data and not getPaymentItems:
            try:
                payloadDeleteBill = {
                    "ClientToken": ClientToken,
                    "AccessToken": AccessToken,
                    "Client": Client,
                    "BillIds": [billsIds[i][0]]
                }
                json_payloadDeleteBill = json.dumps(payloadDeleteBill)  # Convert the payload to JSON format
                deleteBillResponse = requests.post(URL + "bills/delete", data=json_payloadDeleteBill, headers=headers)  # Send the POST request
                if deleteBillResponse.status_code != 200:
                    deleteBillResponse_data = deleteBillResponse.json()
                    Error = "DeleteBillResponse: " + str(deleteBillResponse_data) + ", " + str(billsIds[i][0])
                    logMessages.append(str(Error))
                    continue
                deleteBillResponse_data = deleteBillResponse.json()
                continue
            except Exception as e:
                Error = "Exception while deleting bill ID: " + str(billsIds[i][0]) + ": " + str(e)
                logMessages.append(str(Error))
                continue

        accountingCategoryId = "3a7bdc80-0191-4a3d-884b-b2f000c40389"
        if openValue != 0:
            payloadPayment = {
                "ClientToken": ClientToken,
                "AccessToken": AccessToken,
                "Client": Client,
                "AccountId": billsIds[i][1],
                "BillId": billsIds[i][0],
                "AccountingCategoryId": accountingCategoryId,
                "Amount": {
                    "Currency": "EUR",
                    "GrossValue": openValue
                },
                "Type": "CrossSettlement"
            }

            json_payloadPayment = json.dumps(payloadPayment)  # Convert the payload to JSON format
            paymentResponse = requests.post(URL + "payments/addExternal", data=json_payloadPayment, headers=headers)  # Send the POST request
            if paymentResponse.status_code != 200:
                paymentResponse_data = paymentResponse.json()
                Error = f"PaymentResponse: {paymentResponse_data}, BillId: {billsIds[i][0]}"
                logMessages.append(str(Error))
                continue
            paymentResponse_data = paymentResponse.json()  # Parse the JSON response

        try:
            PayloadbillsClose = {
                "ClientToken": ClientToken,
                "AccessToken": AccessToken,
                "Client": Client,
                "BillId": billsIds[i][0],
                "Type": "Receipt"
            }

            json_PayloadbillsClose = json.dumps(PayloadbillsClose)  # Convert the payload to JSON format
            billsCloseResponse = requests.post(URL + "bills/close", data=json_PayloadbillsClose, headers=headers)  # Send the POST request
            if billsCloseResponse.status_code != 200:
                billsCloseResponse_data = billsCloseResponse.json()
                Error = "BillsCloseResponse: " + str(billsCloseResponse_data) + ", " + str(billsIds[i][0])
                logMessages.append(str(Error))
                continue
            billsCloseResponse_data = billsCloseResponse.json()  # Parse the JSON response
        except Exception as e:
            payloadDeleteBill = {
                    "ClientToken": ClientToken,
                    "AccessToken": AccessToken,
                    "Client": Client,
                    "BillIds": [billsIds[i][0]]
                }
            json_payloadDeleteBill = json.dumps(payloadDeleteBill)  # Convert the payload to JSON format
            deleteBillResponse = requests.post(URL + "bills/delete", data=json_payloadDeleteBill, headers=headers)  # Send the POST request
            if deleteBillResponse.status_code != 200:
                deleteBillResponse_data = deleteBillResponse.json()
                Error = "DeleteBillResponse: " + str(deleteBillResponse_data) + ", " + str(billsIds[i][0])
                logMessages.append(str(Error))
                continue
            deleteBillResponse_data = deleteBillResponse.json()
        pprint.pprint("Log: " + str(logMessages))

    
print(logMessages)