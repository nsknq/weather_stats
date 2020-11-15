#!/usr/bin/env python3
"""Collect current temperature and save it to file.

Currently, it observes the temperature in Lyon and Saint-Etienne only.
For each city its own file is created (e.g. "Lyon.txt").
To add city, modify the dictionary `WEB_PAGES` with a city name as a key
and the link to correspondent MeteoFrance web page as a value.
The key `main` is ignored for temperature observation, but is used for
other purposes.

"""
import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from browser import create_browser, closing_window
import logging
from misc import prepare_logging
logger = prepare_logging(__name__, level=logging.INFO)


WEB_PAGES = {
    'main': 'https://meteofrance.com',
    'Saint-Etienne': 'https://meteofrance.com/previsions-meteo-france/saint-etienne/42000',
    'Lyon': 'https://meteofrance.com/previsions-meteo-france/lyon/69000',
}
# Timeout for a web-page element waiting.
TIME_OUT = 10


def click(driver, element):
    driver.execute_script("arguments[0].click();", element)


def get_and_save_temperature(driver, city):
    temp_xpath = '//*[@id="atmogramme_slider"]/div/ul/li[1]/div/strong'
    waiter = WebDriverWait(driver, TIME_OUT)
    with closing_window(driver, WEB_PAGES[city]):
        temp_el = waiter.until(
            EC.presence_of_element_located((By.XPATH, temp_xpath)))
        temperature = temp_el.text
        logger.info(f'{city} temperature: {temperature}')
        output_fname = f'{city}.txt'
        with open(output_fname, 'a') as output:
            date = datetime.datetime.now()
            measure_time = date.strftime("%d-%m-%y %H:%M")
            output.write(f'{measure_time} | {temperature}\n')
    return temperature


def main():
    driver = create_browser(headless=True, browser_type="chrome")
    waiter = WebDriverWait(driver, TIME_OUT)
    driver.get(WEB_PAGES['main'])

    # Manage cookies.
    cookies_btn_xpath = '//*[@id="didomi-notice-agree-button"]'
    try:
        cookies_btn = waiter.until(
            EC.element_to_be_clickable((By.XPATH, cookies_btn_xpath)))
    except TimeoutException as te:
        logger.debug('Cookies had already been accepted.')
    else:
        click(driver, cookies_btn)
        logger.debug('Cookies have been accepted.')
    logger.debug('Cookies have been managed.')

    # Collect temperature.
    for city in WEB_PAGES:
        if city != 'main':
            get_and_save_temperature(driver, city)


if __name__ == '__main__':
    main()
