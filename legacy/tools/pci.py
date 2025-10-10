from flask import Flask, request, jsonify, render_template_string, Response, send_file
from datetime import datetime, timedelta, timezone
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from tempfile import NamedTemporaryFile
import xml.etree.ElementTree as ET
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import os
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

driver = webdriver.Chrome(ChromeDriverManager().install())


os.system("pkill -9 chrome")

from selenium import webdriver

options = webdriver.ChromeOptions()
options.add_argument("--headless")
driver = webdriver.Chrome(options=options)


# Open a blank page
driver.get("about:blank")


app = Flask(__name__)


HTML = '''
<script src="https://pay.sandbox.datatrans.com/upp/payment/js/secure-fields-2.0.0.js"></script>

<form>
  <div>
    <div>
      <label for="card-number-placeholder">Card Number</label>
      <!-- card number container -->
      <div id="card-number-placeholder" style="width: 250px;"></div>
    </div>

    <div>
      <label for="cvv-placeholder">Cvv</label>
      <!-- cvv container -->
      <div id="cvv-placeholder" style="width: 90px;"></div>
    </div>

    <button type="button" id="go">Get Token!</button>
  </div>
</form

var secureFields = new SecureFields();

// Another Secure Fields instance
// e.g. var secureFields2 = new SecureFields();

secureFields.initTokenize("1100007006", {
  cardNumber: "card-number-placeholder",
  cvv: "cvv-placeholder"
});

$(function() {
  $("#go").click(function() {
    secureFields.submit({ // submit the "form"
      expm: 12,
      expy: 26,
      usage: "SIMPLE" 
    });
  });
});

secureFields.on("success", function(data) {
  if (data.transactionId) {
    // transmit data.transactionId and the rest
    // of the form to your server    
  }
});

/*secureFields.destroy();*/
'''

# Inject the HTML content into the browser
driver.execute_script("document.write(arguments[0])", HTML)

# Wait for the page to load
time.sleep(5)

# Click the button to trigger the JavaScript function
button = driver.find_element(By.ID, "go")
button.click()

# Wait for the JavaScript to execute
time.sleep(5)

# Close the browser
driver.quit()