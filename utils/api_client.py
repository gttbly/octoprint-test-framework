import requests
from config.config import Config


class OctoPrintAPI:
    def __init__(self):
        self.base_url = Config.BASE_URL
        self.headers = {}
        if Config.API_KEY:
            self.headers["X-Api-Key"] = Config.API_KEY

    def connect_printer(self):
        try:
            r = requests.post(
                f"{self.base_url}/api/connection",
                headers=self.headers,
                json={"command": "connect"},
                timeout=15
            )
            if r.status_code in (200, 204):
                return True
        except Exception:
            pass
        return False

    def get_printer_state(self):
        r = requests.get(
            f"{self.base_url}/api/printer",
            headers=self.headers,
            timeout=10
        )
        r.raise_for_status()
        return r.json()

    def get_tool_temperatures(self):
        state = self.get_printer_state()
        return state.get("temperature", {}).get("tool0", {})

    def get_bed_temperature(self):
        state = self.get_printer_state()
        return state.get("temperature", {}).get("bed", {})

    def send_gcode(self, commands):
        r = requests.post(
            f"{self.base_url}/api/printer/command",
            headers=self.headers,
            json={"commands": commands},
            timeout=10
        )
        r.raise_for_status()
        if r.status_code == 204 or not r.content:
            return True
        return r.json()

    def get_filament_usage(self):
        try:
            r = requests.get(
                f"{self.base_url}/plugin/filamentmanager/spools",
                headers=self.headers,
                timeout=10
            )
            if r.status_code == 200:
                return r.json()
        except Exception:
            pass
        return None
