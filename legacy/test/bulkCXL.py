import subprocess
import sys
import requests
import json
from datetime import datetime, timedelta, timezone
import random
'''
ClientToken = "E0D439EE522F44368DC78E1BFB03710C-D24FB11DBE31D4621C4817E028D9E1D"
AccessToken = "C2FFDD8B9DAA4458BF9CB09E00C1A82D-1FC86D9F087CC822F96527F1E6B1102"
Client = "Demo - Quentin"
'''

headers = {
    "Content-Type": "application/json"
}

#RIA
#ClientToken = "8A63FE45937F4FD6B797B10800EBBCDC-BB365A9A28E91ECC0F6F461336D6AAF"
#AccessToken = "F387FDEDEA8F4F9E8496B177008FF20D-02211951E4196B37560F023E4B97533"
#Solvang
#AccessToken = "FCF0D6ED13CA4C22863EB20900BE02BB-B7B8D228A4959E33689610F0AA9048C"
Client = "Mews Import Application"

now_utc = datetime.now(timezone.utc)
now_utc_iso8601 = now_utc.strftime('%Y-%m-%dT%H:%M:%SZ')
now_utc_datetime = datetime.strptime(now_utc_iso8601, "%Y-%m-%dT%H:%M:%SZ")
nowUpdate = now_utc_datetime.replace(hour=10, minute=0, second=0)

cancelledReservations = 0

ClientToken = "E0D439EE522F44368DC78E1BFB03710C-D24FB11DBE31D4621C4817E028D9E1D"
AccessToken = "FA313B35B0AA44F9A985B2DE0076DC0D-B2ED620854C06E840EA6857E5306661"
Client = "St Clement - Demo"

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
