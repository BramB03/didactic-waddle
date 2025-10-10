from flask import Flask, render_template_string

app = Flask(__name__)

# HTML Content with Banner and Mews Booking Engine Widget
html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hotel Booking Page</title>
    <style>
        /* General Styles */
        body {
            margin: 0;
            font-family: Arial, sans-serif;
            color: #333;
        }

        /* Banner Styles */
        .banner {
            background: url('https://via.placeholder.com/1920x400') no-repeat center center;
            background-size: cover;
            height: 400px;
            position: relative;
            color: white;
            text-align: center;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }

        .banner-overlay {
            background-color: rgba(0, 0, 0, 0.6);
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
        }

        .banner-content {
            position: relative;
            z-index: 2;
        }

        .banner h1 {
            font-size: 3rem;
            margin: 0;
        }

        .banner p {
            font-size: 1.2rem;
        }

        .banner a {
            margin-top: 20px;
            display: inline-block;
            background: #ff5722;
            color: white;
            padding: 10px 20px;
            text-decoration: none;
            border-radius: 5px;
            font-size: 1rem;
        }

        /* Booking Widget Section */
        .booking-widget {
            text-align: center;
            padding: 20px;
        }

        .booking-widget h2 {
            font-size: 2rem;
            margin-bottom: 20px;
        }
    </style>
    <script>
        // Load the Mews Booking Engine Widget script
        (function(d, s, id) {
            var js, fjs = d.getElementsByTagName(s)[0];
            if (d.getElementById(id)) return;
            js = d.createElement(s);
            js.id = id;
            js.src = "https://widgets.mews.com/bookingengine/production/initialize.min.js";
            fjs.parentNode.insertBefore(js, fjs);
        })(document, 'script', 'mews-widget-js');
    </script>
</head>
<body>

    <!-- Banner Section -->
    <div class="banner">
        <div class="banner-overlay"></div>
        <div class="banner-content">
            <h1>Welcome to Our Hotel</h1>
            <p>Book your stay with us for an unforgettable experience.</p>
            <a href="#booking-widget">Book Now</a>
        </div>
    </div>

    <!-- Booking Engine Widget Section -->
    <div id="booking-widget" class="booking-widget">
        <h2>Book Your Stay</h2>
        <!-- Booking Engine Widget -->
        <div id="mews-booking-engine-widget"></div>
        <script>
            document.addEventListener("DOMContentLoaded", function () {
                // Initialize the Mews Booking Engine Widget
                MEWS_BookingEngine.initialize({
                    containerId: "mews-booking-engine-widget",
                    propertyCode: "YOUR_PROPERTY_CODE", // Replace with your Mews property code
                    language: "en-US", // Change to your preferred language code
                    currency: "EUR", // Change to your preferred currency
                    dateFormat: "MM/DD/YYYY" // Adjust the date format as needed
                });
            });
        </script>
    </div>

</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(html_content)

if __name__ == "__main__":
    app.run(debug=True)
