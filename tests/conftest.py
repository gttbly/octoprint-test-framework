import json
import os
import re
import shutil
from pathlib import Path
from uuid import uuid4

import allure
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from config.config import Config
from pages.connection_page import ConnectionPage
from pages.dashboard_page import DashboardPage
from pages.files_page import FilesPage
from pages.login_page import LoginPage
from utils.api_client import OctoPrintAPI

ACTIVE_JOB_STATES = {"Starting", "Printing", "Pausing", "Paused", "Resuming", "Finishing"}


def pytest_addoption(parser):
    parser.addoption("--headed", action="store_true", help="Run UI tests with a visible browser")
    parser.addoption(
        "--allow-hardware-control",
        action="store_true",
        help="Allow heating and motion tests against a non-virtual printer",
    )


def _safe_name(nodeid: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_.-]+", "_", nodeid)[-180:]


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if not report.failed or report.when not in {"setup", "call"}:
        return

    browser = item.funcargs.get("browser") or item.funcargs.get("driver")
    if browser:
        name = _safe_name(item.nodeid)
        Config.SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
        Config.PAGE_SOURCE_DIR.mkdir(parents=True, exist_ok=True)
        screenshot_path = Config.SCREENSHOT_DIR / f"{name}.png"
        source_path = Config.PAGE_SOURCE_DIR / f"{name}.html"
        try:
            screenshot = browser.get_screenshot_as_png()
            screenshot_path.write_bytes(screenshot)
            allure.attach(
                screenshot,
                name="failure-screenshot",
                attachment_type=allure.attachment_type.PNG,
            )
            source_path.write_text(browser.page_source, encoding="utf-8")
            allure.attach(
                browser.page_source,
                name="failure-page-source",
                attachment_type=allure.attachment_type.HTML,
            )
        except Exception:
            pass

    api = item.funcargs.get("api_client")
    if api:
        try:
            snapshot = {
                "connection": api.get_connection(),
                "job": api.get_job(),
                "printer": api.get_printer_state(),
            }
            allure.attach(
                json.dumps(snapshot, indent=2, ensure_ascii=False),
                name="octoprint-state",
                attachment_type=allure.attachment_type.JSON,
            )
        except Exception:
            pass


@pytest.fixture(scope="session", autouse=True)
def validate_environment():
    if not Config.API_KEY:
        pytest.exit("OCTOPRINT_API_KEY is required for the integration suite")
    api = OctoPrintAPI()
    try:
        api.get_version()
        api.get_current_user()
    except Exception as exc:
        pytest.exit(f"OctoPrint is unavailable or credentials are invalid: {exc}")
    finally:
        api.close()


@pytest.fixture
def api_client():
    api = OctoPrintAPI()
    yield api
    api.close()


@pytest.fixture
def unauthenticated_api():
    api = OctoPrintAPI(api_key="")
    yield api
    api.close()


@pytest.fixture
def invalid_key_api():
    api = OctoPrintAPI(api_key="invalid-e2e-key")
    yield api
    api.close()


def _chrome_driver(headless: bool):
    options = Options()
    if headless:
        options.add_argument("--headless=new")
    if os.getenv("CI") == "true":
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-search-engine-choice-screen")

    driver_path = Config.DRIVER_PATH or shutil.which("chromedriver")
    service = Service(driver_path) if driver_path else Service()
    return webdriver.Chrome(service=service, options=options)


@pytest.fixture
def browser(request):
    if Config.BROWSER != "chrome":
        pytest.fail(f"Unsupported browser: {Config.BROWSER}")
    instance = _chrome_driver(Config.HEADLESS and not request.config.getoption("--headed"))
    instance.base_url = Config.BASE_URL
    instance.set_page_load_timeout(Config.LONG_TIMEOUT)
    yield instance
    instance.quit()


@pytest.fixture
def driver(browser):
    if not Config.USERNAME or not Config.PASSWORD:
        pytest.fail("UI tests require OCTOPRINT_USERNAME and OCTOPRINT_PASSWORD")
    LoginPage(browser).open().login(Config.USERNAME, Config.PASSWORD)
    return browser


@pytest.fixture
def login_page(browser):
    return LoginPage(browser)


@pytest.fixture
def connection_page(driver):
    return ConnectionPage(driver)


@pytest.fixture
def files_page(driver):
    return FilesPage(driver)


@pytest.fixture
def dashboard_page(driver):
    return DashboardPage(driver)


@pytest.fixture
def connected_printer(api_client):
    return api_client.ensure_connected()


@pytest.fixture
def control_guard(request, api_client, connected_printer):
    port = connected_printer["current"].get("port")
    if port != "VIRTUAL" and not request.config.getoption("--allow-hardware-control"):
        pytest.skip("Hardware control is disabled; use --allow-hardware-control for a real printer")
    job = api_client.get_job()
    if job["state"] in ACTIVE_JOB_STATES:
        pytest.skip(f"Printer has an active job: {job['state']}")
    yield connected_printer
    try:
        api_client.set_tool_target(0)
        api_client.set_bed_target(0)
    except Exception:
        pass


@pytest.fixture
def virtual_printer(api_client, connected_printer):
    port = connected_printer["current"].get("port")
    if port != "VIRTUAL":
        pytest.skip(f"This scenario requires OctoPrint virtual printer, current port: {port}")
    job = api_client.get_job()
    if job["state"] in ACTIVE_JOB_STATES:
        pytest.skip(f"Virtual printer has an active job: {job['state']}")
    yield connected_printer
    try:
        current = api_client.get_job()
        filename = current.get("job", {}).get("file", {}).get("name") or ""
        if current["state"] in ACTIVE_JOB_STATES and filename.startswith("e2e_"):
            api_client.cancel_job()
            api_client.wait_for_job_state({"Operational"})
        api_client.set_tool_target(0)
        api_client.set_bed_target(0)
    except Exception:
        pass


@pytest.fixture
def gcode_file(tmp_path: Path) -> Path:
    path = tmp_path / f"e2e_file_{uuid4().hex[:8]}.gcode"
    path.write_text("G28\nG90\nG1 X10 Y10 Z1 F3000\nM105\n", encoding="utf-8")
    return path


@pytest.fixture
def long_gcode_file(tmp_path: Path) -> Path:
    path = tmp_path / f"e2e_job_{uuid4().hex[:8]}.gcode"
    moves = "".join(f"G1 X{i % 100} Y{(i * 7) % 100} F3000\n" for i in range(3000))
    path.write_text(f"G28\nG90\n{moves}", encoding="utf-8")
    return path


@pytest.fixture
def uploaded_gcode(api_client, gcode_file):
    api_client.upload_file(gcode_file)
    yield gcode_file.name
    try:
        api_client.delete_file(gcode_file.name)
    except Exception:
        pass


@pytest.fixture
def uploaded_print_job(api_client, virtual_printer, long_gcode_file):
    api_client.upload_file(long_gcode_file, select=True)
    yield long_gcode_file.name
    try:
        job = api_client.get_job()
        if job["state"] in ACTIVE_JOB_STATES:
            api_client.cancel_job()
            api_client.wait_for_job_state({"Operational"})
        api_client.delete_file(long_gcode_file.name)
    except Exception:
        pass
