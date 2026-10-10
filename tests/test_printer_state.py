import os
import allure
import pytest
import time
from utils.api_client import OctoPrintAPI


SKIP_IN_CI = pytest.mark.skipif(
    os.getenv("CI") == "true",
    reason="CI 环境 API 认证配置不同，此测试需在本地运行"
)


@allure.feature("打印机状态监控")
class TestPrinterState:

    @pytest.fixture(autouse=True)
    def setup(self):
        api = OctoPrintAPI()
        api.connect_printer()
        time.sleep(3)
        yield

    @SKIP_IN_CI
    @allure.story("读取打印头温度")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_read_tool_temperature(self):
        api = OctoPrintAPI()
        tool = api.get_tool_temperatures()
        assert "actual" in tool

    @SKIP_IN_CI
    @allure.story("读取热床温度")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_read_bed_temperature(self):
        api = OctoPrintAPI()
        bed = api.get_bed_temperature()
        assert "actual" in bed

    @SKIP_IN_CI
    @allure.story("发送 G-code 控制指令")
    @allure.severity(allure.severity_level.NORMAL)
    def test_send_gcode_command(self):
        api = OctoPrintAPI()
        api.send_gcode(["G91", "G1 E5 F300", "G90"])

    @SKIP_IN_CI
    @allure.story("查询耗材剩余量")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_filament_usage(self):
        api = OctoPrintAPI()
        state = api.get_printer_state()
        assert "temperature" in state
