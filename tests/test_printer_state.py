import allure
import pytest


@pytest.mark.temperature
@allure.feature("温度监控与控制")
class TestTemperatureControl:
    @pytest.mark.api
    @allure.story("温度传感器读数结构与范围")
    def test_temperature_sensor_contract(self, api_client, connected_printer):
        printer = api_client.get_printer_state()

        for component in ("tool0", "bed"):
            reading = printer["temperature"][component]
            assert set(reading) >= {"actual", "target", "offset"}
            assert isinstance(reading["actual"], (int, float))
            assert -20 <= reading["actual"] <= 500

    @pytest.mark.api
    @pytest.mark.hardware_control
    @allure.story("设置喷头温度并等待稳定")
    def test_tool_heating_and_cooldown(self, api_client, control_guard):
        api_client.set_tool_target(60)
        target = api_client.wait_for_temperature_target("tool0", 60)
        assert target["target"] == 60

        stable = api_client.wait_for_temperature("tool0", 60, tolerance=2)
        assert abs(stable["actual"] - 60) <= 2

        api_client.set_tool_target(0)
        assert api_client.wait_for_temperature_target("tool0", 0)["target"] == 0

    @pytest.mark.api
    @pytest.mark.hardware_control
    @allure.story("设置热床温度并等待稳定")
    def test_bed_heating_and_cooldown(self, api_client, control_guard):
        api_client.set_bed_target(40)
        target = api_client.wait_for_temperature_target("bed", 40)
        assert target["target"] == 40

        stable = api_client.wait_for_temperature("bed", 40, tolerance=2)
        assert abs(stable["actual"] - 40) <= 2

        api_client.set_bed_target(0)
        assert api_client.wait_for_temperature_target("bed", 0)["target"] == 0

    @pytest.mark.ui
    @allure.story("Web 控制台显示喷头与热床温度")
    def test_temperature_is_visible_on_dashboard(self, dashboard_page, connected_printer):
        snapshot = dashboard_page.open().temperature_snapshot()

        assert "Tool" in snapshot
        assert "Bed" in snapshot
        assert "°C" in snapshot["Tool"]
        assert "°C" in snapshot["Bed"]

    @pytest.mark.ui
    @pytest.mark.hardware_control
    @allure.story("终端下发诊断 G-code 并收到回显")
    def test_diagnostic_gcode_from_terminal(self, dashboard_page, control_guard):
        command = "M117 e2e-terminal-check"

        output = dashboard_page.open().send_terminal_command(command)

        assert "e2e-terminal-check" in output
        assert "Recv: ok" in output
