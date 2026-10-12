from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class LoginPage(BasePage):
    USERNAME_INPUT = (By.CSS_SELECTOR, "[data-test-id='login-username']")
    PASSWORD_INPUT = (By.CSS_SELECTOR, "[data-test-id='login-password']")
    LOGIN_BUTTON = (By.CSS_SELECTOR, "[data-test-id='login-submit']")
    CREDENTIAL_ERROR = (By.ID, "login-error-credentials")
    LOGIN_MENU = (By.CSS_SELECTOR, "[data-test-id='login-menu']")
    LOGIN_MENU_TITLE = (By.CSS_SELECTOR, "[data-test-id='login-menu-title']")
    LOGOUT_BUTTON = (By.CSS_SELECTOR, "[data-test-id='logout-submit']")

    def open(self):
        super().open("/")
        self.find(self.USERNAME_INPUT)
        return self

    def login(self, username: str, password: str, *, wait_for_success: bool = True):
        self.type_text(self.USERNAME_INPUT, username)
        self.type_text(self.PASSWORD_INPUT, password)
        self.click(self.LOGIN_BUTTON)
        if wait_for_success:
            self.wait_until(lambda driver: "/login" not in driver.current_url)
            self.find(self.LOGIN_MENU_TITLE)
        return self

    def error_message(self) -> str:
        return self.get_text(self.CREDENTIAL_ERROR)

    def logged_in_username(self) -> str:
        return self.get_text(self.LOGIN_MENU_TITLE)

    def logout(self):
        self.click(self.LOGIN_MENU)
        self.click(self.LOGOUT_BUTTON)
        self.wait_until(lambda driver: "/login" in driver.current_url)
        return self
