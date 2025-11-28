# Mainrevenueportal.py adjustments:

# Line 32
timeZone = "Europe/Amsterdam"

# Line 34
ROOM_TYPE_IDS_BY_SERVICE: Dict[str, Dict[str, str]] = {
    # Service A (hotel)
    "2a11701c-061c-4262-830a-b3a200f3ff40": {
        "Standard Double": "d10c5a8e-3e0a-4180-a7f7-b3a200f423c0",
        "Standard Twin": "b527693b-4c9a-4778-8ee7-b3a200f488a5",
        "Deluxe Double": "f0df4d73-8a79-44f5-822c-b3a200f4b847",
        "Family Room": "36766d2f-c0b5-4ed0-a891-b3a200f4f15b",
    },
    # Service B (student)
    "5a6ee418-468c-45f7-a3d2-b364007a7c0f": {
        "Standard Double": "8fad2a22-594a-4c39-afb3-b364007ae8aa",
        "Standard Twin": "35f02589-5c0b-4eb5-9446-b3a000ef8159",
        "Deluxe Double": "1bc0cab7-d54f-4c3f-86d3-b3a000efb7db",
        "Family Room": "d7392203-a33e-4331-a566-b3a000efd4d2",
    },
    # Service C (extended stay)
    "d9668056-a076-434e-8412-b364007a95da": {
        "Standard Double": "ed2d470a-d6e1-4b6d-83fb-b364007acaa0",
        "Standard Twin": "427b22df-1ea3-4772-821d-b3a000f1463c",
        "Deluxe Double": "7d28e32b-1c8c-4586-861d-b3a000f1fe00",
        "Family Room": "7a86e76e-7a5a-42eb-ad14-b3a000f28080",
    },
}

HOTEL_SERVICE_ID = "2a11701c-061c-4262-830a-b3a200f3ff40"
STUDENT_SERVICE_ID = "5a6ee418-468c-45f7-a3d2-b364007a7c0f"
EXTENDED_STAY_SERVICE_ID = "d9668056-a076-434e-8412-b364007a95da"

# Line 327
mews_base = "https://api.mews-demo.com/api/connector/v1/"
client_token = os.getenv("DEMO_CLIENTTOKEN")
access_token = os.getenv("DAVID_WEST_ACCESSTOKEN")
client_name = "RevenuePortal 1.0.0"

# index-revenueportal.html adjustments:

# Line 117

const roomTypeNameMap = {
  "20695bb1-8484-4939-9394-ab5f00f5aff3": { name: "Standard Single - H", order: 0 },
  "8a7710ec-6a8b-4f01-8057-ab5f00f5aff3": { name: "Executive Queen -H", order: 2 },
  "841b9dbe-0dfe-419e-b33b-ab5f00f5aff3": { name: "Deluxe Queen - H", order: 4 },
  "f58d0f78-f50e-4412-864c-ab5f00f5aff3": { name: "Deluxe King - H", order: 6 },
  "e11aadc8-1f89-4747-898b-ab5f00f5aff3": { name: "Executive Studio - H", order: 7 },
  "b12c9d3e-2e56-44c2-b920-ab5f00f5aff3": { name: "Deluxe Studio - H", order: 10 }
};

