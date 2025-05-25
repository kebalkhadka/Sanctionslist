from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import csv

# === Step 1: Create 'output' folder if it doesn't exist ===
output_folder = "output"
os.makedirs(output_folder, exist_ok=True)

# CSV file path
csv_file_path = os.path.join(output_folder, "interpol_red_notices.csv")

# Path to your msedgedriver
edge_driver_path = r"C:\Program Files\edgedriver_win64\msedgedriver.exe"
service = Service(edge_driver_path)
driver = webdriver.Edge(service=service)

driver.get("https://www.interpol.int/en/How-we-work/Notices/Red-Notices/View-Red-Notices")

all_data = []

try:
    while True:
        # Wait for red notice items to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".redNoticesList__item"))
        )

        # Extract data
        items = driver.find_elements(By.CSS_SELECTOR, ".redNoticesList__item")
        for item in items:
            try:
                name = item.find_element(By.CSS_SELECTOR, ".redNoticeItem__labelLink").text.replace("\n", " ")
                age = item.find_element(By.CSS_SELECTOR, ".ageCount").text
                nationality = item.find_element(By.CSS_SELECTOR, ".nationalities").text
                all_data.append([name, age, nationality])
                print(f"Name: {name}\nAge: {age}\nNationality: {nationality}\n")
            except Exception as e:
                print("Error extracting item:", e)

        # Check if the next button is disabled
        try:
            next_li = driver.find_element(By.CSS_SELECTOR, "li.nextElement")
        
            if 'hidden' in next_li.get_attribute("class"):
                print("No more pages (Next is disabled).")
                break

            # Click the next button using JavaScript
            next_button = next_li.find_element(By.CSS_SELECTOR, "a.nextIndex")
            driver.execute_script("arguments[0].click();", next_button)
            time.sleep(2)

        except Exception as e:
            print("No more pages or error navigating to next:", e)
            break

except Exception as e:
    print("Unhandled error:", e)

finally:
    driver.quit()

    # Save CSV with utf-8-sig encoding (helps Excel open it with proper encoding)
    with open(csv_file_path, mode='w', newline='', encoding='utf-8-sig') as file:
        writer = csv.writer(file)
        writer.writerow(["Name", "Age", "Nationality"])  # Header
        writer.writerows(all_data)  # Data rows

    print(f"✅ Data saved to {csv_file_path}")
