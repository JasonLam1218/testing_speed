import time
import logging
import httpx
import json
from config.settings import Config

class SOCKS5TTFBClient:
    """
    Production-ready SOCKS5 client for measuring Time To First Byte (TTFB) with Gemini API.
    
    Optimized for Gemini API's architecture where:
    - API generates complete responses before sending any data
    - TTFB ≈ Total processing time (not network latency)
    - Processing time after first byte is minimal (<0.1s)
    
    Uses httpx event hooks for precise timing measurement.
    """
    
    def __init__(self, region):
        self.region = region
        proxy_url = self._build_proxy(region)
        
        # Critical timing variables - must be instance variables for event hooks
        self.request_start_time = None
        self.first_byte_time = None
        self.response_complete_time = None
        
        # Connection statistics
        self.connection_attempts = 0
        self.successful_requests = 0
        self.failed_requests = 0
        
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
        """Build SOCKS5 proxy URL with correct NordVPN format"""
        # Same logic as above
        if region.endswith('.us'):
            city = region.replace('.us', '')
            domain = f"{city}.us.nordvpn.com"
        elif region.endswith('.nl'):
            city = region.replace('.nl', '')
            domain = f"{city}.nl.nordvpn.com"
        elif region.endswith('.se'):
            city = region.replace('.se', '')
            domain = f"{city}.se.nordvpn.com"
        else:
            domain = "us.nordvpn.com"
        
        credentials = f"{Config.NORDVPN_USERNAME}:{Config.NORDVPN_PASSWORD}"
        print(f"Debug: Connecting to SOCKS5 proxy at {domain}:{Config.NORDVPN_PORT}")
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
        """Test SOCKS5 proxy connectivity with retry logic"""
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                self.connection_attempts += 1
                
                # Reset timing for connection test
                self.request_start_time = None
                self.first_byte_time = None
                
                response = self.client.get("https://httpbin.org/ip", timeout=10)
                
                if response.status_code == 200:
                    logging.debug(f"[{self.region}] Connection test successful on attempt {attempt + 1}")
                    return True
                else:
                    logging.warning(f"[{self.region}] Connection test failed: HTTP {response.status_code}")
                    
            except Exception as e:
                logging.error(f"[{self.region}] Connection test error (attempt {attempt + 1}): {e}")
                
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    logging.info(f"[{self.region}] Retrying connection in {wait_time}s...")
                    time.sleep(wait_time)
        
        logging.error(f"[{self.region}] Connection failed after {max_retries} attempts")
        return False

    def measure_pure_ttfb(self, prompt):
        """
        Measure TTFB optimized for Gemini API architecture.
        
        Returns comprehensive timing data including:
        - True TTFB (time to first byte)
        - Processing time (minimal for Gemini)
        - Total response time
        - Quality metrics and validation
        """
        try:
            headers = {"Content-Type": "application/json"}
            data = {"contents": [{"parts": [{"text": prompt}]}]}
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={Config.GEMINI_API_KEY}"
            
            # Reset all timing variables
            self.request_start_time = None
            self.first_byte_time = None
            self.response_complete_time = None
            
            # Measure overall request time
            overall_start = time.perf_counter()
            
            # Use streaming for maximum accuracy
            with self.client.stream('POST', url, json=data, headers=headers) as response:
                # Verify we got a response
                response.raise_for_status()
                
                # Read the complete response
                content = b""
                for chunk in response.iter_bytes():
                    content += chunk
                
                self.response_complete_time = time.perf_counter()
            
            # Calculate timing metrics
            total_time = self.response_complete_time - overall_start
            
            # Determine TTFB measurement method and calculate
            if self.request_start_time and self.first_byte_time:
                # Primary method: Event hooks
                ttfb = self.first_byte_time - self.request_start_time
                processing_time = self.response_complete_time - self.first_byte_time
                measurement_method = "event_hooks_accurate"
                
                # Validation for Gemini API characteristics
                if ttfb < 0 or ttfb > total_time:
                    logging.warning(f"[{self.region}] Invalid timing detected, using fallback")
                    ttfb = total_time * 0.98  # Gemini: nearly all time is processing
                    processing_time = total_time * 0.02  # Minimal transfer time
                    measurement_method = "fallback_validation"
                    
            else:
                # Fallback method: Estimation based on Gemini API behavior
                logging.warning(f"[{self.region}] Event hooks failed, using Gemini-optimized estimation")
                ttfb = total_time * 0.98  # Gemini generates complete response before sending
                processing_time = total_time * 0.02  # Minimal data transfer time
                measurement_method = "gemini_estimation"
            
            # Parse response content
            try:
                json_data = json.loads(content.decode('utf-8'))
                text = json_data.get("candidates", [{}])[0]\
                    .get("content", {}).get("parts", [{}])[0]\
                    .get("text", "")
                
                if not text:
                    logging.warning(f"[{self.region}] Empty response text received")
                    text = ""
                    
            except Exception as e:
                logging.error(f"[{self.region}] Response parsing error: {e}")
                return {
                    "success": False,
                    "ttfb": ttfb if 'ttfb' in locals() else None,
                    "total_time": total_time,
                    "error": f"Parsing error: {str(e)}",
                    "measurement_method": measurement_method if 'measurement_method' in locals() else "unknown"
                }
            
            # Calculate quality metrics
            chars_per_second = len(text) / total_time if total_time > 0 else 0
            response_efficiency = len(text) / ttfb if ttfb > 0 else 0
            
            # Success tracking
            self.successful_requests += 1
            
            # Logging with appropriate validation for Gemini API
            logging.info(f"[{self.region}] SUCCESS - TTFB: {ttfb:.3f}s, "
                        f"Processing: {processing_time:.3f}s, Total: {total_time:.3f}s, "
                        f"Method: {measurement_method}, Chars: {len(text)}, "
                        f"Rate: {chars_per_second:.1f} chars/s")
            
            # Gemini-specific validation (adjusted thresholds)
            validation_warnings = []
            
            if ttfb > 30.0:
                validation_warnings.append(f"Very high TTFB: {ttfb:.3f}s")
            elif ttfb < 1.0:
                validation_warnings.append(f"Unusually fast TTFB: {ttfb:.3f}s")
            
            # For Gemini, processing time should be very low
            if processing_time > 1.0:
                validation_warnings.append(f"High processing time: {processing_time:.3f}s (unusual for Gemini)")
            
            # Response size validation
            if len(text) < 5 and total_time > 10.0:
                validation_warnings.append(f"Very short response ({len(text)} chars) for long processing time")
            
            # Log any validation warnings
            for warning in validation_warnings:
                logging.warning(f"[{self.region}] {warning}")
            
            # Determine timing quality
            timing_quality = "high" if measurement_method == "event_hooks_accurate" else "estimated"
            
            return {
                "success": True,
                "ttfb": ttfb,
                "processing_time": processing_time,
                "total_time": total_time,
                "bytes_received": len(content),
                "response_text": text,
                "character_count": len(text),
                "chars_per_second": chars_per_second,
                "response_efficiency": response_efficiency,
                "measurement_method": measurement_method,
                "timing_quality": timing_quality,
                "validation_warnings": validation_warnings
            }

        except httpx.ProxyError as e:
            self.failed_requests += 1
            logging.error(f"[{self.region}] PROXY ERROR: {e}")
            return {
                "success": False, 
                "ttfb": None, 
                "total_time": None, 
                "error": f"Proxy: {e}",
                "error_type": "proxy"
            }
            
        except httpx.TimeoutException as e:
            self.failed_requests += 1
            logging.error(f"[{self.region}] TIMEOUT: {e}")
            return {
                "success": False, 
                "ttfb": None, 
                "total_time": None, 
                "error": f"Timeout: {e}",
                "error_type": "timeout"
            }
            
        except httpx.HTTPStatusError as e:
            self.failed_requests += 1
            logging.error(f"[{self.region}] HTTP ERROR: {e.response.status_code}")
            return {
                "success": False, 
                "ttfb": None, 
                "total_time": None, 
                "error": f"HTTP {e.response.status_code}",
                "error_type": "http"
            }
            
        except Exception as e:
            self.failed_requests += 1
            logging.error(f"[{self.region}] UNEXPECTED ERROR: {type(e).__name__}: {e}")
            return {
                "success": False, 
                "ttfb": None, 
                "total_time": None, 
                "error": f"{type(e).__name__}: {e}",
                "error_type": "unexpected"
            }

    def get_connection_stats(self):
        """Get connection statistics for this client"""
        total_requests = self.successful_requests + self.failed_requests
        success_rate = (self.successful_requests / total_requests) if total_requests > 0 else 0.0
        
        return {
            "connection_attempts": self.connection_attempts,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "success_rate": success_rate
        }

    def __del__(self):
        """Clean up HTTP client and log final statistics"""
        try:
            if hasattr(self, 'client'):
                stats = self.get_connection_stats()
                logging.info(f"[{self.region}] Final stats - "
                           f"Success rate: {stats['success_rate']:.1%}, "
                           f"Successful: {stats['successful_requests']}, "
                           f"Failed: {stats['failed_requests']}")
                self.client.close()
        except:
            pass
