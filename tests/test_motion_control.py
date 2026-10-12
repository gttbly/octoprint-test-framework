import allure
import pytest


@pytest.mark.api
@pytest.mark.motion
@pytest.mark.hardware_control
@allure.feature("打印头运动控制")
class TestMotionControl:
    @allure.story("XYZ 三轴归零")
    def test_home_all_axes(self, api_client, control_guard):
        assert api_client.home(["x", "y", "z"])
        assert api_client.get_printer_state()["state"]["flags"]["operational"]

    @allure.story("相对点动打印头")
    def test_relative_jog(self, api_client, control_guard):
        assert api_client.jog(x=5, y=-5, z=1)
        assert api_client.get_printer_state()["state"]["flags"]["operational"]

    @allure.story("发送安全诊断 G-code")
    def test_send_diagnostic_gcode(self, api_client, control_guard):
        assert api_client.send_gcode(["M105", "M114"])

    @allure.story("拒绝未知运动命令")
    def test_unknown_printhead_command_is_rejected(self, api_client, control_guard):
        response = api_client.request(
            "POST",
            "/api/printer/printhead",
            json={"command": "unsupported-command"},
        )

        assert response.status_code == 400
        assert "invalid" in response.json()["error"].lower()
