from selenium.webdriver.common.by import By
from pages.base_page import BasePage

class LoginPage(BasePage):
    # 注意：这里的定位器（By.ID）需要根据 OctoPrint 实际页面的元素修改
    # 目前作为框架演示，先用占位符
    USERNAME_INPUT = (By.ID, "login_username")
    PASSWORD_INPUT = (By.ID, "login_password")
    LOGIN_BUTTON = (By.CSS_SELECTOR, "button[type='submit']")
    ERROR_MSG = (By.CSS_SELECTOR, ".alert-error")

    def open(self):
        self.driver.get(f"{self.driver.base_url}/login")
        return self

    def login(self, username, password):
        self.type_text(self.USERNAME_INPUT, username)
        self.type_text(self.PASSWORD_INPUT, password)
        self.click(self.LOGIN_BUTTON)
        return self

    def get_error_message(self):
        return self.get_text(self.ERROR_MSG)
