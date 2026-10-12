import os
import allure
import pytest
import time
from utils.api_client import OctoPrintAPI


SKIP_IN_CI = pytest.mark.skipif(
    os.getenv("CI") == "true",
    reason="CI 环境 API 认证配置不同，此测试需在本地运行"
)


@allure.feature("OctoPrint REST API")
class TestOctoPrintAPI:

    @pytest.fixture(autouse=True)
    def setup(self):
        api = OctoPrintAPI()
        api.connect_printer()
        time.sleep(3)
        yield

    @SKIP_IN_CI
    @allure.story("获取 OctoPrint 版本信息")
    @allure.severity(allure.severity_level.MINOR)
    def test_get_version(self):
        api = OctoPrintAPI()
        info = api.get_version()
        assert "server" in info or "api" in info

    @SKIP_IN_CI
    @allure.story("读取打印头温度")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_read_tool_temperature(self):
        api = OctoPrintAPI()
        tool = api.get_tool_temperatures()
        assert "actual" in tool
        assert isinstance(tool["actual"], (int, float))

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
        result = api.send_gcode(["G91", "G1 E5 F300", "G90"])
        assert result is True

    @SKIP_IN_CI
    @allure.story("获取本地文件列表")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_file_list(self):
        api = OctoPrintAPI()
        result = api.get_files()
        assert "files" in result
        assert isinstance(result["files"], list)

    @SKIP_IN_CI
    @allure.story("上传 G-code 文件并通过 API 验证")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_upload_and_delete_file(self, tmp_path):
        api = OctoPrintAPI()
        test_file = tmp_path / "api_test.gcode"
        test_file.write_text("G28\nG1 X10 Y10\n")
        upload_result = api.upload_file(str(test_file))
        assert upload_result.get("done") is True
        files = api.get_files()["files"]
        filenames = [f["name"] for f in files]
        assert "api_test.gcode" in filenames
        api.delete_file("api_test.gcode")

    @SKIP_IN_CI
    @allure.story("查询当前任务状态")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_job_status(self):
        api = OctoPrintAPI()
        job = api.get_job()
        assert "state" in job
        assert "job" in job
