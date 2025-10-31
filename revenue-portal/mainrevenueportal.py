# bookingengine/mainbookingengine.py
from flask import Flask, render_template, request, render_template_string

app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static"
)

@app.route("/widget")
def booking_widget():
    return render_template("widget-loader.html")

@app.route("/")
def home():
    return render_template("index-revenueportal.html")

# ⬇️ Add this new route
@app.route("/search")
def booking_search():
    payload = request.args.to_dict(flat=True)
    # Simple pretty page showing the payload as JSON
    return render_template_string("""
    <!doctype html>
    <html lang="en">
    <head>
      <meta charset="utf-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1" />
      <title>Search Payload</title>
      <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-slate-50 text-slate-900">
      <div class="max-w-3xl mx-auto p-6">
        <h1 class="text-2xl font-bold mb-4">Received Payload</h1>
        <pre class="bg-white border border-slate-200 rounded-2xl shadow-sm p-4 text-sm">{{ payload|tojson(indent=2) }}</pre>
        <p class="mt-4">
          <a href="/bookingengine/" class="text-blue-600 underline">← Back to Booking Engine</a>
        </p>
      </div>
    </body>
    </html>
    """, payload=payload)