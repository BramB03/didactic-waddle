from flask import Flask, request, jsonify, render_template_string, Response, send_file
from datetime import datetime, timedelta, timezone
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from tempfile import NamedTemporaryFile
import subprocess
import json
from tshDefs import get_utc_time, parse_xml_to_dict,split_data_by_day, dict_to_xml, mergeDays, format_element
import xml.dom.minidom
import xml.etree.ElementTree as ET
import os
import tempfile
import time


app = Flask(__name__)

HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ISTAT MERGE TOOL</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f0f0f0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }
        .form-container {
            background: white;
            padding: 26px;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            width: 590px;
        }
        .form-title {
            background-color: black;
            color: white;
            padding: 13px;
            font-size: 23px;
            text-align: center;
            border-top-left-radius: 10px;
            border-top-right-radius: 10px;
        }
        .form-fields {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .form-field {
            margin: 13px 0;
            width: 45%;
        }
        label {
            font-size: 20px;
            display: block;
            margin-bottom: 5px;
        }
        input[type="file"], select {
            font-size: 16px;
            padding: 5px;
            width: 100%;
        }
        button {
            background-color: #007BFF;
            color: white;
            border: none;
            padding: 13px;
            font-size: 18px;
            border-radius: 8px;
            cursor: pointer;
        }
        button:hover {
            background-color: #0056b3;
        }
        button:disabled {
            background-color: #b0b0b0;
            cursor: not-allowed;
        }
        .fading-border {
            padding: 10px;
            background: radial-gradient(circle, white, black);
            display: inline-block;
        }

        .fading-border img {
            display: block;
        }
        img {
            height: 100px;
        }
    </style>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <div class="form-container">
        <div class="form-title">
            ISTAT MERGE TOOL
        </div>
        <form id="myForm" method="post" action="/process" enctype="multipart/form-data">
            <div class="form-fields">
                <!-- Choose an Option Dropdown -->
                <div class="form-field">
                    <label for="selection">Choose an Option:</label>
                    <select id="selection" name="selection" required>
                        <option value="" disabled selected>Select an option</option>
                        <option value="Bologna Monthly">Bologna Monthly</option>
                        <option value="Belfiore Monthly">Belfiore Monthly</option>
                        <option value="Spain police">Spain police</option>
                        <option value="Lavagnini">Lavagnini</option>
                    </select>
                </div>
                
                <!-- City Dropdown (initially hidden) -->
                <div class="form-field" id="cityField" style="display: none;">
                    <label for="city">Choose a City:</label>
                    <select id="city" name="city" disabled>
                        <option value="" disabled selected>Select a city</option>
                        <option value="Madrid">Madrid</option>
                        <option value="Barcelona">Barcelona</option>
                        <option value="Lavagnini">Lavagnini</option>
                    </select>
                </div>
            </div>

            <div class="form-field">
                <label for="hotelFile">Upload Hotel File:</label>
                <input type="file" id="hotelFile" name="hotelFile" accept=".xml" required>
            </div>
            <div class="form-field">
                <label for="studentFile">Upload Student File:</label>
                <input type="file" id="studentFile" name="studentFile" accept=".xml" required>
            </div>
            <div class="form-field">
                <label for="extendedStayFile">Upload Extended Stay File:</label>
                <input type="file" id="extendedStayFile" name="extendedStayFile" accept=".xml" required>
            </div>
            <button type="submit" id="submitBtn" disabled>Submit</button>
        </form>
    </div>

    <script>
        const selection = document.getElementById("selection");
        const cityField = document.getElementById("cityField");
        const citySelect = document.getElementById("city");
        const submitBtn = document.getElementById("submitBtn");

        // Enable the submit button if a selection is made
        selection.addEventListener("change", () => {
            if (selection.value === "Spain police") {
                cityField.style.display = "block";  // Show the city select dropdown
                citySelect.disabled = false;       // Enable the city dropdown
            } else {
                cityField.style.display = "none";  // Hide the city select dropdown
                citySelect.disabled = true;        // Disable the city dropdown
            }

            // Check if a city is selected and enable/disable submit button
            checkCitySelection();
        });

        // Enable submit button only if city is selected
        citySelect.addEventListener("change", checkCitySelection);

        function checkCitySelection() {
            submitBtn.disabled = !citySelect.value;  // Disable if no city is selected
        }

        // Initial validation: Ensure submit button is disabled if no selection or city
        submitBtn.disabled = selection.value === "" || !citySelect.value;
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/process', methods=['POST'])
def process():
    # Retrieve files
    parsedData1 = parse_xml_to_dict(request.files['hotelFile'])
    parsedData2 = parse_xml_to_dict(request.files['studentFile'])
    parsedData3 = parse_xml_to_dict(request.files['extendedStayFile'])
    selection = request.form['selection']
    if selection == "Spain police":
        city = request.form['city']

    # Check and print the result
    if selection != "Spain police":
        if parsedData1 is not None:
            dailyEntries1 = split_data_by_day(parsedData1)
        else:
            print("Failed to parse the first XML file.")

        if parsedData2 is not None:
            dailyEntries2 = split_data_by_day(parsedData2)
        else:
            print("Failed to parse the second XML file.")
            
        if parsedData3 is not None:
            dailyEntries3 = split_data_by_day(parsedData3)
        else:
            print("Failed to parse the third XML file.")
    else:
        dailyEntries1 = parsedData1
        dailyEntries2 = parsedData2
        dailyEntries3 = parsedData3
        
    temp_file = None
    temp_file_path = None
    try:
        # Serialize each dictionary separately
        serialized_dict1 = json.dumps(dailyEntries1)
        serialized_dict2 = json.dumps(dailyEntries2)
        serialized_dict3 = json.dumps(dailyEntries3)

        dataSend = json.dumps({"dailyEntries1": dailyEntries1, "dailyEntries2": dailyEntries2, "dailyEntries3": dailyEntries3})
        # Use subprocess to call script2.py and pass the serialized dictionaries as arguments
        
        if selection == "Bologna Monthly":
            result = subprocess.run(
                ["python3", "legacy/tools/ISTAT Bologna Monthly.py"],
                input=dataSend,
                text=True,
                capture_output=True
            )
                        
        elif selection == "Belfiore Monthly":
            print("Belfiore Monthly")
            result = subprocess.run(
                ["python3", "-u", "legacy/tools/ISTAT Belfiore Monthly.py"],
                input=dataSend,
                text=True,
                capture_output=True
            )
        
        elif selection == "Spain police":
            print("Spain police")
            result = subprocess.run(
                ["python3", "legacy/tools/Spain police.py", city],
                input=dataSend,
                text=True,
                capture_output=True
            )
        
        elif selection == "Lavagnini Monthly":
            print("Spain police")
            result = subprocess.run(
                ["python3", "legacy/tools/ISTAT Lavagnini Monthly.py", city],
                input=dataSend,
                text=True,
                capture_output=True
            )


            
        else:
            return jsonify({"status": "error", "message": "Invalid selection."})
        
        # Capture the output from the subprocess and map it to a temp file
        if result.returncode == 0:
            stdout_lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
            if not stdout_lines:
                return jsonify({"status": "error", "message": "No output returned from subprocess."})

            temp_file_path = None
            for candidate in reversed(stdout_lines):
                if os.path.exists(candidate):
                    temp_file_path = candidate
                    break

            if temp_file_path:
                import calendar
                from datetime import datetime
                # Return the file as a downloadable response
                if selection == "Bologna Monthly":
                    current_month = datetime.today().month
                    last_month = current_month - 1 if current_month > 1 else 12
                    last_month_name = calendar.month_name[last_month]
                    return send_file(
                        temp_file_path,
                        mimetype="application/xml",
                        as_attachment=True,
                        download_name="ISTAT Bologna " + last_month_name +".xml"
                    )
                elif selection == "Spain police":
                    yesterday = datetime.today() - timedelta(days=1)
                    yesterday_date = yesterday.strftime('%d %B %Y')
                    return send_file(
                        temp_file_path,
                        mimetype="application/xml",
                        as_attachment=True,
                        download_name="Spain police " + yesterday_date +".xml"
                    )
                elif selection == "Belfiore Monthly":
                    current_month = datetime.today().month
                    last_month = current_month - 1 if current_month > 1 else 12
                    last_month_name = calendar.month_name[last_month]
                    return send_file(
                        temp_file_path,
                        mimetype="application/xml",
                        as_attachment=True,
                        download_name="ISTAT Belfiore " + last_month_name +".xml"
                    )
            else:
                print(f"Unexpected subprocess stdout: {stdout_lines}")
                return jsonify({"status": "error", "message": "File not found."})

        else:
            return jsonify({"status": "error1", "message": result.stderr})

    except Exception as e:
        return jsonify({"status": "error2", "message": str(e)})

    finally:
        # Clean up the temporary file if it exists and is not None
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
                print(f"Temporary file {temp_file_path} has been removed.")
            except Exception as e:
                print(f"Error removing file {temp_file_path}: {e}")
                
if __name__ == '__main__':
    app.run(debug=True)
