import requests
from config.config import Config


class OctoPrintAPI:
    def __init__(self):
        self.base_url = Config.BASE_URL
        self.headers = {"X-Api-Key": Config.API_KEY}

    # ---------- 连接控制 ----------
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

    # ---------- 版本信息 ----------
    def get_version(self):
        r = requests.get(
            f"{self.base_url}/api/version",
            headers=self.headers,
            timeout=10
        )
        r.raise_for_status()
        return r.json()

    # ---------- 打印机状态 ----------
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

    # ---------- 发送 G-code ----------
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

    # ---------- 文件列表 ----------
    def get_files(self, location="local"):
        r = requests.get(
            f"{self.base_url}/api/files/{location}",
            headers=self.headers,
            timeout=10
        )
        r.raise_for_status()
        return r.json()

    # ---------- 上传文件 ----------
    def upload_file(self, filepath, location="local"):
        with open(filepath, "rb") as f:
            files = {"file": f}
            data = {"location": location, "select": "false", "print": "false"}
            r = requests.post(
                f"{self.base_url}/api/files/{location}",
                headers=self.headers,
                files=files,
                data=data,
                timeout=30
            )
        r.raise_for_status()
        return r.json()

    # ---------- 删除文件 ----------
    def delete_file(self, filename, location="local"):
        r = requests.delete(
            f"{self.base_url}/api/files/{location}/{filename}",
            headers=self.headers,
            timeout=10
        )
        r.raise_for_status()
        return True

    # ---------- 任务状态 ----------
    def get_job(self):
        r = requests.get(
            f"{self.base_url}/api/job",
            headers=self.headers,
            timeout=10
        )
        r.raise_for_status()
        return r.json()

    # ---------- 耗材插件（可选）----------
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
