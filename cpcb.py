import streamlit as st
from datetime import datetime
import math
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import pandas as pd
from selenium.webdriver.common.action_chains import ActionChains
from lxml import html
from selenium.common.exceptions import WebDriverException
from datetime import datetime
from selenium.webdriver.support import expected_conditions as EC

st.set_page_config(page_title="EPR Dashboard Scraper", layout="centered")

def convert_cat(text):
    roman = ['I', 'II', 'III', 'IV', 'V']
    text = re.sub(r'\b([1-5])\b', lambda m: roman[int(m.group(1))-1], text)
    text = text.replace('-', ' ').replace('CAT', 'Cat').replace('cat', 'Cat').strip()

def custom_wait_clickable_and_click(elem, attempts=20):
    count = 0
    a='no success'
    while count < attempts:
        try:
            if(a!='success'):
                elem.click()
                a='success'
            elif(a=='success'):
                break
        except:
            time.sleep(1)
            count = count + 1
# --- Streamlit UI ---
st.title("📊 EPR Dashboard Scraper")

# --- Input Credentials ---
with st.form("login_form"):
    mail = st.text_input("Enter your username/email:")
    password = st.text_input("Enter your password:", type="password")
    submitted = st.form_submit_button("Submit Credentials")

# --- Initialize Browser ---
def initialize_browser():
    global driver
    driver = st.session_state.get("driver", None)
    if driver is None:
        options = Options()
        options.add_experimental_option("detach", True)
        driver = webdriver.Edge(options=options)
        driver.maximize_window()
        driver.implicitly_wait(15)
        st.session_state.driver = driver
    return driver

# --- Open Browser and Login ---
def open_browser_and_login():
    global driver
    driver = initialize_browser()

    st.warning("🚀 Browser is launching... Please log in manually including CAPTCHA and OTP.")
    driver.get('https://eprplastic.cpcb.gov.in/#/plastic/home')

    # --- Fill login form automatically ---
    try:
        action = ActionChains(driver)
        username_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="user_name"]'))
        )
        password_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="password_pass"]'))
        )

        action.click(username_input).perform()
        username_input.send_keys(mail)
        time.sleep(1)
        action.click(password_input).perform()
        password_input.send_keys(password)
    except Exception as e:
        st.warning(f"⚠️ Unable to auto-fill credentials: {e}")

    st.info("🕒 Waiting for login... You have 10 minutes to complete login.")
    WebDriverWait(driver, 600).until(
        EC.presence_of_element_located((By.XPATH, '//span[@class="account-name"]'))
    )
    st.success("✅ Login detected.")

    # --- Fetch user details ---
    email_id = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.XPATH, '//tbody[@id="ScrollableSimpleTableBody"]//span[contains(text(),"@")]')
        )
    ).text

    time.sleep(2)
    driver.get("https://eprplastic.cpcb.gov.in/#/epr/pibo-dashboard-view")

    entity_type = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.XPATH, '//p[text()="User Type"]/following::span[1]')
        )
    ).text

    entity_name = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.XPATH, '//p[text()="Company Name"]/following::span[1]')
        )
    ).text

    # --- Save values to session_state ---
    st.session_state["email_id"] = email_id
    st.session_state["entity_name"] = entity_name
    st.session_state["entity_type"] = entity_type
    st.session_state["is_logged_in"] = True

    st.info(f"📧 Logged in as: {email_id}")
    st.info(f"🏢 Entity Name: {entity_name}")
    st.info(f"👤 Entity Type: {entity_type}")

