import logging

from selenium import webdriver
from selenium.webdriver import Remote
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities



class Firefox:

    def __init__(self, pytest_request):
        self.init_logging()
        self._pytest_request = pytest_request

    def init_logging(self):
        logger = logging.getLogger('firefox')
        self.info = logger.info
        self.debug = logger.debug
        self.warning = logger.warning
        self.critical = logger.critical
        self.exception = logger.exception

    def __enter__(self):
        self.debug('Starting browser')
        self.br = self.browser = self.get_firefox()
        self.br.implicitly_wait(10)
        return self

    def __exit__(self, *args):
        self.debug('Shutting down browser')
        self.browser.quit()

    def get_firefox(self):
        if os.environ.get('DOCKERIZED_FIREFOX') is not None:
            return webdriver.Firefox()
        else:
            return Remote(
              command_executor='http://firefox:4444/wd/hub',
              desired_capabilities=DesiredCapabilities.FIREFOX
            )

