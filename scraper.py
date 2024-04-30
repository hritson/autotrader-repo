from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
import re

start_time = time.time()

vehicle_type = "van"

params = {
    "postcode": "NN116FB",
    "year_to": "2024", #insert current date; removes all new cars
    "advertising-location": "at_vans",
    "price-to": "10000",
    "price-from": "500",
    "maximum-mileage": "150000",
    "minimum-mileage": "5000"
}


driver = webdriver.Chrome()
driver.maximize_window()
timeout = 8
base_url = "https://www.autotrader.co.uk/"+ f"{vehicle_type}" + "-search?"


url = base_url + "&".join([f"{key}={value}" for key, value in params.items()])

driver.get(url)
driver.implicitly_wait(0.6)

#Shut down cookies
try:
    # Wait for the iframe to be present
    iframe = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.ID, "sp_message_iframe_1086457")))    
    # Switch to the cookie popup iframe
    driver.switch_to.frame(iframe)
    reject_cookie = driver.find_element(By.XPATH, "//button[contains(text(), 'Reject All')]")
    reject_cookie.click()
    
except TimeoutException:
    print("Timed out waiting for the 'Reject All' button button.")
except NoSuchElementException:
    print("The 'Reject All' button element was not found on the webpage.")
except Exception as e:
    print("An error occurred:", str(e))
    
time.sleep(1)
try:
    pages = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.XPATH, "//p[@data-testid='pagination-show']")))
    page_count = int(pages.text.split(" ")[3].replace(',', ''))
    print(page_count)
except Exception as e:
    print("An error occurred:", str(e))


def extract_ad_info(ad):
    try:
        model = ad.find_element(By.XPATH, ".//a[@data-testid='search-listing-title']").text
        specs = ad.find_element(By.XPATH, ".//ul[@data-testid='search-listing-specs']").text
        price = ad.find_element(By.XPATH, ".//*[contains(text(), '£')]").text
        location = ad.find_element(By.XPATH, ".//p[@data-testid='search-listing-seller']").text
        return model, specs, price, location
    except NoSuchElementException:
        #print("Error")
        return None, None, None, None

def string_to_year(year_string):
    try:
        year_datetime = datetime.strptime(year_string, '%Y')
        year = year_datetime.year
        return year
    except ValueError:
        print("Error: Invalid year format")
        return None
    
keyList = ["Make", "Model", "Price", "Year", "Mileage", "Location"]
car_info = {key: [] for key in keyList}
c = 0


for _ in range(0, 50):
    
    results = driver.find_element(By.XPATH, "//ul[@data-testid='desktop-search']")
    ad_listings = results.find_elements(By.XPATH, "./*/section")
    
    for ad in ad_listings:
        span_elements = ad.find_elements(By.XPATH, "./span")
        if not span_elements:  # Check if there are no <span> child elements
            model, specs, price, location = extract_ad_info(ad)
            if model and specs and price and location:
                car_info["Make"].append(model.split(" ")[0])
                car_info["Model"].append(' '.join(model.split(" ")[1:]))
                car_info["Price"].append(price.split(" ")[0].replace('£', ''))
                car_info["Year"].append(string_to_year(re.findall(r"\d{4}", specs)[0]))
                car_info["Mileage"].append(int(re.findall(r"([\d,]+)\s+miles", specs)[0].replace(',', '')))
                car_info["Location"].append(re.findall(r"ocation\s*(.*)", location)[0])
                c+=1
        else:
            print("promotion skipped")
            
    next_page = driver.find_element(By.XPATH, "//a[@data-testid='pagination-next']")
    next_page.click()

car_info["Price"] = [int(price.replace(',', '')) if "," in price else int(price) for price in car_info["Price"]] 

df = pd.DataFrame(car_info)
print(df)

df.to_csv('car_market.csv', index=False)

#driver.close()

end_time = time.time()
runtime = end_time - start_time
print("Runtime:", round(runtime, 2), "seconds")