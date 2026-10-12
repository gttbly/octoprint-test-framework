import os
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from config.config import Config


def pytest_addoption(parser):
    parser.addoption("--headless", action="store_true", default=False)


@pytest.fixture(scope="session")
def driver(request):
    options = Options()
    if Config.HEADLESS or request.config.getoption("--headless"):
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")

    # 直接用本地已有的 ChromeDriver，不联网检查版本
    local_driver = "/usr/local/bin/chromedriver"
    if os.path.exists(local_driver):
        service = Service(local_driver)
    else:
        # 兜底：如果本地没有，才用 webdriver-manager
        from webdriver_manager.chrome import ChromeDriverManager
        service = Service(ChromeDriverManager().install())

    driver = webdriver.Chrome(service=service, options=options)
    driver.base_url = Config.BASE_URL
    driver.implicitly_wait(5)

    # 自动登录
    driver.get(driver.base_url)
    if "login" in driver.current_url:
        print("\n检测到需要登录，正在自动登录...")
        driver.find_element(By.ID, "login-user").send_keys(Config.USERNAME)
        driver.find_element(By.ID, "login-password").send_keys(Config.PASSWORD)
        driver.find_element(By.ID, "login-button").click()
        WebDriverWait(driver, 10).until(lambda d: "login" not in d.current_url)
        print("✅ 登录成功！")

    yield driver
    driver.quit()


@pytest.fixture
def login_page(driver):
    from pages.login_page import LoginPage
    return LoginPage(driver)


@pytest.fixture
def connection_page(driver):
    from pages.connection_page import ConnectionPage
    return ConnectionPage(driver)
