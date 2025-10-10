from flask import Flask, request, jsonify, render_template_string, render_template

app = Flask(__name__)

HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8" />
    <script src="https://api.mews.com/distributor/distributor.min.js"></script>
    <title>My Page</title>
</head>
<body>
    <!-- Date selection form -->
    <form id="booking-form">
        <label for="start">Check-in:</label>
        <input type="date" id="start" name="start" required>

        <label for="end">Check-out:</label>
        <input type="date" id="end" name="end" required>

        <!-- hotel selection dropdown -->
        <label for="hotel">Select a Hotel:</label>
        <select id="hotel" name="hotel" required>
            <option value="" disabled selected>Select a hotel</option>
            <option value="Piccadilly">Capsule Piccadilly</option>
            <option value="leicester">leicester</option>
        </select>

        <button type="submit">Book Now</button>
    </form>

    <script>
        Mews.Distributor(
            {
                configurationIds: [
                    '50997dcd-7e15-4d09-918b-b28000c5d32f',
                    '41e7d45b-70d5-4443-948d-ad88007f067f'
                ],
            },
            function (api) {
                document.getElementById('booking-form').addEventListener('submit', function(event) {
                    event.preventDefault();

                    const start = document.getElementById('start').value;
                    const end = document.getElementById('end').value;
                    const hotel = document.getElementById('hotel').value;

                    if (!start || !end || !hotel) {
                        alert("Please select check-in and check-out dates, and a hotel.");
                        return;
                    }

                    const [startYear, startMonth, startDay] = start.split('-');
                    const [endYear, endMonth, endDay] = end.split('-');

                    const startDate = new Date(startYear, startMonth - 1, startDay);
                    const endDate = new Date(endYear, endMonth - 1, endDay);

                    // Define hotel IDs
                    const hotelIds = {
                        Piccadilly: '1e044878-1336-4235-86d6-b244008c36e6',
                        leicester: '00923d1f-17bd-44a2-babc-ad88007efe3c'
                    };

                    // Apply hotel and date selection to Mews Distributor API
                    api.setStartDate(startDate);
                    api.setEndDate(endDate);
                    // api.showRooms(hotelIds[hotel]);
                    api.open();
                });
            }
        );
    </script>
</body>
</html>'''

@app.route('/')
def index():
    return render_template_string(HTML)

if __name__ == '__main__':
    app.run(debug=True)