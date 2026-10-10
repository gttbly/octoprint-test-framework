from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from pages.base_page import BasePage


class FilesPage(BasePage):
    FILE_INPUT = (By.CSS_SELECTOR, "input[type='file']")

    def upload_file(self, filepath):
        """上传文件（Selenium 可以直接对隐藏的 input 文件框 send_keys）"""
        file_input = self.wait.until(
            lambda d: d.find_element(*self.FILE_INPUT)
        )
        file_input.send_keys(filepath)
        return self

    def is_file_present(self, filename):
        """检查文件名是否出现在页面中"""
        try:
            WebDriverWait(self.driver, 15).until(
                lambda d: filename in d.page_source
            )
            return True
        except Exception:
            return False
