from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
from bs4 import BeautifulSoup
from selenium.webdriver.common.alert import Alert
from datetime import datetime
import pandas as pd

criteria = {
    "vehicle_type": 'vans',
    "postcode": "LS1 2AD",
    "radius": "20",
    "year_from": "2010",
    "year_to": "2014",
    "price_from": "3000",
    "price_to": "6500",
}

driver = webdriver.Chrome()
timeout = 8
url = f"https://www.autotrader.co.uk"#/"{criteria['vehicle_type']}/used-{criteria['vehicle_type']}"
driver.get(url)
driver.implicitly_wait(2)

source = driver.page_source
content = BeautifulSoup(source, "html.parser")
