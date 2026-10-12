import allure
import pytest


@pytest.mark.api
@pytest.mark.regression
@allure.feature("OctoPrint REST API")
class TestPlatformAPI:
    @allure.story("版本契约")
    def test_version_contract(self, api_client):
        info = api_client.get_version()

        assert info["api"] == "0.1"
        assert info["server"]
        assert info["text"].startswith("OctoPrint")

    @allure.story("服务器状态契约")
    def test_server_status_contract(self, api_client):
        status = api_client.get_server_status()

        assert set(status) >= {"version", "safemode"}
        assert isinstance(status["version"], str)

    @allure.story("打印机状态契约")
    def test_printer_state_contract(self, api_client, connected_printer):
        printer = api_client.get_printer_state()

        assert set(printer) >= {"state", "temperature"}
        assert set(printer["state"]) >= {"text", "flags"}
        assert isinstance(printer["state"]["flags"]["operational"], bool)

    @allure.story("任务状态契约")
    def test_job_status_contract(self, api_client):
        job = api_client.get_job()

        assert set(job) >= {"job", "progress", "state"}
        assert set(job["progress"]) >= {"completion", "printTime", "printTimeLeft"}

    @allure.story("打印机配置包含物理能力")
    def test_printer_profile_contract(self, api_client):
        result = api_client.get_printer_profiles()

        assert result["profiles"]
        for profile in result["profiles"].values():
            assert set(profile) >= {"axes", "volume", "extruder"}
