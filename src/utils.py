import os
import socket
import time
from datetime import datetime
import requests
from ping3 import ping
from config.settings import Config

class FileUtils:
    @staticmethod
    def ensure_directories():
        for d in (Config.RESULTS_DIR, Config.REPORTS_DIR):
            os.makedirs(d, exist_ok=True)

class NetworkUtils:
    @staticmethod
    def test_connectivity(host, port=443, timeout=5):
        try:
            sock = socket.create_connection((host, port), timeout)
            sock.close()
            return True
        except:
            return False

    @staticmethod
    def ping_host(host, count=4):
        times = []
        for _ in range(count):
            t = ping(host, timeout=2)
            if t:
                times.append(t*1000)
            time.sleep(0.2)
        return {
            "success": bool(times),
            "avg_ping": sum(times)/len(times) if times else None,
            "loss": (count-len(times))/count*100
        }

class ValidationUtils:
    @staticmethod
    def validate_environment():
        errors = []
        # config
        try:
            Config.validate_config()
        except ValueError as e:
            errors.append(str(e))
        # dirs
        try:
            FileUtils.ensure_directories()
        except Exception as e:
            errors.append(f"Dir error: {e}")
        # network
        if not NetworkUtils.test_connectivity("generativelanguage.googleapis.com"):
            errors.append("Cannot reach Gemini API")
        return {"valid": not errors, "errors": errors}
