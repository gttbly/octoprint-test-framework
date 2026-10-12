import allure
import pytest


@pytest.mark.job
@pytest.mark.virtual_printer
@allure.feature("打印任务状态机")
class TestPrintJobLifecycle:
    @pytest.mark.api
    @allure.story("选中文件但不自动打印")
    def test_uploaded_job_is_selected(self, api_client, uploaded_print_job):
        job = api_client.get_job()

        assert job["job"]["file"]["name"] == uploaded_print_job
        assert job["state"] == "Operational"

    @pytest.mark.api
    @allure.story("打印任务启动、暂停、恢复并取消")
    def test_start_pause_resume_cancel(self, api_client, uploaded_print_job):
        api_client.start_job()
        printing = api_client.wait_for_job_state({"Printing"})
        assert printing["job"]["file"]["name"] == uploaded_print_job

        api_client.pause_job()
        assert api_client.wait_for_job_state({"Paused"})["state"] == "Paused"

        api_client.resume_job()
        assert api_client.wait_for_job_state({"Printing"})["state"] == "Printing"

        api_client.cancel_job()
        assert api_client.wait_for_job_state({"Operational"})["state"] == "Operational"

    @pytest.mark.api
    @allure.story("打印过程中进度持续更新")
    def test_print_progress_is_reported(self, api_client, uploaded_print_job):
        api_client.start_job()
        job = api_client.wait_for_job_state({"Printing"})

        assert job["progress"]["completion"] is not None
        assert 0 <= job["progress"]["completion"] <= 100
        assert job["progress"]["printTime"] is not None

        api_client.cancel_job()
        api_client.wait_for_job_state({"Operational"})

    @pytest.mark.api
    @allure.story("打印过程中阻止运动和删除在用文件")
    def test_busy_printer_safety_interlocks(self, api_client, uploaded_print_job):
        api_client.start_job()
        api_client.wait_for_job_state({"Printing"})

        jog_response = api_client.request(
            "POST", "/api/printer/printhead", json={"command": "jog", "x": 5}
        )
        delete_response = api_client.request("DELETE", f"/api/files/local/{uploaded_print_job}")

        assert jog_response.status_code == 409
        assert delete_response.status_code == 409

    @pytest.mark.ui
    @allure.story("Web 控制台执行完整打印控制流程")
    def test_print_workflow_from_web(
        self, api_client, uploaded_print_job, files_page, dashboard_page
    ):
        files_page.open().print_file(uploaded_print_job)
        dashboard_page.wait_for_state("Printing")
        assert dashboard_page.selected_file() == uploaded_print_job

        dashboard_page.pause_or_resume().wait_for_state("Paused")
        dashboard_page.pause_or_resume().wait_for_state("Printing")
        dashboard_page.cancel_print().wait_for_state("Operational")

        assert api_client.get_job()["state"] == "Operational"
