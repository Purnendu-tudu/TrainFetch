from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import os

# Initialize a cache dictionary
train_cache = {}

def fetch_train_data(driver, train_url):
    # Check if the data is already in cache
    if train_url in train_cache:
        print(f"Fetching data from cache for {train_url}")
        return train_cache[train_url]

    # Load the webpage
    driver.get(train_url)

    # Wait for the dynamic content to load
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "lts-result_table")))

    # Get the page source after the dynamic content has loaded
    page_source = driver.page_source

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(page_source, "html.parser")

    # Extract the train name
    train_name = soup.find('div', class_="col-xs-12 lts-timeline_title").find_all('span')
    train_name = train_name[0].text

    # Find the first row of the table
    first_row = soup.find('table').find('tbody').find('tr')

    # Extract data from the first row
    station = first_row.find_all('td')[0].get_text(strip=True)
    arrival = first_row.find_all('td')[1].get_text(strip=True)
    train_status = first_row.find_all('td')[2].get_text(strip=True)
    halt_time = first_row.find_all('td')[3].get_text(strip=True)
    platform = first_row.find_all('td')[4].get_text(strip=True)
    locomotive_reverse = first_row.find_all('td')[5].get_text(strip=True)

    # Store the extracted data in cache
    train_cache[train_url] = {
        "train_name": train_name,
        "station": station,
        "arrival": arrival,
        "train_status": train_status,
        "halt_time": halt_time,
        "platform": platform,
        "locomotive_reverse": locomotive_reverse
    }

    return train_cache[train_url]

def fetch_all_train_data(urls):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-browser-side-navigation")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--remote-debugging-port=9222")
    chrome_options.add_experimental_option("prefs", {
        "profile.managed_default_content_settings.images": 2,  # Disable images
        "profile.managed_default_content_settings.javascript": 2  # Disable JavaScript
    })

    # Initialize the WebDriver with the specified options
    driver = webdriver.Chrome(options=chrome_options)

    results = []
    try:
        for url in urls:
            data = fetch_train_data(driver, "https://www.railyatri.in/live-train-status/" + str(url))
            results.append(data)
            print(f"Fetched data for {url}")
    finally:
        # Close the WebDriver
        driver.quit()
    
    return results

def generate_pdf_with_multiple_pages(train_data_list, date):

    # Ensure output directory exists
    output_dir = "output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Set the PDF file path inside the output directory
    pdf_filename = os.path.join(output_dir, f"all_trains_report_{date}.pdf")
    c = canvas.Canvas(pdf_filename, pagesize=letter)
    
    # Set font and size
    c.setFont("Courier", 12)
    y_position = 750  # Initial y position for text
    max_y = 50  # Maximum y position before starting a new page
    page_height = 800  # Page height for letter size
    
    # Write train data to PDF
    for train_data in train_data_list:
        c.drawString(100, y_position, f"{train_data['train_name']}")
        c.drawString(100, y_position - 20, f"Station: {train_data['station']}")
        c.drawString(100, y_position - 40, f"Dpt Time: {train_data['arrival']}")
        # c.drawString(100, y_position - 60, f"Train Status: {train_data['train_status']}")
        # c.drawString(100, y_position - 80, f"Halt Time: {train_data['halt_time']}")
        # c.drawString(100, y_position - 100, f"Platform: {train_data['platform']}")
        # c.drawString(100, y_position - 120, f"Locomotive Reverse: {train_data['locomotive_reverse']}")
        c.drawString(100, y_position - 60, "-" * 50)
        y_position -= 80  # Adjust y position
        
        # Check if content exceeds page height and start a new page if needed
        if y_position < max_y:
            c.showPage()  # Start a new page
            y_position = page_height - 50  # Reset y position for new page

    c.save()

# Prompt user for the date
date = input("Please enter the date (YYYY-MM-DD): ")

# Read train codes from a text file (comma-separated)
with open('train_codes.txt', 'r') as file:
    train_codes_content = file.read()
    traincodes = {int(code.strip()) for code in train_codes_content.split(',') if code.strip().isdigit()}

# Fetch the train data for all URLs
start_time = time.time()
all_train_data = fetch_all_train_data(traincodes)
end_time = time.time()

generate_pdf_with_multiple_pages(all_train_data, date)

print(f"Total time taken: {end_time - start_time} seconds")
