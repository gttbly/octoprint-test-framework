from pathlib import Path
from typing import Any
from urllib.parse import quote

import requests

from config.config import Config
from utils.wait import wait_until


class OctoPrintAPI:
    """Small typed facade over the OctoPrint REST API."""

    def __init__(
        self,
        base_url: str = Config.BASE_URL,
        api_key: str = Config.API_KEY,
        timeout: int = Config.API_TIMEOUT,
        session: requests.Session | None = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = session or requests.Session()
        self._owns_session = session is None
        self.session.headers.update({"Accept": "application/json"})
        if api_key:
            self.session.headers.update({"X-Api-Key": api_key})

    def close(self) -> None:
        if self._owns_session:
            self.session.close()

    def request(
        self,
        method: str,
        path: str,
        *,
        expected_status: int | tuple[int, ...] | None = None,
        **kwargs: Any,
    ) -> requests.Response:
        response = self.session.request(
            method,
            f"{self.base_url}{path}",
            timeout=kwargs.pop("timeout", self.timeout),
            **kwargs,
        )
        if expected_status is not None:
            allowed = (expected_status,) if isinstance(expected_status, int) else expected_status
            if response.status_code not in allowed:
                response.raise_for_status()
                raise AssertionError(
                    f"Expected HTTP {allowed}, got {response.status_code}: {response.text[:500]}"
                )
        return response

    def _json(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        response = self.request(method, path, expected_status=200, **kwargs)
        return response.json()

    # Service and identity
    def get_version(self) -> dict[str, Any]:
        return self._json("GET", "/api/version")

    def get_server_status(self) -> dict[str, Any]:
        return self._json("GET", "/api/server")

    def get_current_user(self) -> dict[str, Any]:
        return self._json("GET", "/api/currentuser")

    def get_printer_profiles(self) -> dict[str, Any]:
        return self._json("GET", "/api/printerprofiles")

    # Connection
    def get_connection(self) -> dict[str, Any]:
        return self._json("GET", "/api/connection")

    def connect_printer(
        self,
        *,
        port: str | None = None,
        baudrate: int | None = None,
        printer_profile: str | None = None,
    ) -> bool:
        payload: dict[str, Any] = {"command": "connect"}
        if port:
            payload["port"] = port
        if baudrate:
            payload["baudrate"] = baudrate
        if printer_profile:
            payload["printerProfile"] = printer_profile
        self.request("POST", "/api/connection", json=payload, expected_status=(200, 204))
        return True

    def disconnect_printer(self) -> bool:
        self.request(
            "POST",
            "/api/connection",
            json={"command": "disconnect"},
            expected_status=(200, 204),
        )
        return True

    def wait_for_connection_state(
        self, states: set[str], timeout: int = Config.LONG_TIMEOUT
    ) -> str:
        return wait_until(
            lambda: (
                state if (state := self.get_connection()["current"]["state"]) in states else None
            ),
            timeout=timeout,
            description=f"connection state in {sorted(states)}",
        )

    def ensure_connected(self) -> dict[str, Any]:
        connection = self.get_connection()
        if connection["current"]["state"] in {"Closed", "Offline", "Error"}:
            self.connect_printer()
            self.wait_for_connection_state({"Operational"})
            connection = self.get_connection()
        return connection

    # Printer status and control
    def get_printer_state(self) -> dict[str, Any]:
        return self._json("GET", "/api/printer")

    def get_tool_temperatures(self, tool: str = "tool0") -> dict[str, Any]:
        return self.get_printer_state().get("temperature", {}).get(tool, {})

    def get_bed_temperature(self) -> dict[str, Any]:
        return self.get_printer_state().get("temperature", {}).get("bed", {})

    def set_tool_target(self, target: float, tool: str = "tool0") -> bool:
        self.request(
            "POST",
            "/api/printer/tool",
            json={"command": "target", "targets": {tool: target}},
            expected_status=204,
        )
        return True

    def set_bed_target(self, target: float) -> bool:
        self.request(
            "POST",
            "/api/printer/bed",
            json={"command": "target", "target": target},
            expected_status=204,
        )
        return True

    def wait_for_temperature_target(
        self,
        component: str,
        target: float,
        *,
        timeout: int = Config.API_TIMEOUT,
    ) -> dict[str, Any]:
        def target_accepted() -> dict[str, Any] | None:
            value = self.get_printer_state()["temperature"][component]
            return value if value["target"] == target else None

        return wait_until(
            target_accepted,
            timeout=timeout,
            interval=0.25,
            description=f"{component} target to become {target}°C",
        )

    def wait_for_temperature(
        self,
        component: str,
        target: float,
        *,
        tolerance: float = 2.0,
        timeout: int = Config.LONG_TIMEOUT,
    ) -> dict[str, Any]:
        def at_target() -> dict[str, Any] | None:
            temperatures = self.get_printer_state()["temperature"]
            value = temperatures[component]
            return value if abs(value["actual"] - target) <= tolerance else None

        return wait_until(
            at_target,
            timeout=timeout,
            interval=1,
            description=f"{component} temperature near {target}°C",
        )

    def send_gcode(self, commands: list[str] | str) -> bool:
        payload = {"commands": commands} if isinstance(commands, list) else {"command": commands}
        self.request(
            "POST",
            "/api/printer/command",
            json=payload,
            expected_status=(200, 204),
        )
        return True

    def home(self, axes: list[str]) -> bool:
        self.request(
            "POST",
            "/api/printer/printhead",
            json={"command": "home", "axes": axes},
            expected_status=204,
        )
        return True

    def jog(self, **axes: float) -> bool:
        self.request(
            "POST",
            "/api/printer/printhead",
            json={"command": "jog", **axes},
            expected_status=204,
        )
        return True

    # Files
    def get_files(self, location: str = "local") -> dict[str, Any]:
        return self._json("GET", f"/api/files/{quote(location, safe='')}")

    def get_file(self, filename: str, location: str = "local") -> dict[str, Any]:
        path = quote(filename, safe="/")
        return self._json("GET", f"/api/files/{quote(location, safe='')}/{path}")

    def upload_file(
        self,
        filepath: str | Path,
        *,
        location: str = "local",
        select: bool = False,
        print_file: bool = False,
    ) -> dict[str, Any]:
        filepath = Path(filepath)
        with filepath.open("rb") as stream:
            response = self.request(
                "POST",
                f"/api/files/{quote(location, safe='')}",
                files={"file": (filepath.name, stream)},
                data={
                    "select": str(select).lower(),
                    "print": str(print_file).lower(),
                },
                timeout=Config.LONG_TIMEOUT,
                expected_status=201,
            )
        return response.json()

    def select_file(
        self,
        filename: str,
        *,
        location: str = "local",
        print_file: bool = False,
    ) -> bool:
        path = quote(filename, safe="/")
        self.request(
            "POST",
            f"/api/files/{quote(location, safe='')}/{path}",
            json={"command": "select", "print": print_file},
            expected_status=204,
        )
        return True

    def delete_file(self, filename: str, location: str = "local") -> bool:
        path = quote(filename, safe="/")
        self.request(
            "DELETE",
            f"/api/files/{quote(location, safe='')}/{path}",
            expected_status=204,
        )
        return True

    # Print job
    def get_job(self) -> dict[str, Any]:
        return self._json("GET", "/api/job")

    def _job_command(self, payload: dict[str, Any]) -> bool:
        self.request("POST", "/api/job", json=payload, expected_status=204)
        return True

    def start_job(self) -> bool:
        return self._job_command({"command": "start"})

    def pause_job(self) -> bool:
        return self._job_command({"command": "pause", "action": "pause"})

    def resume_job(self) -> bool:
        return self._job_command({"command": "pause", "action": "resume"})

    def cancel_job(self) -> bool:
        return self._job_command({"command": "cancel"})

    def wait_for_job_state(
        self, states: set[str], timeout: int = Config.LONG_TIMEOUT
    ) -> dict[str, Any]:
        return wait_until(
            lambda: job if (job := self.get_job())["state"] in states else None,
            timeout=timeout,
            description=f"job state in {sorted(states)}",
        )
