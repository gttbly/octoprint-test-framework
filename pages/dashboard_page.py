from selenium.webdriver.common.by import By

from config.config import Config
from pages.base_page import BasePage


class DashboardPage(BasePage):
    STATE = (By.CSS_SELECTOR, "[data-test-id='state-string']")
    SELECTED_FILE = (By.CSS_SELECTOR, "[data-test-id='selected-file-string']")
    PROGRESS = (By.ID, "job_progressBar")
    PAUSE_BUTTON = (By.ID, "job_pause")
    CANCEL_BUTTON = (By.ID, "job_cancel")
    TEMPERATURE_TAB = (By.ID, "temp_link")
    TEMPERATURE_ROWS = (By.CSS_SELECTOR, "#temperature-table tr")
    TERMINAL_TAB = (By.ID, "term_link")
    TERMINAL_COMMAND = (By.ID, "terminal-command")
    TERMINAL_SEND = (By.ID, "terminal-send")
    TERMINAL_OUTPUT = (By.ID, "terminal-output")
    VISIBLE_MODAL = (By.CSS_SELECTOR, ".modal.in")

    def open(self):
        super().open("/")
        self.find(self.STATE)
        return self

    def state(self) -> str:
        return self.get_text(self.STATE)

    def wait_for_state(self, state: str, timeout: int = Config.LONG_TIMEOUT):
        self.wait_until(lambda _: self.state() == state, timeout)
        return self

    def selected_file(self) -> str:
        return self.get_text(self.SELECTED_FILE)

    def progress(self) -> float:
        width = self.find(self.PROGRESS).value_of_css_property("width")
        parent_width = self.find(self.PROGRESS).find_element(By.XPATH, "..").size["width"]
        return 0.0 if not parent_width else float(width.removesuffix("px")) / parent_width * 100

    def pause_or_resume(self):
        self.click(self.PAUSE_BUTTON)
        return self

    def cancel_print(self):
        self.click(self.CANCEL_BUTTON)
        modal = self.find(self.VISIBLE_MODAL)
        modal.find_element(By.CSS_SELECTOR, ".btn-danger").click()
        return self

    def temperature_snapshot(self) -> dict[str, str]:
        self.click(self.TEMPERATURE_TAB)
        rows = self.find_all(self.TEMPERATURE_ROWS)
        result: dict[str, str] = {}
        for row in rows[1:]:
            cells = row.find_elements(By.CSS_SELECTOR, "th, td")
            if len(cells) >= 2 and cells[0].text.strip():
                result[cells[0].text.strip()] = cells[1].text.strip()
        return result

    def send_terminal_command(self, command: str) -> str:
        self.click(self.TERMINAL_TAB)
        self.type_text(self.TERMINAL_COMMAND, command)
        self.click(self.TERMINAL_SEND)
        self.wait_until(
            lambda _: command in self.find(self.TERMINAL_OUTPUT).text,
            Config.LONG_TIMEOUT,
        )
        return self.find(self.TERMINAL_OUTPUT).text
