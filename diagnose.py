from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from config.config import Config

options = Options()
options.add_argument("--window-size=1920,1080")
# 先用可见模式（不加 --headless），方便肉眼观察
driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)
driver.implicitly_wait(5)

print("=== 正在访问:", Config.BASE_URL)
driver.get(Config.BASE_URL)

import time
time.sleep(5)  # 等页面加载

print("=== 当前 URL:", driver.current_url)
print("=== 页面标题:", driver.title)

# 保存截图
driver.save_screenshot("diagnose_page.png")
print("=== 截图已保存为 diagnose_page.png")

# 尝试查找连接按钮
from selenium.webdriver.common.by import By
try:
    btn = driver.find_element(By.ID, "printer_connect")
    print("=== ✅ 找到连接按钮，文字是:", btn.text)
except Exception as e:
    print("=== ❌ 找不到连接按钮，原因:", e)

input("按回车键关闭浏览器...")
driver.quit()
