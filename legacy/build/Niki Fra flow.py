import json
import ast
import re
from collections import defaultdict

# Retrieve the input data
account_id = input_data.get('accountId', '')
data = input_data.get('data', '[]')

parsed_data = ast.literal_eval(data)
print(parsed_data)
def createItem(Name, Count, Value, Taxcode, AccountingCategory):
  payload = {
    "Name": Name,
    "UnitCount": Count,
    "UnitAmount": {
        "Currency": "EUR",
        "GrossValue": float(Value),
        "TaxCodes": [
            Taxcode
        ]
    },
    "AccountingCategoryId": AccountingCategory
  }
  return payload

productMapping = {
    "f6baa55c-5ae3-480c-8c1d-b035010ea738.adult": {
        "Category": "[R1] Reindeer Express (25m) - Adult",
        "Name": [
            "[R1] Reindeer Express (25m) - C",
            "[R1] Reindeer Express (25m) - M"
        ],
        "Value": [
            42.18,
            46.82
        ],
        "Taxcode": [
            "FI-2025-0%",
            "FI-2025-25.5%"
        ],
        "AccountingCategory": [
            "ee995e65-194d-47d4-8fd3-037b88296c5f",
            "ee995e65-194d-47d4-8fd3-037b88296c5f"
        ]
    },
    "f6baa55c-5ae3-480c-8c1d-b035010ea738.child": {
        "Category": "[R1] Reindeer Express (25m) - Child",
        "Name": [
            "[R1] Reindeer Express (25m) - C",
            "[R1] Reindeer Express (25m) - M"
        ],
        "Value": [
            21.09,
            23.41
        ],
        "Taxcode": [
            "FI-2025-0%",
            "FI-2025-25.5%"
        ],
        "AccountingCategory": [
            "ee995e65-194d-47d4-8fd3-037b88296c5f",
            "ee995e65-194d-47d4-8fd3-037b88296c5f"
        ]
    },
    "f31c90b8-0701-4e75-b19d-b035010edaef.adult": {
        "Category": "[R2] Reindeer Express (1.5h) - Adult",
        "Name": [
            "[R2] Reindeer Express (1.5h) - C",
            "[R2] Reindeer Express (1.5h) - M"
        ],
        "Value": [
            85.5,
            73.5
        ],
        "Taxcode": [
            "FI-2025-0%",
            "FI-2025-25.5%"
        ],
        "AccountingCategory": [
            "ee995e65-194d-47d4-8fd3-037b88296c5f",
            "ee995e65-194d-47d4-8fd3-037b88296c5f"
        ]
    },
    "f31c90b8-0701-4e75-b19d-b035010edaef.child": {
        "Category": "[R2] Reindeer Express (1.5h) - Child",
        "Name": [
            "[R2] Reindeer Express (1.5h) - C",
            "[R2] Reindeer Express (1.5h) - M"
        ],
        "Value": [
            42.75,
            36.75
        ],
        "Taxcode": [
            "FI-2025-0%",
            "FI-2025-25.5%"
        ],
        "AccountingCategory": [
            "ee995e65-194d-47d4-8fd3-037b88296c5f",
            "ee995e65-194d-47d4-8fd3-037b88296c5f"
        ]
    },
    "4977c19b-ea0e-4eb7-9961-b035010f0c05.adult": {
        "Category": "[R3] Reindeer Day (2.5-3h) - Adult",
        "Name": [
            "[R3] Reindeer Day (2.5-3h) - C",
            "[R3] Reindeer Day (2.5-3h) - M"
        ],
        "Value": [
            117.42,
            71.58
        ],
        "Taxcode": [
            "FI-2025-0%",
            "FI-2025-25.5%"
        ],
        "AccountingCategory": [
            "ee995e65-194d-47d4-8fd3-037b88296c5f",
            "ee995e65-194d-47d4-8fd3-037b88296c5f"
        ]
    },
    "4977c19b-ea0e-4eb7-9961-b035010f0c05.child": {
        "Category": "[R3] Reindeer Day (2.5-3h) - Child",
        "Name": [
            "[R3] Reindeer Day (2.5-3h) - C",
            "[R3] Reindeer Day (2.5-3h) - M"
        ],
        "Value": [
            58.71,
            35.79
        ],
        "Taxcode": [
            "FI-2025-0%",
            "FI-2025-25.5%"
        ],
        "AccountingCategory": [
            "ee995e65-194d-47d4-8fd3-037b88296c5f",
            "ee995e65-194d-47d4-8fd3-037b88296c5f"
        ]
    },
    "ef3daada-4251-422d-b1aa-b22b011c679c.adult": {
        "Category": "[F11] Reindeer Paddock Visit (1h) - Adult",
        "Name": [
            "[F11] Reindeer Paddock Visit (1h) - C",
            "[F11] Reindeer Paddock Visit (1h) - M"
        ],
        "Value": [
            42.18,
            46.82
        ],
        "Taxcode": [
            "FI-2025-0%",
            "FI-2025-25.5%"
        ],
        "AccountingCategory": [
            "ee995e65-194d-47d4-8fd3-037b88296c5f",
            "ee995e65-194d-47d4-8fd3-037b88296c5f"
        ]
    },
    "ef3daada-4251-422d-b1aa-b22b011c679c.child": {
        "Category": "[F11] Reindeer Paddock Visit (1h) - Child",
        "Name": [
            "[F11] Reindeer Paddock Visit (1h) - C",
            "[F11] Reindeer Paddock Visit (1h) - M"
        ],
        "Value": [
            21.09,
            23.41
        ],
        "Taxcode": [
            "FI-2025-0%",
            "FI-2025-25.5%"
        ],
        "AccountingCategory": [
            "ee995e65-194d-47d4-8fd3-037b88296c5f",
            "ee995e65-194d-47d4-8fd3-037b88296c5f"
        ]
    },
    "41fdcfbf-d45d-4a57-9c79-b03600c27f23.adult": {
        "Category": "N150 [R1] Reindeer Express (25m) - Adult",
        "Name": [
            "N150 [R1] Reindeer Express (25m) - C",
            "N150 [R1] Reindeer Express (25m) - M"
        ],
        "Value": [
            42.18,
            33.47
        ],
        "Taxcode": [
            "FI-2025-0%",
            "FI-2025-25.5%"
        ],
        "AccountingCategory": [
            "ee995e65-194d-47d4-8fd3-037b88296c5f",
            "ee995e65-194d-47d4-8fd3-037b88296c5f"
        ]
    },
    "41fdcfbf-d45d-4a57-9c79-b03600c27f23.child": {
        "Category": "N150 [R1] Reindeer Express (25m) - Child",
        "Name": [
            "N150 [R1] Reindeer Express (25m) - C",
            "N150 [R1] Reindeer Express (25m) - M"
        ],
        "Value": [
            21.09,
            16.74
        ],
        "Taxcode": [
            "FI-2025-0%",
            "FI-2025-25.5%"
        ],
        "AccountingCategory": [
            "ee995e65-194d-47d4-8fd3-037b88296c5f",
            "ee995e65-194d-47d4-8fd3-037b88296c5f"
        ]
    },
    "327d936a-088e-470e-9297-b03600c2dff7.adult": {
        "Category": "N150 [R2] Reindeer Express (1.5h) - Adult",
        "Name": [
            "N150 [R2] Reindeer Express (1.5h) - C",
            "N150 [R2] Reindeer Express (1.5h) - M"
        ],
        "Value": [
            85.5,
            49.65
        ],
        "Taxcode": [
            "FI-2025-0%",
            "FI-2025-25.5%"
        ],
        "AccountingCategory": [
            "ee995e65-194d-47d4-8fd3-037b88296c5f",
            "ee995e65-194d-47d4-8fd3-037b88296c5f"
        ]
    },
    "327d936a-088e-470e-9297-b03600c2dff7.child": {
        "Category": "N150 [R2] Reindeer Express (1.5h) - Child",
        "Name": [
            "N150 [R2] Reindeer Express (1.5h) - C",
            "N150 [R2] Reindeer Express (1.5h) - M"
        ],
        "Value": [
            42.75,
            24.83
        ],
        "Taxcode": [
            "FI-2025-0%",
            "FI-2025-25.5%"
        ],
        "AccountingCategory": [
            "ee995e65-194d-47d4-8fd3-037b88296c5f",
            "ee995e65-194d-47d4-8fd3-037b88296c5f"
        ]
    },
    "e329bac3-f07a-4a88-a8cf-b03600c32614.adult": {
        "Category": "N150 [R3] Reindeer Day (2.5-3h) - Adult",
        "Name": [
            "N150 [R3] Reindeer Day (2.5-3h) - C",
            "N150 [R3] Reindeer Day (2.5-3h) - M"
        ],
        "Value": [
            117.42,
            43.23
        ],
        "Taxcode": [
            "FI-2025-0%",
            "FI-2025-25.5%"
        ],
        "AccountingCategory": [
            "ee995e65-194d-47d4-8fd3-037b88296c5f",
            "ee995e65-194d-47d4-8fd3-037b88296c5f"
        ]
    },
    "e329bac3-f07a-4a88-a8cf-b03600c32614.child": {
        "Category": "N150 [R3] Reindeer Day (2.5-3h) - Child",
        "Name": [
            "N150 [R3] Reindeer Day (2.5-3h) - C",
            "N150 [R3] Reindeer Day (2.5-3h) - M"
        ],
        "Value": [
            58.71,
            21.62
        ],
        "Taxcode": [
            "FI-2025-0%",
            "FI-2025-25.5%"
        ],
        "AccountingCategory": [
            "ee995e65-194d-47d4-8fd3-037b88296c5f",
            "ee995e65-194d-47d4-8fd3-037b88296c5f"
        ]
    },
    "c739d047-2e03-46bf-96db-b18e00edc129.adult": {
        "Category": "N150 Reindeer for Groups (1h) - Adult",
        "Name": [
            "N150 Reindeer for Groups (1h) - C",
            "N150 Reindeer for Groups (1h) - M"
        ],
        "Value": [
            51.3,
            41.35
        ],
        "Taxcode": [
            "FI-2025-0%",
            "FI-2025-25.5%"
        ],
        "AccountingCategory": [
            "ee995e65-194d-47d4-8fd3-037b88296c5f",
            "ee995e65-194d-47d4-8fd3-037b88296c5f"
        ]
    },
    "c739d047-2e03-46bf-96db-b18e00edc129.child": {
        "Category": "N150 Reindeer for Groups (1h) - Child",
        "Name": [
            "N150 Reindeer for Groups (1h) - C",
            "N150 Reindeer for Groups (1h) - M"
        ],
        "Value": [
            25.65,
            20.68
        ],
        "Taxcode": [
            "FI-2025-0%",
            "FI-2025-25.5%"
        ],
        "AccountingCategory": [
            "ee995e65-194d-47d4-8fd3-037b88296c5f",
            "ee995e65-194d-47d4-8fd3-037b88296c5f"
        ]
    },
    "892a4be5-0e01-4f8a-900b-b22b011ce8e9.adult": {
        "Category": "N150 [F11] Reindeer Paddock Visit (1h) - Adult",
        "Name": [
            "N150 [F11] Reindeer Paddock Visit (1h) - C",
            "N150 [F11] Reindeer Paddock Visit (1h) - M"
        ],
        "Value": [
            42.18,
            33.47
        ],
        "Taxcode": [
            "FI-2025-0%",
            "FI-2025-25.5%"
        ],
        "AccountingCategory": [
            "ee995e65-194d-47d4-8fd3-037b88296c5f",
            "ee995e65-194d-47d4-8fd3-037b88296c5f"
        ]
    },
    "892a4be5-0e01-4f8a-900b-b22b011ce8e9.child": {
        "Category": "N150 [F11] Reindeer Paddock Visit (1h) - Child",
        "Name": [
            "N150 [F11] Reindeer Paddock Visit (1h) - C",
            "N150 [F11] Reindeer Paddock Visit (1h) - M"
        ],
        "Value": [
            21.09,
            16.74
        ],
        "Taxcode": [
            "FI-2025-0%",
            "FI-2025-25.5%"
        ],
        "AccountingCategory": [
            "ee995e65-194d-47d4-8fd3-037b88296c5f",
            "ee995e65-194d-47d4-8fd3-037b88296c5f"
        ]
    },
    "6da2ba64-7baf-4573-a714-b03600dbcb55.adult": {
        "Category": "N175 [R1] Reindeer Express (25m) - Adult",
        "Name": [
            "N175 [R1] Reindeer Express (25m) - C",
            "N175 [R1] Reindeer Express (25m) - M"
        ],
        "Value": [
            42.18,
            31.25
        ],
        "Taxcode": [
            "FI-2025-0%",
            "FI-2025-25.5%"
        ],
        "AccountingCategory": [
            "ee995e65-194d-47d4-8fd3-037b88296c5f",
            "ee995e65-194d-47d4-8fd3-037b88296c5f"
        ]
    },
    "6da2ba64-7baf-4573-a714-b03600dbcb55.child": {
        "Category": "N175 [R1] Reindeer Express (25m) - Child",
        "Name": [
            "N175 [R1] Reindeer Express (25m) - C",
            "N175 [R1] Reindeer Express (25m) - M"
        ],
        "Value": [
            21.09,
            15.63
        ],
        "Taxcode": [
            "FI-2025-0%",
            "FI-2025-25.5%"
        ],
        "AccountingCategory": [
            "ee995e65-194d-47d4-8fd3-037b88296c5f",
            "ee995e65-194d-47d4-8fd3-037b88296c5f"
        ]
    },
    "b940fa32-13f7-44da-8dee-b03600dc8023.adult": {
        "Category": "N175 [R2] Reindeer Express (1.5h) - Adult",
        "Name": [
            "N175 [R2] Reindeer Express (1.5h) - C",
            "N175 [R2] Reindeer Express (1.5h) - M"
        ],
        "Value": [
            85.5,
            45.68
        ],
        "Taxcode": [
            "FI-2025-0%",
            "FI-2025-25.5%"
        ],
        "AccountingCategory": [
            "ee995e65-194d-47d4-8fd3-037b88296c5f",
            "ee995e65-194d-47d4-8fd3-037b88296c5f"
        ]
    },
    "b940fa32-13f7-44da-8dee-b03600dc8023.child": {
        "Category": "N175 [R2] Reindeer Express (1.5h) - Child",
        "Name": [
            "N175 [R2] Reindeer Express (1.5h) - C",
            "N175 [R2] Reindeer Express (1.5h) - M"
        ],
        "Value": [
            42.75,
            22.84
        ],
        "Taxcode": [
            "FI-2025-0%",
            "FI-2025-25.5%"
        ],
        "AccountingCategory": [
            "ee995e65-194d-47d4-8fd3-037b88296c5f",
            "ee995e65-194d-47d4-8fd3-037b88296c5f"
        ]
    },
    "971fed2f-782d-42df-9d29-b03600e09175.adult": {
        "Category": "N175 [R3] Reindeer Day (2.5-3h) - Adult",
        "Name": [
            "N175 [R3] Reindeer Day (2.5-3h) - C",
            "N175 [R3] Reindeer Day (2.5-3h) - M"
        ],
        "Value": [
            117.42,
            38.51
        ],
        "Taxcode": [
            "FI-2025-0%",
            "FI-2025-25.5%"
        ],
        "AccountingCategory": [
            "ee995e65-194d-47d4-8fd3-037b88296c5f",
            "ee995e65-194d-47d4-8fd3-037b88296c5f"
        ]
    },
    "971fed2f-782d-42df-9d29-b03600e09175.child": {
        "Category": "N175 [R3] Reindeer Day (2.5-3h) - Child",
        "Name": [
            "N175 [R3] Reindeer Day (2.5-3h) - C",
            "N175 [R3] Reindeer Day (2.5-3h) - M"
        ],
        "Value": [
            58.71,
            19.26
        ],
        "Taxcode": [
            "FI-2025-0%",
            "FI-2025-25.5%"
        ],
        "AccountingCategory": [
            "ee995e65-194d-47d4-8fd3-037b88296c5f",
            "ee995e65-194d-47d4-8fd3-037b88296c5f"
        ]
    },
    "86f4f62e-fc88-48bb-ba73-b18e00ef5183.adult": {
        "Category": "N175 Reindeer for Groups (1h) - Adult",
        "Name": [
            "N175 Reindeer for Groups (1h) - C",
            "N175 Reindeer for Groups (1h) - M"
        ],
        "Value": [
            51.3,
            38.63
        ],
        "Taxcode": [
            "FI-2025-0%",
            "FI-2025-25.5%"
        ],
        "AccountingCategory": [
            "ee995e65-194d-47d4-8fd3-037b88296c5f",
            "ee995e65-194d-47d4-8fd3-037b88296c5f"
        ]
    },
    "86f4f62e-fc88-48bb-ba73-b18e00ef5183.child": {
        "Category": "N175 Reindeer for Groups (1h) - Child",
        "Name": [
            "N175 Reindeer for Groups (1h) - C",
            "N175 Reindeer for Groups (1h) - M"
        ],
        "Value": [
            25.65,
            19.32
        ],
        "Taxcode": [
            "FI-2025-0%",
            "FI-2025-25.5%"
        ],
        "AccountingCategory": [
            "ee995e65-194d-47d4-8fd3-037b88296c5f",
            "ee995e65-194d-47d4-8fd3-037b88296c5f"
        ]
    },
    "dc35dcf0-4965-4d9c-a9d1-b22b011d6a3c.adult": {
        "Category": "N175 [F11] Reindeer Paddock Visit (1h) - Adult",
        "Name": [
            "N175 [F11] Reindeer Paddock Visit (1h) - C",
            "N175 [F11] Reindeer Paddock Visit (1h) - M"
        ],
        "Value": [
            42.18,
            31.25
        ],
        "Taxcode": [
            "FI-2025-0%",
            "FI-2025-25.5%"
        ],
        "AccountingCategory": [
            "ee995e65-194d-47d4-8fd3-037b88296c5f",
            "ee995e65-194d-47d4-8fd3-037b88296c5f"
        ]
    },
    "dc35dcf0-4965-4d9c-a9d1-b22b011d6a3c.child": {
        "Category": "N175 [F11] Reindeer Paddock Visit (1h) - Child",
        "Name": [
            "N175 [F11] Reindeer Paddock Visit (1h) - C",
            "N175 [F11] Reindeer Paddock Visit (1h) - M"
        ],
        "Value": [
            21.09,
            15.63
        ],
        "Taxcode": [
            "FI-2025-0%",
            "FI-2025-25.5%"
        ],
        "AccountingCategory": [
            "ee995e65-194d-47d4-8fd3-037b88296c5f",
            "ee995e65-194d-47d4-8fd3-037b88296c5f"
        ]
    },
    "48a28c46-3bfe-4190-a550-b03600f29565.adult": {
        "Category": "N200 [R1] Reindeer Express (25m) - Adult",
        "Name": [
            "N200 [R1] Reindeer Express (25m) - C",
            "N200 [R1] Reindeer Express (25m) - M"
        ],
        "Value": [
            42.18,
            29.02
        ],
        "Taxcode": [
            "FI-2025-0%",
            "FI-2025-25.5%"
        ],
        "AccountingCategory": [
            "ee995e65-194d-47d4-8fd3-037b88296c5f",
            "ee995e65-194d-47d4-8fd3-037b88296c5f"
        ]
    },
    "48a28c46-3bfe-4190-a550-b03600f29565.child": {
        "Category": "N200 [R1] Reindeer Express (25m) - Child",
        "Name": [
            "N200 [R1] Reindeer Express (25m) - C",
            "N200 [R1] Reindeer Express (25m) - M"
        ],
        "Value": [
            21.09,
            14.51
        ],
        "Taxcode": [
            "FI-2025-0%",
            "FI-2025-25.5%"
        ],
        "AccountingCategory": [
            "ee995e65-194d-47d4-8fd3-037b88296c5f",
            "ee995e65-194d-47d4-8fd3-037b88296c5f"
        ]
    },
    "f7bc554f-1bd3-4655-8645-b03600f2dfe1.adult": {
        "Category": "N200 [R2] Reindeer Express (1.5h) - Adult",
        "Name": [
            "N200 [R2] Reindeer Express (1.5h) - C",
            "N200 [R2] Reindeer Express (1.5h) - M"
        ],
        "Value": [
            85.5,
            41.7
        ],
        "Taxcode": [
            "FI-2025-0%",
            "FI-2025-25.5%"
        ],
        "AccountingCategory": [
            "ee995e65-194d-47d4-8fd3-037b88296c5f",
            "ee995e65-194d-47d4-8fd3-037b88296c5f"
        ]
    },
    "f7bc554f-1bd3-4655-8645-b03600f2dfe1.child": {
        "Category": "N200 [R2] Reindeer Express (1.5h) - Child",
        "Name": [
            "N200 [R2] Reindeer Express (1.5h) - C",
            "N200 [R2] Reindeer Express (1.5h) - M"
        ],
        "Value": [
            42.75,
            20.85
        ],
        "Taxcode": [
            "FI-2025-0%",
            "FI-2025-25.5%"
        ],
        "AccountingCategory": [
            "ee995e65-194d-47d4-8fd3-037b88296c5f",
            "ee995e65-194d-47d4-8fd3-037b88296c5f"
        ]
    },
    "9e4f2897-e14a-4d9f-9a91-b03600f327cb.adult": {
        "Category": "N200 [R3] Reindeer Day (2.5-3h) - Adult",
        "Name": [
            "N200 [R3] Reindeer Day (2.5-3h) - C",
            "N200 [R3] Reindeer Day (2.5-3h) - M"
        ],
        "Value": [
            117.42,
            33.78
        ],
        "Taxcode": [
            "FI-2025-0%",
            "FI-2025-25.5%"
        ],
        "AccountingCategory": [
            "ee995e65-194d-47d4-8fd3-037b88296c5f",
            "ee995e65-194d-47d4-8fd3-037b88296c5f"
        ]
    },
    "9e4f2897-e14a-4d9f-9a91-b03600f327cb.child": {
        "Category": "N200 [R3] Reindeer Day (2.5-3h) - Child",
        "Name": [
            "N200 [R3] Reindeer Day (2.5-3h) - C",
            "N200 [R3] Reindeer Day (2.5-3h) - M"
        ],
        "Value": [
            58.71,
            16.89
        ],
        "Taxcode": [
            "FI-2025-0%",
            "FI-2025-25.5%"
        ],
        "AccountingCategory": [
            "ee995e65-194d-47d4-8fd3-037b88296c5f",
            "ee995e65-194d-47d4-8fd3-037b88296c5f"
        ]
    },
    "a81c6db3-a8dd-4f2b-aa67-b18e00f060a2.adult": {
        "Category": "N200 Reindeer for Groups (1h) - Adult",
        "Name": [
            "N200 Reindeer for Groups (1h) - C",
            "N200 Reindeer for Groups (1h) - M"
        ],
        "Value": [
            51.3,
            35.9
        ],
        "Taxcode": [
            "FI-2025-0%",
            "FI-2025-25.5%"
        ],
        "AccountingCategory": [
            "ee995e65-194d-47d4-8fd3-037b88296c5f",
            "ee995e65-194d-47d4-8fd3-037b88296c5f"
        ]
    },
    "a81c6db3-a8dd-4f2b-aa67-b18e00f060a2.child": {
        "Category": "N200 Reindeer for Groups (1h) - Child",
        "Name": [
            "N200 Reindeer for Groups (1h) - C",
            "N200 Reindeer for Groups (1h) - M"
        ],
        "Value": [
            25.65,
            17.95
        ],
        "Taxcode": [
            "FI-2025-0%",
            "FI-2025-25.5%"
        ],
        "AccountingCategory": [
            "ee995e65-194d-47d4-8fd3-037b88296c5f",
            "ee995e65-194d-47d4-8fd3-037b88296c5f"
        ]
    },
    "fad0b390-346e-4f43-aef7-b22b011daa2c.adult": {
        "Category": "N200 [F11] Reindeer Paddock Visit (1h) - Adult",
        "Name": [
            "N200 [F11] Reindeer Paddock Visit (1h) - C",
            "N200 [F11] Reindeer Paddock Visit (1h) - M"
        ],
        "Value": [
            42.18,
            29.02
        ],
        "Taxcode": [
            "FI-2025-0%",
            "FI-2025-25.5%"
        ],
        "AccountingCategory": [
            "ee995e65-194d-47d4-8fd3-037b88296c5f",
            "ee995e65-194d-47d4-8fd3-037b88296c5f"
        ]
    },
    "fad0b390-346e-4f43-aef7-b22b011daa2c.child": {
        "Category": "N200 [F11] Reindeer Paddock Visit (1h) - Child",
        "Name": [
            "N200 [F11] Reindeer Paddock Visit (1h) - C",
            "N200 [F11] Reindeer Paddock Visit (1h) - M"
        ],
        "Value": [
            21.09,
            14.51
        ],
        "Taxcode": [
            "FI-2025-0%",
            "FI-2025-25.5%"
        ],
        "AccountingCategory": [
            "ee995e65-194d-47d4-8fd3-037b88296c5f",
            "ee995e65-194d-47d4-8fd3-037b88296c5f"
        ]
    },
    "1e8e0d80-bb74-40c0-a693-b03600facaf8.adult": {
        "Category": "N215 [R1] Reindeer Express (25m) - Adult",
        "Name": [
            "N215 [R1] Reindeer Express (25m) - C",
            "N215 [R1] Reindeer Express (25m) - M"
        ],
        "Value": [
            42.18,
            27.69
        ],
        "Taxcode": [
            "FI-2025-0%",
            "FI-2025-25.5%"
        ],
        "AccountingCategory": [
            "ee995e65-194d-47d4-8fd3-037b88296c5f",
            "ee995e65-194d-47d4-8fd3-037b88296c5f"
        ]
    },
    "1e8e0d80-bb74-40c0-a693-b03600facaf8.child": {
        "Category": "N215 [R1] Reindeer Express (25m) - Child",
        "Name": [
            "N215 [R1] Reindeer Express (25m) - C",
            "N215 [R1] Reindeer Express (25m) - M"
        ],
        "Value": [
            21.09,
            13.85
        ],
        "Taxcode": [
            "FI-2025-0%",
            "FI-2025-25.5%"
        ],
        "AccountingCategory": [
            "ee995e65-194d-47d4-8fd3-037b88296c5f",
            "ee995e65-194d-47d4-8fd3-037b88296c5f"
        ]
    },
    "946882c9-6a70-4ce1-9ca3-b03600fb024e.adult": {
        "Category": "N215 [R2] Reindeer Express (1.5h) - Adult",
        "Name": [
            "N215 [R2] Reindeer Express (1.5h) - C",
            "N215 [R2] Reindeer Express (1.5h) - M"
        ],
        "Value": [
            85.5,
            39.32
        ],
        "Taxcode": [
            "FI-2025-0%",
            "FI-2025-25.5%"
        ],
        "AccountingCategory": [
            "ee995e65-194d-47d4-8fd3-037b88296c5f",
            "ee995e65-194d-47d4-8fd3-037b88296c5f"
        ]
    },
    "946882c9-6a70-4ce1-9ca3-b03600fb024e.child": {
        "Category": "N215 [R2] Reindeer Express (1.5h) - Child",
        "Name": [
            "N215 [R2] Reindeer Express (1.5h) - C",
            "N215 [R2] Reindeer Express (1.5h) - M"
        ],
        "Value": [
            42.75,
            19.66
        ],
        "Taxcode": [
            "FI-2025-0%",
            "FI-2025-25.5%"
        ],
        "AccountingCategory": [
            "ee995e65-194d-47d4-8fd3-037b88296c5f",
            "ee995e65-194d-47d4-8fd3-037b88296c5f"
        ]
    },
    "b33f2882-1a12-4a13-9634-b03600fb4177.adult": {
        "Category": "N215 [R3] Reindeer Day (2.5-3h) - Adult",
        "Name": [
            "N215 [R3] Reindeer Day (2.5-3h) - C",
            "N215 [R3] Reindeer Day (2.5-3h) - M"
        ],
        "Value": [
            117.42,
            30.95
        ],
        "Taxcode": [
            "FI-2025-0%",
            "FI-2025-25.5%"
        ],
        "AccountingCategory": [
            "ee995e65-194d-47d4-8fd3-037b88296c5f",
            "ee995e65-194d-47d4-8fd3-037b88296c5f"
        ]
    },
    "b33f2882-1a12-4a13-9634-b03600fb4177.child": {
        "Category": "N215 [R3] Reindeer Day (2.5-3h) - Child",
        "Name": [
            "N215 [R3] Reindeer Day (2.5-3h) - C",
            "N215 [R3] Reindeer Day (2.5-3h) - M"
        ],
        "Value": [
            58.71,
            15.48
        ],
        "Taxcode": [
            "FI-2025-0%",
            "FI-2025-25.5%"
        ],
        "AccountingCategory": [
            "ee995e65-194d-47d4-8fd3-037b88296c5f",
            "ee995e65-194d-47d4-8fd3-037b88296c5f"
        ]
    },
    "a0950c52-2b3b-4e27-a0a1-b18e00f13371.adult": {
        "Category": "N215 Reindeer for Groups (1h) - Adult",
        "Name": [
            "N215 Reindeer for Groups (1h) - C",
            "N215 Reindeer for Groups (1h) - M"
        ],
        "Value": [
            51.3,
            34.27
        ],
        "Taxcode": [
            "FI-2025-0%",
            "FI-2025-25.5%"
        ],
        "AccountingCategory": [
            "ee995e65-194d-47d4-8fd3-037b88296c5f",
            "ee995e65-194d-47d4-8fd3-037b88296c5f"
        ]
    },
    "a0950c52-2b3b-4e27-a0a1-b18e00f13371.child": {
        "Category": "N215 Reindeer for Groups (1h) - Child",
        "Name": [
            "N215 Reindeer for Groups (1h) - C",
            "N215 Reindeer for Groups (1h) - M"
        ],
        "Value": [
            25.65,
            17.14
        ],
        "Taxcode": [
            "FI-2025-0%",
            "FI-2025-25.5%"
        ],
        "AccountingCategory": [
            "ee995e65-194d-47d4-8fd3-037b88296c5f",
            "ee995e65-194d-47d4-8fd3-037b88296c5f"
        ]
    },
    "4e61fd5d-c1b8-45a8-b288-b22b011e1199.adult": {
        "Category": "N215 [F11] Reindeer Paddock Visit (1h) - Adult",
        "Name": [
            "N215 [F11] Reindeer Paddock Visit (1h) - C",
            "N215 [F11] Reindeer Paddock Visit (1h) - M"
        ],
        "Value": [
            42.18,
            27.69
        ],
        "Taxcode": [
            "FI-2025-0%",
            "FI-2025-25.5%"
        ],
        "AccountingCategory": [
            "ee995e65-194d-47d4-8fd3-037b88296c5f",
            "ee995e65-194d-47d4-8fd3-037b88296c5f"
        ]
    },
    "4e61fd5d-c1b8-45a8-b288-b22b011e1199.child": {
        "Category": "N215 [F11] Reindeer Paddock Visit (1h) - Child",
        "Name": [
            "N215 [F11] Reindeer Paddock Visit (1h) - C",
            "N215 [F11] Reindeer Paddock Visit (1h) - M"
        ],
        "Value": [
            21.09,
            13.85
        ],
        "Taxcode": [
            "FI-2025-0%",
            "FI-2025-25.5%"
        ],
        "AccountingCategory": [
            "ee995e65-194d-47d4-8fd3-037b88296c5f",
            "ee995e65-194d-47d4-8fd3-037b88296c5f"
        ]
    },
    "342eee05-e142-458f-a12c-761024a97125": {
        "Category": "[R1] Reindeer Express (25m) - Adult",
        "Name": [
            "[R1] Reindeer Express (25m) - Adult - C",
            "[R1] Reindeer Express (25m) - Adult - M"
        ],
        "Value": [
            42.18,
            46.82
        ],
        "Taxcode": [
            "FI-2025-0%",
            "FI-2025-25.5%"
        ],
        "AccountingCategory": [
            "ee995e65-194d-47d4-8fd3-037b88296c5f",
            "ee995e65-194d-47d4-8fd3-037b88296c5f"
        ]
    },
    "453fa81f-a2d9-4e04-a7fd-ce848a43970a": {
        "Category": "[R1] Reindeer Express (25m) - Child",
        "Name": [
            "[R1] Reindeer Express (25m) - Child - C",
            "[R1] Reindeer Express (25m) - Child - M"
        ],
        "Value": [
            21.09,
            23.41
        ],
        "Taxcode": [
            "FI-2025-0%",
            "FI-2025-25.5%"
        ],
        "AccountingCategory": [
            "ee995e65-194d-47d4-8fd3-037b88296c5f",
            "ee995e65-194d-47d4-8fd3-037b88296c5f"
        ]
    },
    "bf8b6083-c68b-47f9-a4dc-2d0f98f2c90d": {
        "Category": "[R2] Reindeer Express (1.5h) - Adult",
        "Name": [
            "[R2] Reindeer Express (1.5h) - Adult - C",
            "[R2] Reindeer Express (1.5h) - Adult - M"
        ],
        "Value": [
            85.50,
            73.50
        ],
        "Taxcode": [
            "FI-2025-0%",
            "FI-2025-25.5%"
        ],
        "AccountingCategory": [
            "ee995e65-194d-47d4-8fd3-037b88296c5f",
            "ee995e65-194d-47d4-8fd3-037b88296c5f"
        ]
    },
    "fea3ebc3-d88c-4d7c-a4a0-b2ba83bba3a2": {
        "Category": "[R2] Reindeer Express (1.5h) - Child",
        "Name": [
            "[R2] Reindeer Express (1.5h) - Child - C",
            "[R2] Reindeer Express (1.5h) - Child - M"
        ],
        "Value": [
            42.75,
            36.75
        ],
        "Taxcode": [
            "FI-2025-0%",
            "FI-2025-25.5%"
        ],
        "AccountingCategory": [
            "ee995e65-194d-47d4-8fd3-037b88296c5f",
            "ee995e65-194d-47d4-8fd3-037b88296c5f"
        ]
    },
    "410024f3-4f60-4c76-b483-5234e1698f48": {
        "Category": "[R3] Reindeer Day (2.5-3h) - Adult",
        "Name": [
            "[R3] Reindeer Day (2.5-3h) - Adult - C",
            "[R3] Reindeer Day (2.5-3h) - Adult - M"
        ],
        "Value": [
            117.42,
            71.58
        ],
        "Taxcode": [
            "FI-2025-0%",
            "FI-2025-25.5%"
        ],
        "AccountingCategory": [
            "ee995e65-194d-47d4-8fd3-037b88296c5f",
            "ee995e65-194d-47d4-8fd3-037b88296c5f"
        ]
    },
    "81ea57f2-db65-4819-93b9-396fa19432a2": {
        "Category": "[R3] Reindeer Day (2.5-3h) - Child",
        "Name": [
            "[R3] Reindeer Day (2.5-3h) - Child - C",
            "[R3] Reindeer Day (2.5-3h) - Child - M"
        ],
        "Value": [
            58.71,
            35.79
        ],
        "Taxcode": [
            "FI-2025-0%",
            "FI-2025-25.5%"
        ],
        "AccountingCategory": [
            "ee995e65-194d-47d4-8fd3-037b88296c5f",
            "ee995e65-194d-47d4-8fd3-037b88296c5f"
        ]
    },
    "e3f6f4e0-7d95-427e-827d-b22b011fcf9f": {
        "Category": "[F11] Reindeer Paddock Visit (1h) - Adult",
        "Name": [
            "[F11] Reindeer Paddock Visit (1h) - Adult - C",
            "[F11] Reindeer Paddock Visit (1h) - Adult - M"
        ],
        "Value": [
            42.18,
            46.82
        ],
        "Taxcode": [
            "FI-2025-0%",
            "FI-2025-25.5%"
        ],
        "AccountingCategory": [
            "ee995e65-194d-47d4-8fd3-037b88296c5f",
            "ee995e65-194d-47d4-8fd3-037b88296c5f"
        ]
    },
    "feae1890-fa0f-45e1-9a38-b22b011ff508": {
        "Category": "[F11] Reindeer Paddock Visit (1h) - Child",
        "Name": [
            "[F11] Reindeer Paddock Visit (1h) - Child - C",
            "[F11] Reindeer Paddock Visit (1h) - Child - M"
        ],
        "Value": [
            21.09,
            23.41
        ],
        "Taxcode": [
            "FI-2025-0%",
            "FI-2025-25.5%"
        ],
        "AccountingCategory": [
            "ee995e65-194d-47d4-8fd3-037b88296c5f",
            "ee995e65-194d-47d4-8fd3-037b88296c5f"
        ]
    }
}

allPayloads = []
orderItems = []
packageNames = []
packageDict = {}
packageCounts = {}
billId = None


def isAdult(name: str) -> bool:
    return "Adult" in name

def isChild(name: str) -> bool:
    return "Child" in name or not isAdult(name)

for reservation in parsed_data:
    dataItems = reservation['orderItems']
    if isinstance(dataItems, dict):
        dataItems = [dataItems]
    for item in dataItems:
        orderitem = item['orderItemId']
        orderItems.append(orderitem)
    # if dataItems is a dict (single item), wrap it in a list
    if isinstance(dataItems, dict):
        dataItems = [dataItems]
    for dataItem in dataItems:
        productId = dataItem.get('productId')
        unitCount = dataItem.get('unitCount', 1)
        billId = dataItem.get('billId')
        reservationId = reservation.get('ReservationId')
        # Use the function or one-liner to pick first non-None id
        chosenIdBill = next((x for x in [billId] if x is not None), None)
        chosenIdReservationId = next((x for x in [reservationId] if x is not None), None)
        if productId in productMapping:
            mapped = productMapping[productId]
            category = mapped['Category']
            count = dataItem['unitCount']
            if category in packageDict:
                packageDict[category] += count
            else:
                packageDict[category] = count
            for i in range(len(mapped['Name'])):
                itemPayload = createItem(
                    Name=mapped['Name'][i],
                    Count=count,
                    Value=float(mapped['Value'][i]),
                    Taxcode=mapped['Taxcode'][i],
                    AccountingCategory=mapped['AccountingCategory'][i]
                )
                allPayloads.append(itemPayload)

packageList = [(cat, cnt) for cat, cnt in packageDict.items()]
print(packageList)

output = {
    'billId': chosenIdBill,
    'reservationId': chosenIdReservationId,
    'data': str(allPayloads),
    'orderItems': orderItems,
    'packageNames': packageList
}