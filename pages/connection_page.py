from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from pages.base_page import BasePage


class ConnectionPage(BasePage):
    CONNECT_BUTTON = (By.ID, "printer_connect")

    def click_connect_button(self):
        btn = self.wait.until(lambda d: d.find_element(*self.CONNECT_BUTTON))
        self.driver.execute_script("arguments[0].click();", btn)
        return self

    def get_button_text(self):
        btn = self.wait.until(lambda d: d.find_element(*self.CONNECT_BUTTON))
        return btn.get_attribute("textContent").strip()

    def is_connected(self):
        return "Disconnect" in self.get_button_text()

    def wait_for_connected(self, timeout=30):
        WebDriverWait(self.driver, timeout).until(
            lambda d: "Disconnect" in d.find_element(By.ID, "printer_connect").get_attribute("textContent")
        )

    def wait_for_disconnected(self, timeout=30):
        # 关键：必须是 "Disconnect" not in，否则 "Connect" 会被误判
        WebDriverWait(self.driver, timeout).until(
            lambda d: "Disconnect" not in d.find_element(By.ID, "printer_connect").get_attribute("textContent")
        )
