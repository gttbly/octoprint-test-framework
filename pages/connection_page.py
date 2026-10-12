from selenium.webdriver.common.by import By

from config.config import Config
from pages.base_page import BasePage


class ConnectionPage(BasePage):
    CONNECT_BUTTON = (By.CSS_SELECTOR, "[data-test-id='connection-connect']")
    STATE = (By.CSS_SELECTOR, "[data-test-id='state-string']")

    def open(self):
        super().open("/#connection")
        self.find(self.CONNECT_BUTTON)
        return self

    def toggle_connection(self):
        button = self.find(self.CONNECT_BUTTON)
        self.driver.execute_script("arguments[0].click();", button)
        return self

    def button_text(self) -> str:
        return self.find(self.CONNECT_BUTTON).get_attribute("textContent").strip()

    def state(self) -> str:
        return self.get_text(self.STATE)

    def is_connected(self) -> bool:
        return self.state() not in {"Offline", "Closed"}

    def wait_for_connected(self, timeout: int = Config.LONG_TIMEOUT):
        self.wait_until(lambda _: self.state() == "Operational", timeout)
        return self

    def wait_for_disconnected(self, timeout: int = Config.LONG_TIMEOUT):
        self.wait_until(lambda _: self.state() in {"Offline", "Closed"}, timeout)
        return self
