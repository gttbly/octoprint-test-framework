import allure
import pytest
import time
from utils.api_client import OctoPrintAPI


@allure.feature("打印机状态监控")
class TestPrinterState:

    @pytest.fixture(autouse=True)
    def setup(self):
        """每个测试前，确保虚拟打印机已连接"""
        api = OctoPrintAPI()
        api.connect_printer()
        time.sleep(3)  # 等待连接建立
        yield

    @allure.story("读取打印头温度")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_read_tool_temperature(self):
        api = OctoPrintAPI()
        tool = api.get_tool_temperatures()
        assert "actual" in tool
        assert isinstance(tool["actual"], (int, float))

    @allure.story("读取热床温度")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_read_bed_temperature(self):
        api = OctoPrintAPI()
        bed = api.get_bed_temperature()
        assert "actual" in bed

    @allure.story("发送 G-code 控制指令")
    @allure.severity(allure.severity_level.NORMAL)
    def test_send_gcode_command(self):
        api = OctoPrintAPI()
        api.send_gcode(["G91", "G1 E5 F300", "G90"])

    @allure.story("查询耗材剩余量")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_filament_usage(self):
        api = OctoPrintAPI()
        state = api.get_printer_state()
        assert "temperature" in state
        filament = api.get_filament_usage()
        if filament is not None:
            assert isinstance(filament, (list, dict))
