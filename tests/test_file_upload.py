from uuid import uuid4

import allure
import pytest


@pytest.mark.files
@allure.feature("G-code 文件管理")
class TestFileManagement:
    @pytest.mark.api
    @allure.story("上传文件并校验元数据")
    def test_upload_and_read_metadata(self, api_client, uploaded_gcode, gcode_file):
        metadata = api_client.get_file(uploaded_gcode)

        assert metadata["name"] == uploaded_gcode
        assert metadata["origin"] == "local"
        assert metadata["type"] == "machinecode"
        assert metadata["size"] == gcode_file.stat().st_size
        assert metadata["refs"]["download"]

    @pytest.mark.api
    @allure.story("文件出现在本地文件列表")
    def test_uploaded_file_is_listed(self, api_client, uploaded_gcode):
        names = {item["name"] for item in api_client.get_files()["files"]}

        assert uploaded_gcode in names

    @pytest.mark.api
    @allure.story("拒绝不受支持的文件类型")
    def test_invalid_file_type_is_rejected(self, api_client, tmp_path):
        invalid_file = tmp_path / f"e2e_invalid_{uuid4().hex[:8]}.exe"
        invalid_file.write_bytes(b"MZ")
        with invalid_file.open("rb") as stream:
            response = api_client.request(
                "POST",
                "/api/files/local",
                files={"file": (invalid_file.name, stream)},
            )

        assert response.status_code == 415
        assert "invalid type" in response.json()["error"]

    @pytest.mark.api
    @allure.story("删除不存在文件返回 404")
    def test_delete_missing_file_returns_not_found(self, api_client):
        response = api_client.request("DELETE", f"/api/files/local/e2e_missing_{uuid4().hex}.gcode")

        assert response.status_code == 404

    @pytest.mark.ui
    @allure.story("Web 控制台完成文件上传与删除")
    def test_upload_and_delete_from_web(self, files_page, api_client, gcode_file):
        page = files_page.open().upload_file(gcode_file)
        try:
            assert page.is_file_present(gcode_file.name)
            page.delete_file(gcode_file.name)
            response = api_client.request("GET", f"/api/files/local/{gcode_file.name}")
            assert response.status_code == 404
        finally:
            response = api_client.request("GET", f"/api/files/local/{gcode_file.name}")
            if response.status_code == 200:
                api_client.delete_file(gcode_file.name)

    @pytest.mark.ui
    @allure.story("Web 控制台提示非法文件上传失败")
    def test_invalid_upload_shows_notification(self, files_page, tmp_path):
        invalid_file = tmp_path / "e2e_invalid.txt"
        invalid_file.write_text("not gcode", encoding="utf-8")

        page = files_page.open().upload_file(invalid_file)

        assert "Upload failed" in page.notification_text()
