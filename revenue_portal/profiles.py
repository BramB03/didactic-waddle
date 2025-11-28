# profiles.py

PROFILES = {
    "default": {
        # ---------------------------
        #  General settings
        # ---------------------------
        "display_name": "The David Demo",
        "timezone": "Europe/Amsterdam",
        "client_name": "RevenuePortal 1.0.0",

        # ---------------------------
        #  Mews API credentials
        # ---------------------------
        "mews_base": "https://api.mews-demo.com/api/connector/v1/",
        "client_token_env": "DEMO_CLIENTTOKEN",
        "access_token_env": "DAVID_WEST_ACCESSTOKEN",

        # ---------------------------
        #  Service IDs (Hotel / Student / Extended Stay)
        # ---------------------------
        "hotel_service_id": "2a11701c-061c-4262-830a-b3a200f3ff40",
        "student_service_id": "5a6ee418-468c-45f7-a3d2-b364007a7c0f",
        "extended_service_id": "d9668056-a076-434e-8412-b364007a95da",

        # ---------------------------
        #  Room type mapping per service → canonical category
        # ---------------------------
        # This structure stays identical to your current hardcoded setup
        "room_type_ids_by_service": {
            # Hotel
            "2a11701c-061c-4262-830a-b3a200f3ff40": {
                "Standard Double": "d10c5a8e-3e0a-4180-a7f7-b3a200f423c0",
                "Standard Twin":   "b527693b-4c9a-4778-8ee7-b3a200f488a5",
                "Deluxe Double":   "f0df4d73-8a79-44f5-822c-b3a200f4b847",
                "Family Room":     "36766d2f-c0b5-4ed0-a891-b3a200f4f15b",
            },

            # Student
            "5a6ee418-468c-45f7-a3d2-b364007a7c0f": {
                "Standard Double": "8fad2a22-594a-4c39-afb3-b364007ae8aa",
                "Standard Twin":   "35f02589-5c0b-4eb5-9446-b3a000ef8159",
                "Deluxe Double":   "1bc0cab7-d54f-4c3f-86d3-b3a000efb7db",
                "Family Room":     "d7392203-a33e-4331-a566-b3a000efd4d2",
            },

            # Extended stay
            "d9668056-a076-434e-8412-b364007a95da": {
                "Standard Double": "ed2d470a-d6e1-4b6d-83fb-b364007acaa0",
                "Standard Twin":   "427b22df-1ea3-4772-821d-b3a000f1463c",
                "Deluxe Double":   "7d28e32b-1c8c-4586-861d-b3a000f1fe00",
                "Family Room":     "7a86e76e-7a5a-42eb-ad14-b3a000f28080",
            },
        },

        # ---------------------------
        #  Frontend mapping (index file)
        # ---------------------------
        "frontend_room_types": {
            "d10c5a8e-3e0a-4180-a7f7-b3a200f423c0": { "name": "Standard Double", "order": 0 },
            "b527693b-4c9a-4778-8ee7-b3a200f488a5": { "name": "Standard Twin",   "order": 1 },
            "f0df4d73-8a79-44f5-822c-b3a200f4b847": { "name": "Deluxe Double",   "order": 2 },
            "36766d2f-c0b5-4ed0-a891-b3a200f4f15b": { "name": "Family Room",     "order": 3 },
        }
    },
    "TSH": {
        # ---------------------------
        #  General settings
        # ---------------------------
        "display_name": "TSH Delft",
        "timezone": "Europe/Amsterdam",
        "client_name": "RevenuePortal 1.0.0",

        # ---------------------------
        #  Mews API credentials
        # ---------------------------
        "mews_base": "https://api.mews-demo.com/api/connector/v1/",
        "client_token_env": "DEMO_CLIENTTOKEN",
        "access_token_env": "TSH_DELFT_ACCESSTOKEN",

        # ---------------------------
        #  Service IDs (Hotel / Student / Extended Stay)
        # ---------------------------
        "hotel_service_id": "728d18fa-49e9-4b2b-926a-ab5f00f5af20",
        "student_service_id": "141fd392-4d35-435f-a0d9-b11b00b36b6e",
        "extended_service_id": "d69277d2-4193-4e92-93b0-b11b00bb224b",

        # ---------------------------
        #  Room type mapping per service → canonical category
        # ---------------------------
        # This structure stays identical to your current hardcoded setup
        "room_type_ids_by_service": {
            # Hotel
            "728d18fa-49e9-4b2b-926a-ab5f00f5af20": {
                "Standard Single": "20695bb1-8484-4939-9394-ab5f00f5aff3",
                "Executive Queen":   "8a7710ec-6a8b-4f01-8057-ab5f00f5aff3",
                "Deluxe Queen":   "841b9dbe-0dfe-419e-b33b-ab5f00f5aff3",
                "Deluxe King":     "f58d0f78-f50e-4412-864c-ab5f00f5aff3",
                "Executive Studio": "e11aadc8-1f89-4747-898b-ab5f00f5aff3",
                "Deluxe Studio":   "b12c9d3e-2e56-44c2-b920-ab5f00f5aff3",
            },

            # Student
            "141fd392-4d35-435f-a0d9-b11b00b36b6e": {
                "Standard Single": "e18c7468-95ef-4c59-a91b-b11b00d1aefc",
                "Executive Queen":   "1af120e3-1338-4d68-ad94-b11b00d20816",
                "Deluxe Queen":   "e1dfc1d4-c9bb-4a68-8c2f-b11b00d2850b",
                "Deluxe King":     "93aa2f4e-9730-4b01-87be-b11b00d3688c",
                "Executive Studio": "ba116252-3996-4810-a34d-b11b00d3b76e",
                "Deluxe Studio":   "cd40f50b-b0a8-47f6-8f5c-b13a00f83929",
            },

            # Extended stay
            "d69277d2-4193-4e92-93b0-b11b00bb224b": {
                "Standard Single": "1f3cd521-7adb-41f2-a93e-b13a00f8b5e1",
                "Executive Queen":   "c213412d-31e2-44b0-8da9-b13a00fa0b6e",
                "Deluxe Queen":   "55e3d2f2-4594-47a2-ab3a-b13a00fa537b",
                "Deluxe King":     "66d451b4-66d5-420b-91f6-b13a00fa9605",
                "Executive Studio": "62aac068-a924-42bb-afab-b11b00d4265c",
                "Deluxe Studio":   "da12ff51-52b9-4433-aaeb-b11b00d47257",
            },
        },

        # ---------------------------
        #  Frontend mapping (index file)
        # ---------------------------
        "frontend_room_types": {
              "20695bb1-8484-4939-9394-ab5f00f5aff3": { "name": "Standard Single", "order": 0 },
              "8a7710ec-6a8b-4f01-8057-ab5f00f5aff3": { "name": "Executive Queen", "order": 1 },
              "841b9dbe-0dfe-419e-b33b-ab5f00f5aff3": { "name": "Deluxe Queen", "order": 2 },
              "f58d0f78-f50e-4412-864c-ab5f00f5aff3": { "name": "Deluxe King", "order": 3 },
              "e11aadc8-1f89-4747-898b-ab5f00f5aff3": { "name": "Executive Studio", "order": 4 },
              "b12c9d3e-2e56-44c2-b920-ab5f00f5aff3": { "name": "Deluxe Studio", "order": 5 }
        }
    }
}