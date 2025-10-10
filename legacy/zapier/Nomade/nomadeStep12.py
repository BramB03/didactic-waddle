import json
import pprint
data_string = {"2eeb3f13-c0fc-483f-9bda-b2a500266a2a": [["d45a1cd5-0cb9-4c9e-8c67-b131011787d6", "USD", 98.33, "MX-S"], ["f74e2148-94ad-493b-8d27-b131011856ee", "USD", 26.87, "MX-Z"], ["27b5726a-d4db-476f-8e8a-b13101180e24", "USD", 56.07, "MX-S"]], "57bc4b0a-ade9-4243-9435-b2a40038b23a": [["d45a1cd5-0cb9-4c9e-8c67-b131011787d6", "USD", 148.34, "MX-S"], ["f74e2148-94ad-493b-8d27-b131011856ee", "USD", 29.5, "MX-Z"], ["27b5726a-d4db-476f-8e8a-b13101180e24", "USD", 21.19, "MX-S"]], "b97fe550-c798-4965-8349-b2a301782757": [["d45a1cd5-0cb9-4c9e-8c67-b131011787d6", "USD", 32.0, "MX-S"], ["f74e2148-94ad-493b-8d27-b131011856ee", "USD", 8.35, "MX-Z"], ["27b5726a-d4db-476f-8e8a-b13101180e24", "USD", 16.0, "MX-S"]], "e51a7929-5529-479a-9813-b2a30119d1a9": [["27b5726a-d4db-476f-8e8a-b13101180e24", "USD", 5.19, "MX-S"], ["f74e2148-94ad-493b-8d27-b131011856ee", "USD", 0.9, "MX-Z"]]}
foodExcel = "be56fdac-0748-4cda-959f-b22800e876ca"
beverageExcel = "2b960b6a-c561-49d1-a2e5-b22800e876ca"
gratuityExcel = "c5b58257-6a10-4833-93a5-b22800e876ca"
otherExcel = "d45a1cd5-0cb9-4c9e-8c67-b131011787d6"
foodExcelOld = "27b5726a-d4db-476f-8e8a-b13101180e24"
beverageExcelOld = "f74e2148-94ad-493b-8d27-b131011856ee"
gratuityExcelOld = "99a4bc4a-1c1c-4129-bb63-b22800e876ca"
otherExcelOld = "797c8740-f38e-4fdf-8db7-b13101184a61"

#data_string = json.loads(data_string)

for key in data_string:
    for i in range(len(data_string[key])):
        if data_string[key][i][0] == foodExcelOld:
            data_string[key][i][0] = foodExcel
        elif data_string[key][i][0] == beverageExcelOld:
            data_string[key][i][0] = beverageExcel
        elif data_string[key][i][0] == gratuityExcelOld:
            data_string[key][i][0] = gratuityExcel
        elif data_string[key][i][0] == otherExcelOld:
            data_string[key][i][0] = otherExcel

payloads = []
# Iterate through each order in the data
for accountingCategoryId, items in data_string.items():
    for item in items:
        nettValue = float(item[2])  # Convert the net value to float
        payload = {
            "Name": item[0],  # Use the first element (ID) as Name
            "UnitCount": 1,
            "UnitAmount": {
                "Currency": item[1],  # Currency from the second element
                "NetValue": nettValue,
                "TaxCodes": [
                    item[3]  # TaxCode from the fourth element
                ]
            },
            "AccountingCategoryId": accountingCategoryId  # Use the accounting category ID
        }
        payloads.append(payload)

# Print the generated payloads
pprint.pprint(payloads)

