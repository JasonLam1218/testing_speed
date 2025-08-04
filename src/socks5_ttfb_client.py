import time
import logging
import httpx
import json
from config.settings import Config

class SOCKS5TTFBClient:
    """
    Advanced SOCKS5 client for measuring true Time To First Byte (TTFB).
    
    Uses httpx event hooks to capture the exact moment when:
    1. HTTP request is sent over the wire
    2. First byte of HTTP response is received
    
    For Gemini API: TTFB ≈ Processing Time (API generates complete response before sending)
    """
    
    def __init__(self, region):
        self.region = region
        proxy_url = self._build_proxy(region)
        
        # Critical timing variables - must be instance variables for event hooks
        self.request_start_time = None
        self.first_byte_time = None
        self.response_complete_time = None
        
        self.client = httpx.Client(
            proxy=proxy_url,
            timeout=Config.TIMEOUT_SECONDS,
            event_hooks={
                'request': [self._on_request_start],
                'response': [self._on_response_start]
            }
        )
        
        logging.info(f"SOCKS5 TTFB client initialized for {region}")

    def _build_proxy(self, region):
        """Build SOCKS5 proxy URL with credentials"""
        domain = f"{region}.socks.nordhold.net"
        credentials = f"{Config.NORDVPN_USERNAME}:{Config.NORDVPN_PASSWORD}"
        return f"socks5://{credentials}@{domain}:{Config.NORDVPN_PORT}"

    def _on_request_start(self, request):
        """Event hook: Called when HTTP request is sent over the wire"""
        self.request_start_time = time.perf_counter()
        logging.debug(f"[{self.region}] HTTP request sent at {self.request_start_time:.6f}")

    def _on_response_start(self, response):
        """Event hook: Called when first byte of HTTP response arrives"""
        self.first_byte_time = time.perf_counter()
        logging.debug(f"[{self.region}] First byte received at {self.first_byte_time:.6f}")

    def test_connection(self):
        """Test SOCKS5 proxy connectivity"""
        try:
            # Reset timing for connection test
            self.request_start_time = None
            self.first_byte_time = None
            
            response = self.client.get("https://httpbin.org/ip", timeout=10)
            
            if response.status_code == 200:
                logging.debug(f"[{self.region}] Connection test successful")
                return True
            else:
                logging.warning(f"[{self.region}] Connection test failed: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            logging.error(f"[{self.region}] Connection test error: {e}")
            return False

    def measure_pure_ttfb(self, prompt):
        """
        Measure true TTFB using httpx streaming for maximum accuracy.
        
        This method captures the exact moment when the first byte arrives,
        separate from total response processing time.
        """
        try:
            headers = {"Content-Type": "application/json"}
            data = {"contents": [{"parts": [{"text": prompt}]}]}
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={Config.GEMINI_API_KEY}"
            
            # Reset all timing variables
            self.request_start_time = None
            self.first_byte_time = None
            self.response_complete_time = None
            
            # Use streaming to capture true first byte timing
            overall_start = time.perf_counter()
            
            with self.client.stream('POST', url, json=data, headers=headers) as response:
                # Capture the moment streaming starts (true first byte)
                if self.first_byte_time is None:
                    self.first_byte_time = time.perf_counter()
                
                response.raise_for_status()
                
                # Read the complete response
                content = b""
                for chunk in response.iter_bytes():
                    content += chunk
                
                self.response_complete_time = time.perf_counter()
            
            # Calculate all timing metrics
            total_time = self.response_complete_time - overall_start
            
            if self.request_start_time and self.first_byte_time:
                # True TTFB from event hooks
                true_ttfb = self.first_byte_time - self.request_start_time
                processing_time = self.response_complete_time - self.first_byte_time
                measurement_method = "streaming_with_hooks"
                
                # Validation: Ensure timing makes sense
                if true_ttfb < 0 or true_ttfb > total_time:
                    logging.warning(f"[{self.region}] Invalid timing detected, using fallback")
                    true_ttfb = total_time * 0.95  # Most time is processing for Gemini
                    processing_time = total_time * 0.05  # Minimal transfer time
                    measurement_method = "fallback_validation"
                    
            else:
                # Fallback if event hooks failed
                logging.warning(f"[{self.region}] Event hooks failed, using estimation")
                true_ttfb = total_time * 0.95  # Gemini-specific: most time is processing
                processing_time = total_time * 0.05
                measurement_method = "estimation_fallback"
            
            # Parse response content
            try:
                json_data = json.loads(content.decode('utf-8'))
                text = json_data.get("candidates", [{}])[0]\
                    .get("content", {}).get("parts", [{}])[0]\
                    .get("text", "")
                
                if not text:
                    logging.warning(f"[{self.region}] Empty response text received")
                    
            except Exception as e:
                logging.error(f"[{self.region}] Response parsing error: {e}")
                return {
                    "success": False,
                    "ttfb": true_ttfb,
                    "total_time": total_time,
                    "error": f"Parsing error: {str(e)}"
                }
            
            # Quality metrics
            chars_per_second = len(text) / total_time if total_time > 0 else 0
            
            # Log comprehensive results
            logging.info(f"[{self.region}] SUCCESS - TTFB: {true_ttfb:.3f}s, "
                        f"Processing: {processing_time:.3f}s, Total: {total_time:.3f}s, "
                        f"Method: {measurement_method}, Chars: {len(text)}, "
                        f"Rate: {chars_per_second:.1f} chars/s")
            
            # Validation warnings
            if true_ttfb > 10.0:
                logging.warning(f"[{self.region}] Very high TTFB: {true_ttfb:.3f}s")
            if processing_time < 0.01:
                logging.warning(f"[{self.region}] Unusually low processing time: {processing_time:.3f}s")
            
            return {
                "success": True,
                "ttfb": true_ttfb,
                "processing_time": processing_time,
                "total_time": total_time,
                "bytes_received": len(content),
                "response_text": text,
                "character_count": len(text),
                "chars_per_second": chars_per_second,
                "measurement_method": measurement_method,
                "timing_quality": "high" if measurement_method == "streaming_with_hooks" else "estimated"
            }

        except httpx.ProxyError as e:
            logging.error(f"[{self.region}] PROXY ERROR: {e}")
            return {"success": False, "ttfb": None, "total_time": None, "error": f"Proxy: {e}"}
        except httpx.TimeoutException as e:
            logging.error(f"[{self.region}] TIMEOUT: {e}")
            return {"success": False, "ttfb": None, "total_time": None, "error": f"Timeout: {e}"}
        except httpx.HTTPStatusError as e:
            logging.error(f"[{self.region}] HTTP ERROR: {e.response.status_code}")
            return {"success": False, "ttfb": None, "total_time": None, "error": f"HTTP {e.response.status_code}"}
        except Exception as e:
            logging.error(f"[{self.region}] UNEXPECTED ERROR: {type(e).__name__}: {e}")
            return {"success": False, "ttfb": None, "total_time": None, "error": f"{type(e).__name__}: {e}"}

    def __del__(self):
        """Clean up HTTP client"""
        try:
            if hasattr(self, 'client'):
                self.client.close()
        except:
            pass
