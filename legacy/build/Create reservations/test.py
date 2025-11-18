dict = {
    "reservation_id": "resv_12345",
    "window": 30,
}

import datetime from datetime import datetime, timedelta


checkindate = datetime.utcnow().date() + timedelta(days=10)
createddate = datetime.utcnow().date()