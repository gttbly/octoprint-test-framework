import allure
import pytest


@pytest.mark.api
@pytest.mark.smoke
@allure.feature("平台健康检查")
def test_octoprint_service_is_healthy(api_client):
    version = api_client.get_version()
    server = api_client.get_server_status()

    assert version["server"]
    assert server["version"] == version["server"]


@pytest.mark.ui
@pytest.mark.smoke
@allure.feature("平台健康检查")
def test_authenticated_dashboard_is_available(dashboard_page, connected_printer):
    dashboard_page.open()

    assert dashboard_page.driver.title == "OctoPrint"
    assert dashboard_page.state() in {"Operational", "Printing", "Paused"}
