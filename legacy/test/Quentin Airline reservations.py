import sys
import requests
import json
from datetime import datetime, timedelta, timezone
import random
import math
import pytz
import time
from TimeZone import adjust_timezone
from pprint import pprint


headers = {
"Content-Type": "application/json"
}
URL = "https://api.mews-demo.com/api/connector/v1/"

ClientToken = "E0D439EE522F44368DC78E1BFB03710C-D24FB11DBE31D4621C4817E028D9E1D"
AccessToken = "C2FFDD8B9DAA4458BF9CB09E00C1A82D-1FC86D9F087CC822F96527F1E6B1102"
Client = "Demo - Quentin"

ServiceId = "d0b2c517-2c46-4547-b816-aec8007ab3f2"
TimeZoneLocation = "Europe/Amsterdam"
ChainId = "bb7dd3bc-6363-4a46-9b7b-aec8007ab21b"ç
RateId = "612940cb-e9d0-467f-95cd-aec8007ab5c2"
AgeCategoryId = "03b316d0-b05c-498b-8999-aec8007ab451"
CompanyId = "bf8aea04-8bc5-46c0-9665-b260010cda71"
pricePerNight = 150
SpaceIds = [[('c5395549-bb2e-4a47-bd6a-aec900e38da4',
   '827a7e23-4225-4e6f-aa93-aeca0091b338'),
  ('c5395549-bb2e-4a47-bd6a-aec900e38da4',
   'e3aa8e5b-790c-46b1-af68-b2680105b31f'),
  ('c5395549-bb2e-4a47-bd6a-aec900e38da4',
   '11c603ac-bc48-4f44-a8e4-b2680105b31f'),
  ('c5395549-bb2e-4a47-bd6a-aec900e38da4',
   '4a1a68d2-0af6-421d-8295-b2680105b31f'),
  ('c5395549-bb2e-4a47-bd6a-aec900e38da4',
   'e95accbb-2a5b-49fa-96ab-b2680105b320'),
  ('c5395549-bb2e-4a47-bd6a-aec900e38da4',
   '614cccd1-7527-42ef-af09-b2680105b320'),
  ('c5395549-bb2e-4a47-bd6a-aec900e38da4',
   '54a9a1ad-8546-4dba-bc95-b2680105b320'),
  ('c5395549-bb2e-4a47-bd6a-aec900e38da4',
   '24745179-36cb-4493-9013-b2680105b320'),
  ('c5395549-bb2e-4a47-bd6a-aec900e38da4',
   '0f740d7e-fe1f-44f7-b7e3-b2680105b320'),
  ('c5395549-bb2e-4a47-bd6a-aec900e38da4',
   'dd7323e7-7db6-48d7-b35d-b2680105b320'),
  ('c5395549-bb2e-4a47-bd6a-aec900e38da4',
   '838953f6-644f-4c2a-8596-b2680105b320'),
  ('c5395549-bb2e-4a47-bd6a-aec900e38da4',
   'e622c2e4-accc-41ea-8b57-b2680105b320'),
  ('c5395549-bb2e-4a47-bd6a-aec900e38da4',
   'bdae9e72-3dbb-4d4b-859a-b2680105b320'),
  ('c5395549-bb2e-4a47-bd6a-aec900e38da4',
   '3abecf22-c86e-43e2-8578-b2680105b320'),
  ('c5395549-bb2e-4a47-bd6a-aec900e38da4',
   '7917ad33-5473-41bc-85aa-b2680105b320'),
  ('c5395549-bb2e-4a47-bd6a-aec900e38da4',
   'f99c7c35-becc-4392-a389-b2680105b320'),
  ('c5395549-bb2e-4a47-bd6a-aec900e38da4',
   'e0c3dc24-67bb-4a2e-b446-b2680105b320'),
  ('c5395549-bb2e-4a47-bd6a-aec900e38da4',
   'e5c818db-6963-4a41-ac62-b2680105b320'),
  ('97751b14-bbb3-4355-baaa-aeca00f3676a',
   'dbac576d-d626-4b32-b28b-b2680109e514'),
  ('c5395549-bb2e-4a47-bd6a-aec900e38da4',
   '10e99886-2aa2-4f81-a918-aec900e40b75'),
  ('052ca527-f47a-4c29-95db-aeca0096f7e0',
   '2416f806-be27-48db-a0be-aeca0098322e'),
  ('3e52ae43-6b7c-4b09-8c1b-aeca0097632b',
   '5bafeb07-3384-446b-b834-afbf00a4a9dd'),
  ('018da052-3c1c-4d80-bb8a-b23a00f5ea18',
   'e7bd78e5-4bbd-4713-89a6-af5b00bb8f3f'),
  ('052ca527-f47a-4c29-95db-aeca0096f7e0',
   'ac14b402-5369-49de-8317-af5b00bbcd4e'),
  ('570fcfb9-ffa5-4e34-9494-aedf009b4d34',
   '55a77fab-a3e1-4864-9d96-aedf009c4955'),
  ('570fcfb9-ffa5-4e34-9494-aedf009b4d34',
   '7ab977a2-96e7-44bc-9b58-aedf009cf113'),
  ('9e609486-9cdd-4e66-9167-aedf009f8dce',
   '34885695-a4c2-452c-8344-aedf00a021e7')],
 [('c5395549-bb2e-4a47-bd6a-aec900e38da4',
   '0ccab128-702c-43c3-a108-aeca0091d427'),
  ('c5395549-bb2e-4a47-bd6a-aec900e38da4',
   '99092536-416e-4dcb-93b0-b2680105b31f'),
  ('c5395549-bb2e-4a47-bd6a-aec900e38da4',
   'e8057baf-838a-4489-80f2-b2680105b31f'),
  ('c5395549-bb2e-4a47-bd6a-aec900e38da4',
   'ea5fb164-fdf8-4634-8542-b2680105b31f'),
  ('c5395549-bb2e-4a47-bd6a-aec900e38da4',
   'd0b76e24-045d-4ab9-9881-b2680105b320'),
  ('c5395549-bb2e-4a47-bd6a-aec900e38da4',
   '16511aa0-f9d6-4f7c-8c29-b2680105b320'),
  ('c5395549-bb2e-4a47-bd6a-aec900e38da4',
   '436d0637-9a9b-4a31-af1e-b2680105b320'),
  ('c5395549-bb2e-4a47-bd6a-aec900e38da4',
   'c1d09665-53d8-443d-aad7-b2680105b320'),
  ('c5395549-bb2e-4a47-bd6a-aec900e38da4',
   '9a5f8559-8614-4326-a0cb-b2680105b320'),
  ('c5395549-bb2e-4a47-bd6a-aec900e38da4',
   '7630bc25-6cb9-4612-a170-b2680105b320'),
  ('c5395549-bb2e-4a47-bd6a-aec900e38da4',
   'fa64d10c-0fcc-4610-9e6c-b2680105b320'),
  ('c5395549-bb2e-4a47-bd6a-aec900e38da4',
   '34a346c5-d11b-48c0-98a1-b2680105b320'),
  ('c5395549-bb2e-4a47-bd6a-aec900e38da4',
   '5a99a382-72ef-44dd-b53c-b2680105b320'),
  ('c5395549-bb2e-4a47-bd6a-aec900e38da4',
   '95761e8d-d46e-4974-8d92-b2680105b320'),
  ('c5395549-bb2e-4a47-bd6a-aec900e38da4',
   '620b17a8-f1f4-447e-8c93-b2680105b320'),
  ('c5395549-bb2e-4a47-bd6a-aec900e38da4',
   '58b7d360-0369-4bae-833d-b2680105b320'),
  ('c5395549-bb2e-4a47-bd6a-aec900e38da4',
   'bc227f30-d02e-4e59-8dd5-b2680105b320'),
  ('97751b14-bbb3-4355-baaa-aeca00f3676a',
   '445ca257-dc79-4157-a027-b2680105b320'),
  ('97751b14-bbb3-4355-baaa-aeca00f3676a',
   'b9b31f97-91bc-4641-99cf-b2680109e514'),
  ('c5395549-bb2e-4a47-bd6a-aec900e38da4',
   'ec88628f-0ba3-4151-a39f-aec900e3eec1'),
  ('018da052-3c1c-4d80-bb8a-b23a00f5ea18',
   '2416f806-be27-48db-a0be-aeca0098322e'),
  ('052ca527-f47a-4c29-95db-aeca0096f7e0',
   'c69b6032-bd85-494e-b0d3-aeca00985d0e'),
  ('052ca527-f47a-4c29-95db-aeca0096f7e0',
   '069322e4-30e4-4c09-9aa4-af5b00bba332'),
  ('97751b14-bbb3-4355-baaa-aeca00f3676a',
   '7aa519eb-47a7-4947-80af-aedd00f8c45d'),
  ('570fcfb9-ffa5-4e34-9494-aedf009b4d34',
   'bf6eeffc-48a6-4a3e-aa7f-aedf009c710a'),
  ('9e609486-9cdd-4e66-9167-aedf009f8dce',
   '3c7143a8-b2f5-4c6b-8a79-aedf009fd799'),
  ('9e609486-9cdd-4e66-9167-aedf009f8dce',
   'd37d112b-f968-407a-8f77-aedf00a0349a')],
 [('c5395549-bb2e-4a47-bd6a-aec900e38da4',
   'a44871ff-b837-4b2c-9166-aeca0091e702'),
  ('c5395549-bb2e-4a47-bd6a-aec900e38da4',
   'c5d51d16-f63f-4327-943a-b2680105b31f'),
  ('c5395549-bb2e-4a47-bd6a-aec900e38da4',
   '4be7b949-5bf5-4e67-9dfa-b2680105b31f'),
  ('c5395549-bb2e-4a47-bd6a-aec900e38da4',
   '3c579337-be00-4bb9-9191-b2680105b31f'),
  ('c5395549-bb2e-4a47-bd6a-aec900e38da4',
   'f1a89eb1-8ae7-43a2-a2df-b2680105b320'),
  ('c5395549-bb2e-4a47-bd6a-aec900e38da4',
   '3515bbda-d360-4c10-a61a-b2680105b320'),
  ('c5395549-bb2e-4a47-bd6a-aec900e38da4',
   'da0eaf66-6baf-45ee-a25b-b2680105b320'),
  ('c5395549-bb2e-4a47-bd6a-aec900e38da4',
   '96a110a7-3a06-40ed-9d6f-b2680105b320'),
  ('c5395549-bb2e-4a47-bd6a-aec900e38da4',
   '469236ab-f427-4963-891b-b2680105b320'),
  ('c5395549-bb2e-4a47-bd6a-aec900e38da4',
   '85e1ff56-65b8-4636-954f-b2680105b320'),
  ('c5395549-bb2e-4a47-bd6a-aec900e38da4',
   '00827b41-8ad1-4991-853b-b2680105b320'),
  ('c5395549-bb2e-4a47-bd6a-aec900e38da4',
   '48d18b67-328f-408f-ae36-b2680105b320'),
  ('c5395549-bb2e-4a47-bd6a-aec900e38da4',
   'af3b42f6-bbc5-4f67-8614-b2680105b320'),
  ('c5395549-bb2e-4a47-bd6a-aec900e38da4',
   '487a57c2-e085-498c-9a1c-b2680105b320'),
  ('c5395549-bb2e-4a47-bd6a-aec900e38da4',
   '93bd26f4-2944-493c-a724-b2680105b320'),
  ('c5395549-bb2e-4a47-bd6a-aec900e38da4',
   '8af2d9fa-703f-47c3-86c0-b2680105b320'),
  ('c5395549-bb2e-4a47-bd6a-aec900e38da4',
   'd4357a63-6880-4ea0-9653-b2680105b320'),
  ('97751b14-bbb3-4355-baaa-aeca00f3676a',
   '50948e01-e944-4d68-9782-b2680105b320'),
  ('97751b14-bbb3-4355-baaa-aeca00f3676a',
   '49fea7fe-0151-4f09-9f98-b2680109e514'),
  ('3e52ae43-6b7c-4b09-8c1b-aeca0097632b',
   'ba9eccc3-c12b-4217-a852-aeca00979a4d'),
  ('052ca527-f47a-4c29-95db-aeca0096f7e0',
   '7cfbd12b-4b22-4fbf-84fe-aeca0098476a'),
  ('018da052-3c1c-4d80-bb8a-b23a00f5ea18',
   'c69b6032-bd85-494e-b0d3-aeca00985d0e'),
  ('052ca527-f47a-4c29-95db-aeca0096f7e0',
   '0b4bf1bb-a51d-435f-8bc1-af5b00bbb0df'),
  ('77e6cd99-0690-4616-98be-aedf009aaae8',
   '282963d3-c19f-48e3-b497-aedf009be221'),
  ('570fcfb9-ffa5-4e34-9494-aedf009b4d34',
   '9eea04c7-652c-4eb8-9aa0-aedf009c94d8'),
  ('9e609486-9cdd-4e66-9167-aedf009f8dce',
   '04351f5c-18eb-42bc-b6b5-aedf009ff34a'),
  ('9e609486-9cdd-4e66-9167-aedf009f8dce',
   '2a3d439f-a510-4323-8652-aedf00a0509f')],
 [('c5395549-bb2e-4a47-bd6a-aec900e38da4',
   'dd8cba4c-87a1-450c-a347-aeca0091fecb'),
  ('c5395549-bb2e-4a47-bd6a-aec900e38da4',
   'ead0b5a3-6c40-41d4-9f62-b2680105b31f'),
  ('c5395549-bb2e-4a47-bd6a-aec900e38da4',
   '114bc77f-41dd-4dfe-a091-b2680105b31f'),
  ('c5395549-bb2e-4a47-bd6a-aec900e38da4',
   '56cc8501-ab60-46b5-9429-b2680105b320'),
  ('c5395549-bb2e-4a47-bd6a-aec900e38da4',
   '1ff08479-0678-42f3-8b5c-b2680105b320'),
  ('c5395549-bb2e-4a47-bd6a-aec900e38da4',
   '4d53c794-f584-4b25-862b-b2680105b320'),
  ('c5395549-bb2e-4a47-bd6a-aec900e38da4',
   '52d5354e-23a1-461c-9af8-b2680105b320'),
  ('c5395549-bb2e-4a47-bd6a-aec900e38da4',
   '11b5c5b4-7039-4c20-98e5-b2680105b320'),
  ('c5395549-bb2e-4a47-bd6a-aec900e38da4',
   '8b05f9ad-67b1-4e82-b8fd-b2680105b320'),
  ('c5395549-bb2e-4a47-bd6a-aec900e38da4',
   '0edfbe73-8394-4c0e-8cf3-b2680105b320'),
  ('c5395549-bb2e-4a47-bd6a-aec900e38da4',
   '57c5ea57-8bcc-498d-af14-b2680105b320'),
  ('c5395549-bb2e-4a47-bd6a-aec900e38da4',
   'b96a9f24-18f7-4b72-8d14-b2680105b320'),
  ('c5395549-bb2e-4a47-bd6a-aec900e38da4',
   'db338e96-5876-4506-95c3-b2680105b320'),
  ('c5395549-bb2e-4a47-bd6a-aec900e38da4',
   'f40e217e-0180-4aee-a27d-b2680105b320'),
  ('c5395549-bb2e-4a47-bd6a-aec900e38da4',
   '863682f4-e1d4-49ea-8dbd-b2680105b320'),
  ('c5395549-bb2e-4a47-bd6a-aec900e38da4',
   '19520d1d-0036-4b54-a1c3-b2680105b320'),
  ('c5395549-bb2e-4a47-bd6a-aec900e38da4',
   '5ea624a5-93d8-422a-876a-b2680105b320'),
  ('97751b14-bbb3-4355-baaa-aeca00f3676a',
   '89f48d15-901b-4421-8756-b2680109e514'),
  ('c5395549-bb2e-4a47-bd6a-aec900e38da4',
   'cd6454be-5837-4a44-ba6e-aeca009082a5'),
  ('052ca527-f47a-4c29-95db-aeca0096f7e0',
   'c7a27329-d55f-46ac-8c0d-aeca0097c084'),
  ('018da052-3c1c-4d80-bb8a-b23a00f5ea18',
   '7cfbd12b-4b22-4fbf-84fe-aeca0098476a'),
  ('052ca527-f47a-4c29-95db-aeca0096f7e0',
   'e7bd78e5-4bbd-4713-89a6-af5b00bb8f3f'),
  ('052ca527-f47a-4c29-95db-aeca0096f7e0',
   'd732f1cc-419c-486f-ade5-af5b00bbbe05'),
  ('570fcfb9-ffa5-4e34-9494-aedf009b4d34',
   '1a47e762-0c5e-4138-8612-aedf009c2577'),
  ('570fcfb9-ffa5-4e34-9494-aedf009b4d34',
   '8c886243-3b30-47da-b21f-aedf009cbccc'),
  ('9e609486-9cdd-4e66-9167-aedf009f8dce',
   '4ceaacfd-9994-4fe6-b97a-aedf00a00dd5')]]

CheckInTimeHour = [ 6, 13, 14, 20]
CheckInTimeMinute = [ 35, 25, 10, 30]
CheckOutTimeHour = [ 5, 12, 13, 19] 
CheckOutTimeMinute = [ 45, 55, 30, 30]
FlightNumber = ["41", "39", "43", "37"]
FlightNumberLoop = 2

index = 0
createdReservations = 0
failedRes = 0
reservationsPerGroup = 2

# Get the current UTC time and initialize FirstDayUTC and NextDayUTC
utc_now = datetime.now(pytz.utc)
FirstDayUTC = utc_now
NextDayUTC = FirstDayUTC + timedelta(days=1)

#FirstDayUTC = FirstDayUTC + timedelta(days=1)
#NextDayUTC = NextDayUTC + timedelta(days=1)

for i in range(3):
    for j in range(2):
        for j in range(2):
            FirstDayUTC = FirstDayUTC.replace(hour=CheckInTimeHour[FlightNumberLoop], minute=CheckInTimeMinute[FlightNumberLoop], second=0, microsecond=0)
            NextDayUTC = NextDayUTC.replace(hour=CheckOutTimeHour[FlightNumberLoop], minute=CheckOutTimeMinute[FlightNumberLoop], second=0, microsecond=0)
            FirstDayUTCPayload, NextDayUTCPayload = adjust_timezone(FirstDayUTC, NextDayUTC, CheckInTimeHour[FlightNumberLoop], CheckOutTimeHour[FlightNumberLoop], TimeZoneLocation)
            # Convert the date string to a datetime object
            FirstDayUTCPayload = datetime.strptime(FirstDayUTCPayload, "%Y-%m-%d %H:%M:%S")
            FirstDayUTCPayload = FirstDayUTCPayload.replace(tzinfo=timezone.utc)
            NextDayUTCPayload = datetime.strptime(NextDayUTCPayload, "%Y-%m-%d %H:%M:%S")
            NextDayUTCPayload = NextDayUTCPayload.replace(tzinfo=timezone.utc)
            FirstDayUTCPayload = FirstDayUTCPayload.strftime('%Y-%m-%dT%H:%M:%SZ')
            NextDayUTCPayload = NextDayUTCPayload.strftime('%Y-%m-%dT%H:%M:%SZ')
            
            #Create new customer
            CustomerName = "Qatar flight " + FlightNumber[FlightNumberLoop] + " " + str(FirstDayUTC.date())
            FlightNumberLoop = FlightNumberLoop + 1
            
            if FlightNumberLoop == 4:
                FlightNumberLoop = 0
            
            payload6 = {
                "ClientToken": ClientToken,
                "AccessToken": AccessToken,
                "Client": Client,
                "ChainId": ChainId,
                "OverwriteExisting": 'true',
                "LastName": CustomerName
            }
            
            json_payload6 = json.dumps(payload6) # Convert the payload to JSON format
            getGuest_data = requests.post(URL + "customers/add", data=json_payload6, headers=headers) # Send the POST request
            if getGuest_data.status_code != 200:
                Error = "getGuest_data" + str(getGuest_data)
                continue
            getGuestIdPlural = getGuest_data.json()
            GuestId = getGuestIdPlural.get('Id')
            reservationsPayload = []
            for indx in range(reservationsPerGroup):
                miniPayload = {
                    "Identifier": str(indx),
                    "State": "Confirmed",
                    "StartUtc": FirstDayUTCPayload,
                    "EndUtc": NextDayUTCPayload,
                    "CustomerId": GuestId,
                    "CompanyId": CompanyId,
                    "RequestedCategoryId": list(SpaceIds[j][indx])[0],
                    "RateId": RateId,
                    "TimeUnitPrices": [
                        {
                            "Index": 0,
                            "Amount": {
                            "Currency": "EUR",
                            "GrossValue": pricePerNight,
                            "TaxCodes": [
                                    "FR-R"
                                ]
                            }
                        }
                        ],
                        "PersonCounts": [
                            {
                            "AgeCategoryId": AgeCategoryId,
                            "Count": 1
                            }
                        ]
                }
                reservationsPayload.append(miniPayload)
                
            Payload = {
                "ClientToken": ClientToken,
                "AccessToken": AccessToken,
                "Client": Client,
                "ServiceId": ServiceId,
                "SendConfirmationEmail": None,
                "CheckOverbooking": False,
                
                "Reservations": reservationsPayload
            }
            
            json_payload = json.dumps(Payload) # Convert the payload to JSON format
            print(json_payload)
            ResponseJson = requests.post(URL + "reservations/add", data=json_payload, headers=headers) # 
            Response = ResponseJson.json()
            ReservationIds = [item["Reservation"]["Id"] for item in Response["Reservations"]]
            print(ReservationIds)
            Updates = [
                {
                "ReservationId": ReservationIds[i],
                "RequestedCategoryId": {
                    "Value": list(SpaceIds[j])[i][0]
                },
                "AssignedResourceId": {
                    "Value": list(SpaceIds[j])[i][1]
                },
                "AssignedResourceLocked": {
                    "Value": False
                }
                }   
                for i in range(reservationsPerGroup)
            ]
            
            PayloadUpdate = {
                "ClientToken": ClientToken,
                "AccessToken": AccessToken,
                "Client": Client,
                "ReservationUpdates": Updates  
            }
            json_PayloadUpdate = json.dumps(PayloadUpdate) # Convert the payload to JSON format
            print(json_PayloadUpdate)
            ResponseUpdateJson = requests.post(URL + "reservations/update", data=json_PayloadUpdate, headers=headers) # 
            ResponseUpdate = ResponseUpdateJson.json()
            if ResponseJson.status_code != 200:
                print(ResponseUpdate)
                
            time.sleep(0.5)
            UpdatesTwo = [
                {
                "ReservationId": ReservationIds[i],
                "AssignedResourceLocked": {
                    "Value": True
                }
                }   
                for i in range(reservationsPerGroup)
            ]
            PayloadUpdatesTwo = {
                "ClientToken": ClientToken,
                "AccessToken": AccessToken,
                "Client": Client,
                "ReservationUpdates": UpdatesTwo  
            }
            json_PayloadUpdateTwo = json.dumps(PayloadUpdatesTwo) # Convert the payload to JSON format
            ResponseUpdateTwoJson = requests.post(URL + "reservations/update", data=json_PayloadUpdateTwo, headers=headers) # 
            ResponseUpdateTwo = ResponseUpdateTwoJson.json()
            time.sleep(0.5)
 
        FirstDayUTC = FirstDayUTC + timedelta(days=1)
        NextDayUTC = NextDayUTC + timedelta(days=1)
        
    if ResponseJson.status_code == 200:
        createdReservations = createdReservations + 1
        print("Reservation group created: ", CustomerName)
        time.sleep(1)
    else:
        Response = ResponseJson.json()
        failedRes = failedRes +1
        print(failedRes)
        print(Response)
        time.sleep(0.1)
    if failedRes == 3:
        print("Skip to next day")
        time.sleep(0.1)
        break
    
    index = index + 1