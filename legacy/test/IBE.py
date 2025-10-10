from flask import Flask, render_template_string

app = Flask(__name__)

@app.route('/')
def index():
    return render_template_string(HTML)

HTML = '''
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <title>MyBookingEngine</title>
    <!-- Load Mews Distributor as early as possible -->
    <script src="https://api.mews.com/distributor/distributor.min.js"></script>
  </head>
  <body>
    <script>
      document.addEventListener('DOMContentLoaded', function () {
        Mews.Distributor(
          {
            configurationIds: [
              '2d61cc29-2fa9-4f4a-bf46-b2e400ab6207', // identifier of the IBE configuration itself, first ID in the list of 2
              '55c8c6ba-1890-462e-904e-b30000a1055f'
            ],
          },
          function (api) {
            // Compute tomorrow and the day after tomorrow in the user's local time
            const now = new Date();
            const startDate = new Date(now.getFullYear(), now.getMonth(), now.getDate() + 1);
            const endDate = new Date(now.getFullYear(), now.getMonth(), now.getDate() + 2);

            // Preload dates and immediately open Distributor
            api.setStartDate(startDate);
            api.setEndDate(endDate);
            // api.showRooms();
            api.setCity('69a0acda-3c2f-4686-a6a7-586fa33c826c'); // City id, Berlin, found in the IBE settings, second ID listed.
            api.showHotels();
            api.showRooms('f5b03301-5673-497f-8260-b2e400ab4d43'); // Hoten ID, found under general settings of Mews itself.
            // api.setVoucherCode();
            api.open();
          },
          { dataBaseUrl: 'https://api.mews.com' }
        );
      });
    </script>
  </body>
</html>
'''

if __name__ == '__main__':
    app.run(debug=True)