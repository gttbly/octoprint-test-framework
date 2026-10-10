from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from config.config import Config
import time

options = Options()
options.add_argument("--window-size=1920,1080")
driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)
driver.implicitly_wait(5)

# 自动登录
driver.get(Config.BASE_URL)
if "login" in driver.current_url:
    driver.find_element(By.ID, "login-user").send_keys(Config.USERNAME)
    driver.find_element(By.ID, "login-password").send_keys(Config.PASSWORD)
    driver.find_element(By.ID, "login-button").click()
    WebDriverWait(driver, 10).until(lambda d: "login" not in d.current_url)
    print("登录成功")

# 打开连接页面
driver.get(f"{Config.BASE_URL}/#connection")
time.sleep(5)

print("当前 URL:", driver.current_url)
print("页面标题:", driver.title)

btn = driver.find_element(By.ID, "printer_connect")
print("\n=== 按钮状态 ===")
print("  text:", repr(btn.text))
print("  is_displayed:", btn.is_displayed())
print("  is_enabled:", btn.is_enabled())
print("  class:", btn.get_attribute("class"))
print("  disabled属性:", btn.get_attribute("disabled"))
print("  outerHTML:", btn.get_attribute("outerHTML")[:300])

# 截图
driver.save_screenshot("connection_page.png")
print("\n截图已保存 connection_page.png")

input("回车关闭...")
driver.quit()
