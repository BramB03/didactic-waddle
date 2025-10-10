from flask import Flask, render_template_string
from datetime import datetime, timedelta

app = Flask(__name__)

HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8" />
    <script src="https://api.mews.com/distributor/distributor.min.js"></script>
    <title>Booking Page</title>
</head>
<body>
    <!-- Booking Form -->
    <form id="booking-form"> 
        <label for="start">Check-in:</label>
        <input type="date" id="start" name="start" required value="{{ today }}">

        <label for="end">Check-out:</label>
        <input type="date" id="end" name="end" required value="{{ twoDaysLater }}">

        <label for="hotel">Select a Hotel:</label>
        <select id="hotel" name="hotel" required>
            <option value="QL">QL</option>
            <option value="allProperties">All Properties</option>
        </select>

        <button type="button" class="distributor-open">Book Now</button>
    </form>

    <script>
        function getFormattedDate(offsetDays = 0) {
            const date = new Date();
            date.setDate(date.getDate() + offsetDays);
            return date.toISOString().split('T')[0];
        }

        const hotelConfigs = {
            QL: ['b8c0b2e3-d102-4173-a502-ac0c008c28f7'], // Replace with actual config ID for QL
            allProperties: [
                    'b8c0b2e3-d102-4173-a502-ac0c008c28f7', 
                    'a61b74d2-a01f-4c86-9f47-ab6700b75d14', 
                    '3f675d34-2a97-466f-8fb4-ab9d00de7b77', 
                    'bb099cff-9f38-4a84-bec5-adfd007d34d7', 
                    '56070a61-4bb5-436d-b614-bbe65538e8d4', 
                    '55a2bc2e-e545-4154-aa1e-ab870101638c', 
                    'dac1fa58-ee25-49bb-a9f8-f72b4e0b75a9', 
                    '42e8baa4-14a9-4b1d-8381-aa9600af5f09',
                    'f40d6c12-bbe2-4d70-be82-aab600e9c401',
                    '7a13590c-6538-461e-b02f-6357400de493',
                    '2e4ba270-f1d9-4138-ad8d-6345a4dbc7ac',
                    '4d2bc962-8da0-4c77-978e-84f0020e93bf'  
                    'c71fb24e-414b-4af5-a5af-ac5d007ffd95',
                    '01f9c1e4-5117-415c-bb95-b23c0093dfec',
                    'f4a2c820-1f02-4162-a706-b11b00a24a79',
                    '0eaefce3-770d-4a33-a65b-b0b5006fc7a1',
                    '7ddefe80-6c98-4117-9080-b0c700ab49a7',
                    '504b957b-e0d7-43ac-bcbd-b14600780647',
                    '5cf0d1d9-fbef-44ce-b074-b035012a0824',
                    'f3f5b578-b4e9-40b1-888c-ad5800d6daa4',
                    '7347ff5d-ca53-4377-9d1c-b27400bfe36d',
                    'a29d6d7b-6f58-421e-b1b5-e012c8860fa4',
                    '771a5ef4-1f86-44e6-a485-b24c008fd691',
                    '7e0e4d20-0aff-470b-825b-b0dc00acbb51',
                    '4f921344-0774-4f88-aa32-b21b00b3f29f',
                    '8cf78d01-b1e2-4013-ba72-e8f6323a44ec',
                    '994ab2dd-ce36-42c0-a49b-b0b600970cf7',
                    'c9f1f63c-3717-426a-bac9-acbc010a6add',
                    '64e97300-8aa5-4d49-ae3d-aacd00b620a8',
                    'ec866713-b922-4348-a700-b09d00bf8de5',
                    '5299f216-b23f-4104-b748-af240094255c',
                    'd6ef1a23-d741-4e5b-8350-b24b008fa4b1',
                    '58df0046-a2a4-4e55-a27e-b02000bddf24',
                    'dadd566c-b544-4e65-ac8e-afaf00a4a3ad',
                    'd83aaeea-b671-4f99-9d7e-ac3e0112e09c',
                    '82988e66-8880-4792-9330-8c33d795d408',
                    'a5ee2b49-b98b-45bd-a496-b28e008d4ba6',
                    '340672c2-a5ca-430d-b4e9-b18700839739' 
            ]
        };

        let apiInstance = null;

        // Init Distributor globally
        Mews.Distributor(
            {
                configurationIds: [], // Start empty, fill on user action
                openElements: '.distributor-open'
            },
            function (api) {
                apiInstance = api;
            }
        );

        document.querySelector('.distributor-open').addEventListener('click', function () {
            const selectedHotel = document.getElementById('hotel').value;
            const start = new Date(document.getElementById('start').value);
            const end = new Date(document.getElementById('end').value);

            if (!apiInstance) return alert('Booking widget not initialized.');

            apiInstance.setConfigurationIds(hotelConfigs[selectedHotel]);
            apiInstance.setStartDate(start);
            apiInstance.setEndDate(end);
            apiInstance.open(); // Explicitly open the booking engine
        });
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    today = datetime.today().strftime('%Y-%m-%d')
    twoDaysLater = (datetime.today() + timedelta(days=2)).strftime('%Y-%m-%d')
    return render_template_string(HTML, today=today, twoDaysLater=twoDaysLater)

if __name__ == '__main__':
    app.run(debug=True)
