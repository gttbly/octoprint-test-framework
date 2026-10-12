from collections.abc import Callable
from typing import Any

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config.config import Config


class BasePage:
    def __init__(self, driver, timeout: int = Config.TIMEOUT):
        self.driver = driver
        self.timeout = timeout
        self.wait = WebDriverWait(driver, timeout)

    def open(self, path: str = ""):
        self.driver.get(f"{self.driver.base_url}{path}")
        return self

    def find(self, locator):
        return self.wait.until(EC.presence_of_element_located(locator))

    def find_all(self, locator):
        return self.wait.until(EC.presence_of_all_elements_located(locator))

    def click(self, locator):
        self.wait.until(EC.element_to_be_clickable(locator)).click()
        return self

    def type_text(self, locator, text: str, *, clear: bool = True):
        element = self.wait.until(EC.visibility_of_element_located(locator))
        if clear:
            element.clear()
        element.send_keys(text)
        return self

    def get_text(self, locator) -> str:
        return self.wait.until(EC.visibility_of_element_located(locator)).text.strip()

    def wait_for_text(self, locator, text: str, timeout: int | None = None) -> bool:
        return WebDriverWait(self.driver, timeout or self.timeout).until(
            EC.text_to_be_present_in_element(locator, text)
        )

    def wait_until(self, condition: Callable[[Any], Any], timeout: int | None = None):
        return WebDriverWait(self.driver, timeout or self.timeout).until(condition)

    def is_visible(self, locator, timeout: int = 2) -> bool:
        try:
            return (
                WebDriverWait(self.driver, timeout)
                .until(EC.visibility_of_element_located(locator))
                .is_displayed()
            )
        except TimeoutException:
            return False
