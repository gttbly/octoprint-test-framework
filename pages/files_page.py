from pathlib import Path

from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By

from config.config import Config
from pages.base_page import BasePage


class FilesPage(BasePage):
    FILE_INPUT = (By.ID, "gcode_upload")
    FILE_ENTRIES = (By.CSS_SELECTOR, "[data-test-id='files-list'] .entry.machinecode")
    NOTIFICATION = (By.CSS_SELECTOR, ".ui-pnotify")
    VISIBLE_MODAL = (By.CSS_SELECTOR, ".modal.in")

    def open(self):
        super().open("/#files")
        self.find(self.FILE_INPUT)
        return self

    def upload_file(self, filepath: str | Path):
        self.find(self.FILE_INPUT).send_keys(str(Path(filepath).resolve()))
        return self

    def _entry(self, filename: str):
        def find_entry(_):
            for entry in self.driver.find_elements(*self.FILE_ENTRIES):
                title = entry.find_element(By.CSS_SELECTOR, ".title").text.strip()
                if title == filename:
                    return entry
            return False

        return self.wait_until(find_entry, Config.LONG_TIMEOUT)

    def is_file_present(self, filename: str) -> bool:
        return bool(self._entry(filename))

    def wait_for_file_absent(self, filename: str):
        def absent(_):
            try:
                for entry in self.driver.find_elements(*self.FILE_ENTRIES):
                    if entry.find_element(By.CSS_SELECTOR, ".title").text.strip() == filename:
                        return False
                return True
            except StaleElementReferenceException:
                return False

        self.wait_until(absent, Config.LONG_TIMEOUT)
        return self

    def print_file(self, filename: str):
        self._entry(filename).find_element(By.CSS_SELECTOR, ".btn-files-print").click()
        return self

    def delete_file(self, filename: str):
        self._entry(filename).find_element(By.CSS_SELECTOR, ".btn-files-delete").click()
        modal = self.find(self.VISIBLE_MODAL)
        modal.find_element(By.CSS_SELECTOR, ".btn-danger").click()
        self.wait_for_file_absent(filename)
        return self

    def notification_text(self) -> str:
        return self.get_text(self.NOTIFICATION)
