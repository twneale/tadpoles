import os
import re
import sys
import pdb
import time
import shutil
import pickle
import logging
import logging.config

from random import random
from getpass import getpass

import requests
import lxml.html
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from xvfbwrapper import Xvfb


# -----------------------------------------------------------------------------
# Logging stuff
# -----------------------------------------------------------------------------
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': "%(asctime)s %(levelname)s %(module)s::%(funcName)s: %(message)s",
            'datefmt': '%H:%M:%S'
        }
    },
    'handlers': {
        'app': {'level': 'DEBUG',
                    'class': 'ansistrm.ColorizingStreamHandler',
                    'formatter': 'standard'},
        'default': {'level': 'ERROR',
                    'class': 'ansistrm.ColorizingStreamHandler',
                    'formatter': 'standard'},
    },
    'loggers': {
        'default': {
            'handlers': ['default'], 'level': 'ERROR', 'propagate': False
        },
         'app': {
            'handlers': ['app'], 'level': 'DEBUG', 'propagate': True
        },

    },
}
logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger('app')
info = logger.info
debug = logger.debug
warning = logger.warning
critical = logger.critical


# -----------------------------------------------------------------------------
# The scraper code.
# -----------------------------------------------------------------------------
SLEEP = 1

class Headless:
    def __init__(self):
        # pass
        self.vdisplay = Xvfb()

    def __enter__(self):
        logger.info("Starting xvfb display")
        self.vdisplay.start()
        logger.info("Starting browser")
       # profile = webdriver.FirefoxProfile()
#        profile.set_preference("javascript.enabled", False);
        self.br = self.browser = webdriver.Firefox()
        self.br.implicitly_wait(10)
        return self

    def __exit__(self, *args):
        logger.info("Shutting down browser")
        self.browser.quit()
        logger.info("Shutting down xfvb display")
        self.vdisplay.stop()


def download(hd):
    br = hd.browser

    # Hit the homepage and start a session.
    url = "http://tadpoles.com/"
    info("Fetching %r", url)
    br.get(url)

    # Add cookies.
    try:
        info("Loading cookies")
        with open("cookies.pkl", "rb") as f:
            cookies = pickle.load(f)
    except FileNotFoundError:
        br.find_element_by_id("login-button").click()
        br.find_element_by_class_name("tp-block-half").click()
        br.find_element_by_class_name("other-login-button").click()
        window = set(br.window_handles) - set([br.current_window_handle])
        br.switch_to.window(window.pop())

        email = br.find_element_by_id("Email")
        email.send_keys(input("Enter email: "))
        email.submit()

        passwd = br.find_element_by_id("Passwd")
        passwd.send_keys(getpass("Enter password:"))
        passwd.submit()

        pin = br.find_element_by_id("idvPreregisteredPhonePin")
        pin.send_keys(getpass("Enter google verification code: "))
        pin.submit()

        # Approve.
        time.sleep(2)
        br.find_element_by_id("submit_approve_access").click()

        # Switch back to tadpoles.
        window = set(br.window_handles) - set([br.current_window_handle])
        br.switch_to.window(window.pop())

        # Now load tadpoles cookies.
        with open("cookies.pkl","wb") as f:
            pickle.dump(br.get_cookies(), f)

    else:
        for cookie in cookies:
            if br.current_url.strip('/').endswith(cookie['domain']):
                br.add_cookie(cookie)
        br.get("https://www.tadpoles.com/parents")

    # Cookies in the form reqeusts expects.
    req_cookies = {}
    for s_cookie in cookies:
        req_cookies[s_cookie["name"]] = s_cookie["value"]

    def get_urls(br):
        urls = []
        re_url = re.compile('\("([^"]+)')
        for div in br.find_elements_by_xpath("//li/div"):
            url = re_url.search(div.get_attribute("style"))
            if not url:
                continue
            url = url.group(1)
            url = url.replace('thumbnail=true', '').replace('&thumbnail=true', '')
            url = 'https://www.tadpoles.com' + url
            urls.append(url)
        return urls

    def save_image(url, filename):
        resp = requests.get(url, cookies=req_cookies, stream=True)
        if resp.status_code == 200:
            with open(filename, 'wb') as f:
                for chunk in resp.iter_content(1024):
                    f.write(chunk)
        else:
            raise Exception('Got error %d' % resp.status_code)

    # For each month on the dashboard...
    month_xpath_tmpl = '//*[@id="app"]/div[4]/div[1]/ul/li[%d]/div/div/div/div/span[%d]'
    month_index = 1
    home_url = 'https://www.tadpoles.com/parents'
    MAX_SLEEP = 3
    while True:
        month_xpath = month_xpath_tmpl % (month_index, 1)
        year_xpath = month_xpath_tmpl % (month_index, 2)
        try:
            # Go home if not there already.
            if br.current_url != home_url:
                br.get(home_url)
            # Click the next month.
            month = br.find_element_by_xpath(month_xpath)
            month_name = month.text
            year_name = br.find_element_by_xpath(year_xpath).text
        except NoSuchElementException:
            warning("No months left to scrape. Stopping.")
            sys.exit(0)
        else:
            warning("Starting month #%d" % month_index)
        month.click()

        # ...get the urls...
        time.sleep(2)
        urls = get_urls(br)
        # ...and fetch them one by one.
        while urls:
            url = urls.pop()
            _, key = url.split("key=")
            br.get(url)

            filename_parts = ['img', year_name, month_name, '%s.jpg' % key]
            filename = os.path.abspath(os.path.join(*filename_parts))
            if not os.path.isfile(filename):
                info("Saving: %s" % filename)
                dirname = os.path.dirname(filename)
                if not os.path.isdir(dirname):
                    os.makedirs(dirname)
                save_image(url, filename)
                # br.get_screenshot_as_file(filename)
                time.sleep(random() * MAX_SLEEP)
            else:
                debug("Already downloaded: %s" % filename)

        # Increment the month index.
        month_index += 1


if __name__ == "__main__":
    try:
        with Headless() as hd:
            download(hd)
    except Exception as exc:
        logger.exception(exc)
        import pdb; pdb.set_trace()

