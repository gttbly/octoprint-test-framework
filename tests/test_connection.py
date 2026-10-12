import allure
import pytest


@pytest.mark.connection
@allure.feature("打印机连接管理")
class TestConnection:
    @pytest.mark.api
    @allure.story("查询串口、波特率和打印机配置")
    def test_connection_options_are_available(self, api_client):
        connection = api_client.get_connection()

        assert set(connection) == {"current", "options"}
        assert connection["options"]["ports"]
        assert connection["options"]["baudrates"]
        assert connection["options"]["printerProfiles"]

    @pytest.mark.api
    @pytest.mark.virtual_printer
    @allure.story("断线后重新连接虚拟打印机")
    def test_disconnect_and_reconnect(self, api_client, virtual_printer):
        api_client.disconnect_printer()
        assert api_client.wait_for_connection_state({"Closed", "Offline"}) in {"Closed", "Offline"}

        api_client.connect_printer(port="VIRTUAL", baudrate=250000)
        assert api_client.wait_for_connection_state({"Operational"}) == "Operational"

    @pytest.mark.ui
    @pytest.mark.virtual_printer
    @allure.story("Web 控制台断开并恢复打印机连接")
    def test_connection_can_be_toggled_from_web(self, connection_page, virtual_printer):
        page = connection_page.open()
        try:
            if page.is_connected():
                page.toggle_connection().wait_for_disconnected()
            assert not page.is_connected()

            page.toggle_connection().wait_for_connected()
            assert page.state() == "Operational"
        finally:
            if not page.is_connected():
                page.toggle_connection().wait_for_connected()
