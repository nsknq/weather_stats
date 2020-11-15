import os
import time
from contextlib import contextmanager
from typing import Sequence
from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from misc import prepare_logging
logger = prepare_logging(__name__)


# Folder to store downloaded files.
DOWNLOAD_PATH = '~/Downloads'


# Type for hints.
TypeWindowHandler = str


# TODO: rename `download_path` to `downloads_path`.
def create_browser(
        headless=False, browser_type="chrome", download_path=DOWNLOAD_PATH):
    """Create selenium driver.

    For Firefox:
        - save without confirmation for .pdf, .docx (msword).

    Returns
    -------
    driver : webdriver.Remote

    """
    assert isinstance(headless, bool)
    if browser_type == "chrome":
        options = webdriver.ChromeOptions()
        # TODO: make headless mode work (problem with chrome://downloads DOM).
        if headless:
            options.add_argument('headless')
            options.add_argument('start-maximized')
            options.add_argument("--window-size=800,600")
        options.add_experimental_option(
            'prefs', {'download.default_directory': download_path})
        driver = webdriver.Chrome(options=options)
    elif browser_type == "firefox":
        options = webdriver.firefox.options.Options()
        options.headless = headless
        profile = webdriver.FirefoxProfile()
        profile.set_preference("browser.download.folderList", 2)
        profile.set_preference("browser.download.manager.showWhenStarting", False)
        profile.set_preference("browser.download.dir", download_path)
        # No prompting on saving for the following MIME types.
        profile.set_preference(
            'browser.helperApps.neverAsk.saveToDisk',
            'application/octet-stream'
            ';application/msword'
            ';application/pdf'
            ';video/x-ms-wmv;video/x-ms-asf'
        )
        # disable Firefox's built-in PDF viewer
        profile.set_preference("pdfjs.disabled", True)
        driver = webdriver.Firefox(firefox_profile=profile, options=options)
    else:
        raise ValueError('Wrong browser choice')
    return driver


def open_inner_page(driver, link=None, new_window=True):
    """Open inner link.

    Internal pages (like "about", "config", "downloads") cannot be open
    in a script-like.  So we need to open an empty link and then load
    the required inner page.

    Parameters
    ----------
    driver : webdriver.Remote
    link : str
        Link to a inner web page.
    new_window : bool
        Flag whether to open a new tab.  If `False` the current tab must
        be ready to use.

    Returns
    -------
    window_handler : TypeWindowHandler
        The handler of the used tab.
    """
    if new_window:
        # Open new window.
        driver.execute_script('window.open("","_blank");')
        # Before using this window, the handle is strange
        # (like "2147483649").
        # Set focus on the new tab.
        driver.switch_to.window(driver.window_handles[-1])
    if link is not None:
        # If the `new_window` is `True`, the current_window_handle
        # magically changes to a normal one.
        driver.get(link)
    return driver.current_window_handle


@contextmanager
def closing_window(driver, link):
    """Context manager for opening a web page.

    Parameters
    ----------
    driver : webdriver.Chrome
        Used browser.
    link : str
        Link to the web page.
    """
    initial_window = driver.current_window_handle
    open_window_handle = open_inner_page(driver, link, new_window=True)
    try:
        yield open_window_handle
    finally:
        driver.switch_to.window(open_window_handle)
        driver.close()
        driver.switch_to.window(initial_window)


if __name__ == '__main__':
    print('Nothing to do here')
