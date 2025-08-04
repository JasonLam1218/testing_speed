import time
import logging
import requests
from config.settings import Config

class SOCKS5Client:
    def __init__(self, region):
        self.region = region
        self.proxy = self._build_proxy(region)
        self.session = requests.Session()
        self.session.proxies = {
            "http": self.proxy,
            "https": self.proxy
        }
        logging.info(f"SOCKS5 client ready for {region}")

    def _build_proxy(self, region):
        domain = f"{region}.socks.nordhold.net"
        cred = f"{Config.NORDVPN_USERNAME}:{Config.NORDVPN_PASSWORD}"
        return f"socks5://{cred}@{domain}:{Config.NORDVPN_PORT}"

    def test_connection(self):
        try:
            r = self.session.get("https://httpbin.org/ip", timeout=10)
            return r.status_code == 200
        except:
            return False

    def generate_content(self, prompt):
        try:
            headers = {
                "Content-Type": "application/json"
            }
            
            # Start timer immediately before API request
            start = time.time()
            r = self.session.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={Config.GEMINI_API_KEY}",
                json={"contents": [{"parts": [{"text": prompt}]}]},
                headers=headers,
                timeout=Config.TIMEOUT_SECONDS
            )
            r.raise_for_status()
            # Stop timer immediately after receiving response
            elapsed = time.time() - start
            
            # JSON parsing happens after timing (excluded from measurement)
            text = r.json().get("candidates", [{}])[0]\
                .get("content", {}).get("parts", [{}])[0]\
                .get("text", "")
            
            return {"success": True, "time": elapsed, "response": text}
        
        except requests.exceptions.ProxyError as e:
            logging.error(f"{self.region} PROXY ERROR: {e}")
            return {"success": False, "time": None, "error": f"Proxy: {e}"}
        except requests.exceptions.Timeout as e:
            logging.error(f"{self.region} TIMEOUT: {e}")
            return {"success": False, "time": None, "error": f"Timeout: {e}"}
        except requests.exceptions.HTTPError as e:
            logging.error(f"{self.region} HTTP ERROR: {e.response.status_code} - {e.response.text}")
            return {"success": False, "time": None, "error": f"HTTP {e.response.status_code}: {e.response.text}"}
        except Exception as e:
            logging.error(f"{self.region} UNKNOWN ERROR: {type(e).__name__}: {e}")
            return {"success": False, "time": None, "error": f"{type(e).__name__}: {e}"}

