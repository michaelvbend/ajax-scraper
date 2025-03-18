from dataclasses import dataclass
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selectors_list import SITE_TO_SCRAPE, SHOW_AS_LIST_PRODUCT_LINE, PRODUCT_LINE, ACTION_BUTTON_CONTAINER, SIGN_IN_NAME, PASSWORD, NEXT_BUTTON, SOLD_OUT_TEXT
import os
import requests
import schedule
import tempfile
from datetime import datetime
import time
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Match:
    fixture: str
    sold_out: bool
    match_link: str

def wait_and_find_element(driver, by, value, timeout=50):
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((by, value))
    )

def determine_if_match_sold_out(child):
    action_buttons = child.find_element(By.CLASS_NAME, ACTION_BUTTON_CONTAINER)
    action_button_text = action_buttons.find_element(By.TAG_NAME, "span").text
    return True if action_button_text == SOLD_OUT_TEXT else False

def login(driver, username, password):
    email_input = wait_and_find_element(driver, By.ID, SIGN_IN_NAME)
    email_input.clear()
    email_input.send_keys(username)

    password_input = wait_and_find_element(driver, By.ID, PASSWORD)
    password_input.clear()
    password_input.send_keys(password)

    button_submit = wait_and_find_element(driver, By.ID, NEXT_BUTTON)
    button_submit.click()
    print("Login succesful!")

def scrape_match_cards(driver):
    print("Scraping match")
    parent_div = wait_and_find_element(driver, By.CLASS_NAME, SHOW_AS_LIST_PRODUCT_LINE)
    child_divs = parent_div.find_elements(By.CLASS_NAME, PRODUCT_LINE)

    match_cards = []
    for index, child in enumerate(child_divs):
        try:
            fixture = child.find_element(By.TAG_NAME, "h3").text
            action_buttons = child.find_element(By.CLASS_NAME, ACTION_BUTTON_CONTAINER)
            try:
                link = action_buttons.find_element(By.TAG_NAME, "a").get_attribute("href")
            except Exception:
                link = None
            
            sold_out_status = determine_if_match_sold_out(child)
            match = Match(fixture=fixture, sold_out=sold_out_status, match_link=link)
            match_cards.append(match)
        except Exception as e:
            print(f"Div {index + 1}: Something went wrong while scraping child div. Error: {e}")
    return match_cards

def call_api_for_available_match(match_list):
    print("calling backend to update matches")
    api_url = "https://goldfish-app-mpxfi.ondigitalocean.app/api/matches"
    payload = {
        "matches": []
    }
    for match in match_list:
        sold_out = False;
       
        home_team, away_team = match.fixture.split(" - ")
        if (away_team == 'AZ'):
            sold_out = True;
        else:
            sold_out = match.sold_out
        matchRequest = {
                "homeTeam": home_team,
                "awayTeam": away_team,
                "soldOut": sold_out,
                "matchLink": match.match_link
            }
        payload['matches'].append(matchRequest)
        
    response = requests.put(api_url, json=payload)
    if response.status_code == 204:
        print(f"Successfully notified for match: {match.fixture}")
    else:
        print(f"Failed to notify for match: {match.fixture}, Status Code: {response.status_code}")

def job():
    user_data_dir = tempfile.mkdtemp()

    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--no-sandbox")  # Optional: for security
    chrome_options.add_argument("--disable-dev-shm-usage")  # Optional: for stability
    chrome_options.add_argument(f"--user-data-dir={user_data_dir}")  # Specify unique user data directory
    chrome_options.add_argument("--remote-debugging-port=9222")  # Add this line to fix DevToolsActivePort issue

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(SITE_TO_SCRAPE)

    username = os.getenv('shopUsername')
    password = os.getenv('shopPassword')

    if not username or not password:
        raise ValueError("Username or password environment variables are not set")

    login(driver, username, password)
    match_cards = scrape_match_cards(driver)
    for matchcard in match_cards:
        print(matchcard)
    call_api_for_available_match(match_cards)

def main():
    while True:
        try:
            job()
            print(f"Job completed succesfully at: {datetime.now()}")
            break
        except Exception as e:
            print(f"Job failed with error: {e}. Retrying in 5 seconds...")
            time.sleep(5)

if __name__ == "__main__":
    main()