#!/usr/bin/env python3
"""Repeatedly collect temperature and save it to a file.

Currently, it observes the temperature in Lyon and Saint-Etienne only.
For each city its own file is created (e.g. "Lyon.txt").
To add city, modify the dictionary `WEB_PAGES`.

Observation frequency is controlled by `REPEAT_INTERVAL`.

Attributes
----------
WEB_PAGES : dict
    A key is a city name, and the related value is a link to the
    correspondent MeteoFrance web page.
    The key `main` is ignored for temperature observation, but is used
    for other purposes.
REPEAT_INTERVAL : float
    Start observation every `REPEAT_INTERVAL` seconds.  The first
    observation starts when the local time is multiple of this number.
    Example: if the value is 3600 and the current time is 11:32, the
    first observation will start at about 12:00 (few seconds are spent
    to open a browser and to get the temperature's value).
TIMEOUT : float
    Timeout for a web-page element waiting.
DATE_TIME_FORMAT : str
    Time format, same as for `datetime.datetime.strftime`.

"""
import time
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
REPEAT_INTERVAL = 60
TIMEOUT = 10
DATE_TIME_FORMAT = "%d-%m-%y %H:%M:%S"


def click(driver, element):
    driver.execute_script("arguments[0].click();", element)


def get_and_save_temperature(driver, city):
    temp_xpath = '//*[@id="atmogramme_slider"]/div/ul/li[1]/div/strong'
    waiter = WebDriverWait(driver, TIMEOUT)
    with closing_window(driver, WEB_PAGES[city]):
        temp_el = waiter.until(
            EC.presence_of_element_located((By.XPATH, temp_xpath)))
        temperature = temp_el.text
        logger.info(f'{city} temperature: {temperature}')
        output_fname = f'{city}.txt'
        with open(output_fname, 'a') as output:
            date = datetime.datetime.now()
            measure_time = date.strftime(DATE_TIME_FORMAT)
            output.write(f'{measure_time} | {temperature}\n')
    return temperature


def do_observation(driver):
    # Manage cookies.
    driver.get(WEB_PAGES['main'])
    cookies_btn_xpath = '//*[@id="didomi-notice-agree-button"]'
    try:
        cookies_btn = WebDriverWait(driver, TIMEOUT).until(
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


def main():
    ri = REPEAT_INTERVAL
    while True:
        time.sleep(ri - time.time() % ri)
        driver = create_browser(headless=True, browser_type="chrome")
        try:
            do_observation(driver)
        finally:
            driver.quit()


if __name__ == '__main__':
    main()
