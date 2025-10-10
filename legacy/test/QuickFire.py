import json
import requests

headers = {
"Content-Type": "application/json"
}
URL = "https://api.mews-demo.com/api/connector/v1/"

# Importing the input variables
item_id_str = input_data.get('orderId', '').split('|')
accountId = input_data.get('accountId', '')
original_prod_id = input_data.get('originalProdId', '')
newProdList = input_data.get('newProdList', '').split(',')
unitCount = input_data.get('unitCount', '')
deadlineUtc = input_data.get('deadlineUtc', '')
billId = input_data.get('billId', '')

try:
  newProdListTwo = input_data['newProdListTwo']
except KeyError:
  newProdListTwo = ''
if newProdListTwo != '':
  newProdList.append(newProdListTwo)

productOrders = []
for productId in newProdList:
    productOrder = {
        "ProductId": productId,
        "Count": int(unitCount)
    }
    productOrders.append(productOrder)

payloadAdd = {
"ClientToken": "E0D439EE522F44368DC78E1BFB03710C-D24FB11DBE31D4621C4817E028D9E1D",
"AccessToken": "133F1ED981804738A045B061008A726C-A06E372F46FA4E3ABAB5951839547ED",
"Client": "Sample Client 1.0.0",
"ServiceId": "17cc75d8-f78e-43d9-b207-b2eb0092b394",
"AccountId": accountId,
"BillId": billId,
"ProductOrders": productOrders
}
jsonPayloadAdd = json.dumps(payloadAdd) # Convert the payload to JSON format
print(payloadAdd)
reservationsAddProductResponseJson = requests.post(URL + "orders/add", data=jsonPayloadAdd, headers=headers)
reservationsAddProductResponse = reservationsAddProductResponseJson.json()
print(reservationsAddProductResponse)

orderItemsCancelResponse = None  # Initialize to avoid reference before assignment

if reservationsAddProductResponse.status_code == 200:
    #payload to remove the products
    payload = {
    "ClientToken": "E0D439EE522F44368DC78E1BFB03710C-D24FB11DBE31D4621C4817E028D9E1D",
    "AccessToken": "133F1ED981804738A045B061008A726C-A06E372F46FA4E3ABAB5951839547ED",
    "Client": "Sample Client 1.0.0",
    "OrderItemIds": item_id_str
    }
    print(payload)

    jsonPayload = json.dumps(payload) # Convert the payload to JSON format
    orderItemsCancelResponse = requests.post(URL + "orderItems/cancel", data=jsonPayload, headers=headers) # Send the POST request
    orderItemsCancel = orderItemsCancelResponse.json()
    print(orderItemsCancel)
elif reservationsAddProductResponse.status_code != 200 or (orderItemsCancelResponse is not None and getattr(orderItemsCancelResponse, "status_code", None) != 200):
  Description = "Please review products on bill Id: " + billId + " or account id: " + accountId + "!"
  payloadTask = {
    "ClientToken": "E0D439EE522F44368DC78E1BFB03710C-D24FB11DBE31D4621C4817E028D9E1D",
    "AccessToken": "133F1ED981804738A045B061008A726C-A06E372F46FA4E3ABAB5951839547ED",
    "Client": "Sample Client 1.0.0",
    "Name": "Product conversion failed",
    "Description": Description,
    "DeadlineUtc": deadlineUtc,
    "DepartmentId": "8f60116c-ae49-4242-a0f8-affe00a5a370"
  }
  jsonPayloadTask = json.dumps(payloadTask) # Convert the payload to JSON format
  orderItemsCancelResponse = requests.post(URL + "tasks/add", data=jsonPayloadTask, headers=headers)
  orderItemsCancelResponseJson = orderItemsCancelResponse.json()
  print(orderItemsCancelResponseJson)
