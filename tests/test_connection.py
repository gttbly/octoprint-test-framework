import allure
import pytest
import os
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

SKIP_IN_CI = pytest.mark.skipif(
    os.getenv("CI") == "true",
    reason="CI 环境未配置虚拟打印机端口，跳过此测试"
)

@allure.feature("打印机连接")
class TestConnection:

    @pytest.fixture(autouse=True)
    def setup(self, driver):
        driver.get(f"{driver.base_url}/#connection")
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "printer_connect"))
        )
        time.sleep(2)

    @SKIP_IN_CI
    @allure.story("连接虚拟打印机")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_connect_virtual_printer(self, connection_page):
        if connection_page.is_connected():
            connection_page.click_connect_button()
            connection_page.wait_for_disconnected()
            time.sleep(3)
        connection_page.click_connect_button()
        connection_page.wait_for_connected(timeout=30)
        assert connection_page.is_connected() == True

    @SKIP_IN_CI
    @allure.story("断开打印机连接")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_disconnect_printer(self, connection_page):
        if not connection_page.is_connected():
            connection_page.click_connect_button()
            connection_page.wait_for_connected(timeout=30)
            time.sleep(2)
        connection_page.click_connect_button()
        connection_page.wait_for_disconnected(timeout=30)
        assert connection_page.is_connected() == False
