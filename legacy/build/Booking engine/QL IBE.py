from flask import Flask, render_template_string
from datetime import datetime, timedelta

app = Flask(__name__)

HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Luxury Hotel - Book Your Stay</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            overflow-x: hidden;
        }

        .hero {
            height: 100vh;
            background: linear-gradient(135deg, rgba(0,0,0,0.7), rgba(0,0,0,0.4)), 
                        url('https://images.unsplash.com/photo-1566073771259-6a8506099945?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2070&q=80');
            background-size: cover;
            background-position: center;
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
        }

        .hero-content {
            text-align: center;
            color: white;
            max-width: 800px;
            padding: 0 20px;
            animation: fadeInUp 1s ease-out;
        }

        .hero h1 {
            font-size: 4rem;
            font-weight: 300;
            margin-bottom: 1rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        }

        .hero p {
            font-size: 1.4rem;
            margin-bottom: 2rem;
            opacity: 0.9;
        }

        .cta-button {
            display: inline-block;
            background: linear-gradient(45deg, #ff6b6b, #ee5a52);
            color: white;
            padding: 15px 40px;
            text-decoration: none;
            border-radius: 50px;
            font-size: 1.1rem;
            font-weight: 600;
            transition: all 0.3s ease;
            box-shadow: 0 8px 25px rgba(238, 90, 82, 0.3);
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .cta-button:hover {
            transform: translateY(-3px);
            box-shadow: 0 12px 35px rgba(238, 90, 82, 0.4);
        }

        .booking-section {
            padding: 80px 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-align: center;
        }

        .booking-container {
            max-width: 1200px;
            margin: 0 auto;
        }

        .booking-section h2 {
            font-size: 3rem;
            margin-bottom: 2rem;
            font-weight: 300;
        }

        .booking-section p {
            font-size: 1.2rem;
            margin-bottom: 3rem;
            opacity: 0.9;
        }

        .booking-widget {
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.2);
            margin: 0 auto;
            max-width: 800px;
            position: relative;
            overflow: hidden;
        }

        .booking-widget::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, #ff6b6b, #ee5a52, #667eea, #764ba2);
        }

        .widget-title {
            color: #333;
            font-size: 1.5rem;
            margin-bottom: 1.5rem;
            text-align: center;
        }

        /* Mews Booking Engine Container */
        #mews-booking-engine {
            min-height: 400px;
            border-radius: 15px;
            overflow: hidden;
        }

        .features {
            padding: 100px 20px;
            background: #f8f9fa;
        }

        .features-container {
            max-width: 1200px;
            margin: 0 auto;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 40px;
        }

        .feature-card {
            background: white;
            padding: 40px 30px;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }

        .feature-card:hover {
            transform: translateY(-10px);
        }

        .feature-icon {
            font-size: 3rem;
            margin-bottom: 1rem;
        }

        .feature-card h3 {
            font-size: 1.5rem;
            margin-bottom: 1rem;
            color: #333;
        }

        .feature-card p {
            color: #666;
            line-height: 1.6;
        }

        .footer {
            background: #333;
            color: white;
            text-align: center;
            padding: 40px 20px;
        }

        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .floating-book-btn {
            position: fixed;
            bottom: 30px;
            right: 30px;
            background: linear-gradient(45deg, #ff6b6b, #ee5a52);
            color: white;
            border: none;
            border-radius: 50px;
            padding: 15px 25px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            box-shadow: 0 8px 25px rgba(238, 90, 82, 0.3);
            transition: all 0.3s ease;
            z-index: 1000;
        }

        .floating-book-btn:hover {
            transform: translateY(-3px);
            box-shadow: 0 12px 35px rgba(238, 90, 82, 0.4);
        }

        @media (max-width: 768px) {
            .hero h1 {
                font-size: 2.5rem;
            }
            
            .hero p {
                font-size: 1.1rem;
            }
            
            .booking-section h2 {
                font-size: 2rem;
            }
            
            .booking-widget {
                padding: 20px;
            }
        }
    </style>
</head>
<body>
    <!-- Hero Section -->
    <section class="hero">
        <div class="hero-content">
            <h1>Luxury Awaits</h1>
            <p>Experience unparalleled comfort and elegance in the heart of the city</p>
            <a href="#booking" class="cta-button">Book Your Stay</a>
        </div>
    </section>

    <!-- Booking Section -->
    <section id="booking" class="booking-section">
        <div class="booking-container">
            <h2>Reserve Your Perfect Stay</h2>
            <p>Select your dates and discover our exclusive offers</p>
            
            <div class="booking-widget">
                <h3 class="widget-title">🏨 Book Direct & Save</h3>
                <!-- Mews Booking Engine will be loaded here -->
                <div id="mews-booking-engine">
                    <div style="display: flex; align-items: center; justify-content: center; height: 400px; background: #f8f9fa; border-radius: 10px; color: #666;">
                        <div style="text-align: center;">
                            <div style="font-size: 2rem; margin-bottom: 1rem;">🏨</div>
                            <p>Loading booking engine...</p>
                            <p style="font-size: 0.9rem; margin-top: 0.5rem;">Please configure your Mews settings</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Features Section -->
    <section class="features">
        <div class="features-container">
            <div class="feature-card">
                <div class="feature-icon">🌟</div>
                <h3>Luxury Rooms</h3>
                <p>Elegantly designed rooms with modern amenities and breathtaking city views</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon">🍽️</div>
                <h3>Fine Dining</h3>
                <p>Award-winning restaurants serving exquisite cuisine from around the world</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon">💆</div>
                <h3>Spa & Wellness</h3>
                <p>Rejuvenate your body and mind at our world-class spa and fitness center</p>
            </div>
        </div>
    </section>

    <!-- Footer -->
    <footer class="footer">
        <p>&copy; 2025 Luxury Hotel. All rights reserved.</p>
    </footer>

    <!-- Floating Book Button -->
    <button class="floating-book-btn" onclick="scrollToBooking()">
        📅 Book Now
    </button>

    <!-- Mews Booking Engine Script -->
    <script>
        // Step 1: Install Mews Booking Engine Loader Script
        (function(d, s, id) {
            var js, fjs = d.getElementsByTagName(s)[0];
            if (d.getElementById(id)) return;
            js = d.createElement(s); js.id = id;
            js.src = "https://www.mews.com/booking-engine/loader.js";
            fjs.parentNode.insertBefore(js, fjs);
        }(document, 'script', 'mews-booking-engine-loader'));

        // Step 2: Configure and Initialize Booking Engine
        window.mewsBookingEngineConfig = {
            // REPLACE THESE WITH YOUR ACTUAL MEWS CONFIGURATION
            configurationIds: ['8077aee8-f5a5-4643-bc1f-ae94011b36bd'], // Replace with your actual config ID
            language: 'en-US',
            currency: 'USD',
            
            // Optional: Custom styling
            theme: {
                primaryColor: '#ff6b6b',
                fontFamily: 'Segoe UI, Tahoma, Geneva, Verdana, sans-serif'
            },
            
            // Container where the booking engine will be loaded
            container: '#mews-booking-engine',
            
            // Optional: Callback functions
            onLoad: function() {
                console.log('Mews Booking Engine loaded successfully');
            },
            
            onError: function(error) {
                console.error('Mews Booking Engine error:', error);
                document.getElementById('mews-booking-engine').innerHTML = `
                    <div style="text-align: center; padding: 40px; color: #666;">
                        <div style="font-size: 2rem; margin-bottom: 1rem;">⚠️</div>
                        <p>Unable to load booking engine</p>
                        <p style="font-size: 0.9rem; margin-top: 0.5rem;">Please check your configuration</p>
                    </div>
                `;
            }
        };

        // Step 3: Load the booking engine when the page is ready
        window.addEventListener('load', function() {
            if (window.Mews && window.Mews.BookingEngine) {
                window.Mews.BookingEngine.init(window.mewsBookingEngineConfig);
            } else {
                // Fallback if Mews script hasn't loaded yet
                setTimeout(function() {
                    if (window.Mews && window.Mews.BookingEngine) {
                        window.Mews.BookingEngine.init(window.mewsBookingEngineConfig);
                    }
                }, 1000);
            }
        });

        // Smooth scrolling function
        function scrollToBooking() {
            document.getElementById('booking').scrollIntoView({
                behavior: 'smooth'
            });
        }

        // Smooth scroll for CTA button
        document.querySelector('.cta-button').addEventListener('click', function(e) {
            e.preventDefault();
            scrollToBooking();
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
