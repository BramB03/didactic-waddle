import subprocess
import sys
import requests
import json, os
from datetime import datetime, timedelta, timezone
import random

headers = {
    "Content-Type": "application/json"
}

Client = "Mews Import Application"

now_utc = datetime.now(timezone.utc)
now_utc_iso8601 = now_utc.strftime('%Y-%m-%dT%H:%M:%SZ')
now_utc_datetime = datetime.strptime(now_utc_iso8601, "%Y-%m-%dT%H:%M:%SZ")
nowUpdate = now_utc_datetime.replace(hour=10, minute=0, second=0)

cancelledReservations = 0

ClientToken = os.getenv("DEMO_CLIENTTOKEN")
AccessToken = os.getenv("DAVID_ACCESSTOKEN")

payload1 = {
    "ClientToken": ClientToken,
    "AccessToken": AccessToken,
    "Client": Client,
    "Limitation":{ "Count": 50 }
}

json_payload1 = json.dumps(payload1) # Convert the payload to JSON format
getService = requests.post("https://api.mews-demo.com/api/connector/v1/services/getAll", data=json_payload1, headers=headers) # Send the POST request
if getService.status_code != 200:
    getService_error = getService.json()
    sys.exit(getService_error)
getService_data = getService.json() # Parse the JSON response
service_ids_list = getService_data["Services"]
bookable_active_ids = [service['Id'] for service in service_ids_list if service.get('Data', {}).get('Discriminator') == 'Bookable' and service.get('IsActive')]
for bookable_service in bookable_active_ids:
    delta = -180
    for _ in range(10):
        DeltaTwo = delta + 90
        start_day_delta = timedelta(days=delta)
        end_day_delta = timedelta(days=DeltaTwo)
        start_utc_datetime = nowUpdate + start_day_delta
        end_utc_datetime = nowUpdate + end_day_delta
        startFormatted = start_utc_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")
        print(startFormatted)
        endFormatted = end_utc_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")
        # JSON payload to be sent in the POST request
        payload1 = {
            "ClientToken": ClientToken,
            "AccessToken": AccessToken,
            "Client": Client,
            "ServiceIds": [
                bookable_service,
            ],
            "ScheduledStartUtc": {
                "StartUtc": startFormatted,
                "EndUtc": endFormatted
            },
            "States": [
                "Confirmed"
            ],
            "Limitation":{
                "Count": 999
            }
        }
        json_payload1 = json.dumps(payload1) # Convert the payload to JSON format
        getRes = requests.post("https://api.mews-demo.com/api/connector/v1/reservations/getall/2023-06-06", data=json_payload1, headers=headers) # Send the POST request
        if getRes.status_code != 200:
            printerror = getRes.json()
            print(printerror)
        getRes_data = getRes.json() # Parse the JSON response
        reservation_ids_list = getRes_data["Reservations"]
        reservations_active_ids = [reservation['Id'] for reservation in reservation_ids_list if reservation.get('CancelledUtc') == None and reservation.get('State') == 'Confirmed']
        for id in reservation_ids_list:
            cancelledReservations = cancelledReservations + 1
        if reservations_active_ids == []:
            print("Timeslot is empty")
        else:
            print(reservations_active_ids)
            payload2 = {
                "ClientToken": ClientToken,
                "AccessToken": AccessToken,
                "Client": Client,
                "ReservationIds": reservations_active_ids,
                "PostCancellationFee": "false",
                "Notes": "Cancellation through Connector API"
                }
            json_payload2 = json.dumps(payload2) # Convert the payload to JSON format
            getResult = requests.post("https://api.mews-demo.com/api/connector/v1/reservations/cancel", data=json_payload2, headers=headers) # Send the POST request
            print(getResult)
            if getResult.status_code != 200:
                printerror = getResult.json()
                print(printerror)
        delta = delta + 90
        
print(cancelledReservations, ' were cancelled')
