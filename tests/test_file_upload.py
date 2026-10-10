import allure
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pages.files_page import FilesPage
import os
import pytest

# CI 环境跳过依赖虚拟打印机环境配置的用例
SKIP_IN_CI = pytest.mark.skipif(
    os.getenv("CI") == "true",
    reason="CI 环境未配置虚拟打印机端口，跳过此测试"
)

class TestConnection:
    @SKIP_IN_CI
    @allure.story("连接虚拟打印机")
    

@allure.feature("文件管理")
class TestFileUpload:

    @pytest.fixture(autouse=True)
    def setup(self, driver):
        driver.get(f"{driver.base_url}/#files")
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']"))
        )

    @allure.story("上传 G-code 文件")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_upload_gcode_file(self, driver, tmp_path):
        # 用 tmp_path 临时生成一个 G-code 测试文件
        gcode_file = tmp_path / "test_print.gcode"
        gcode_file.write_text("G28 ; Home\nG1 X10 Y10 Z10\nM104 S200\n")

        page = FilesPage(driver)
        page.upload_file(str(gcode_file))

        assert page.is_file_present("test_print.gcode") == True
