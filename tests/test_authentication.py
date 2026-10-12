import allure
import pytest

from config.config import Config


@pytest.mark.api
@pytest.mark.auth
@allure.feature("认证与授权")
class TestAPIAuthentication:
    @allure.story("未携带 API Key 的请求被拒绝")
    def test_missing_api_key_is_rejected(self, unauthenticated_api):
        response = unauthenticated_api.request("GET", "/api/printer")

        assert response.status_code == 403

    @allure.story("无效 API Key 的请求被拒绝")
    def test_invalid_api_key_is_rejected(self, invalid_key_api):
        response = invalid_key_api.request("GET", "/api/printer")

        assert response.status_code == 403

    @allure.story("自动化账号具有业务所需权限")
    def test_automation_identity_has_required_permissions(self, api_client):
        user = api_client.get_current_user()
        required = {"STATUS", "CONNECTION", "FILES_LIST", "FILES_UPLOAD", "CONTROL", "PRINT"}

        assert user["name"]
        assert required.issubset(set(user["permissions"]))


@pytest.mark.ui
@pytest.mark.auth
@allure.feature("认证与授权")
class TestWebAuthentication:
    @allure.story("错误密码显示明确提示")
    def test_invalid_credentials_show_error(self, login_page):
        login_page.open().login("invalid-user", "invalid-password", wait_for_success=False)

        assert "Incorrect username or password" in login_page.error_message()

    @allure.story("管理员登录并安全退出")
    def test_login_and_logout(self, login_page):
        login_page.open().login(Config.USERNAME, Config.PASSWORD)

        assert login_page.logged_in_username() == Config.USERNAME
        login_page.logout()
        assert "/login" in login_page.driver.current_url
