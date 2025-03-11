from dataclasses import dataclass
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selectors_list import SITE_TO_SCRAPE, SHOW_AS_LIST_PRODUCT_LINE, PRODUCT_LINE, ACTION_BUTTON_CONTAINER, SIGN_IN_NAME, PASSWORD, NEXT_BUTTON, SOLD_OUT_TEXT
import os
from dotenv import load_dotenv

load_dotenv()

@dataclass
class MatchCard:
    fixture: str
    sold_out: bool

def wait_and_find_element(driver, by, value, timeout=10):
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((by, value))
    )

def login(driver, username, password):
    email_input = wait_and_find_element(driver, By.ID, SIGN_IN_NAME)
    email_input.clear()
    email_input.send_keys(username)

    password_input = wait_and_find_element(driver, By.ID, PASSWORD)
    password_input.clear()
    password_input.send_keys(password)

    button_submit = wait_and_find_element(driver, By.ID, NEXT_BUTTON)
    button_submit.click()

def scrape_match_cards(driver):
    parent_div = wait_and_find_element(driver, By.CLASS_NAME, SHOW_AS_LIST_PRODUCT_LINE)
    child_divs = parent_div.find_elements(By.CLASS_NAME, PRODUCT_LINE)

    match_cards = []
    for index, child in enumerate(child_divs):
        try:
            fixture = child.find_element(By.TAG_NAME, "h3").text
            action_buttons = child.find_element(By.CLASS_NAME, ACTION_BUTTON_CONTAINER)
            action_button_text = action_buttons.find_element(By.TAG_NAME, "span").text
            sold_out_status = True if action_button_text == SOLD_OUT_TEXT else False
            matchcard = MatchCard(fixture=fixture, sold_out=sold_out_status)
            match_cards.append(matchcard)
        except Exception as e:
            print(f"Div {index + 1}: Something went wrong while scraping child div. Error: {e}")
    return match_cards

def main():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
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

if __name__ == "__main__":
    main()