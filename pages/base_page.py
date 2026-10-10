from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class BasePage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10) # 统一显式等待10秒

    def find(self, locator):
        """等待元素出现并返回"""
        return self.wait.until(EC.presence_of_element_located(locator))

    def click(self, locator):
        """等待元素可点击后点击"""
        self.wait.until(EC.element_to_be_clickable(locator)).click()

    def type_text(self, locator, text):
        """清空输入框并输入文本"""
        el = self.find(locator)
        el.clear()
        el.send_keys(text)

    def get_text(self, locator):
        """获取元素文本"""
        return self.find(locator).text

    def is_visible(self, locator):
        """判断元素是否可见，通常用于断言"""
        try:
            return self.wait.until(EC.visibility_of_element_located(locator)).is_displayed()
        except Exception:
            return False
