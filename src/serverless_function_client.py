import time
import logging
import httpx
import json
from config.settings import Config

class ServerlessFunctionClient:
    """
    HTTP client for testing Vercel Serverless Functions with Gemini API.
    Handles cold starts and provides detailed performance metrics.
    """
    
    def __init__(self):
        self.deployment_name = "serverless_function"
        self.url = Config.SERVERLESS_FUNCTION_URL
        self.timeout = Config.get_deployment_config(self.deployment_name)["max_timeout"]
        
        # Cold start detection
        self.first_request = True
        self.cold_start_time = None
        
        # Connection statistics
        self.successful_requests = 0
        self.failed_requests = 0
        self.cold_starts_detected = 0
        
        # Initialize HTTP client optimized for serverless
        self.client = httpx.Client(
            timeout=self.timeout,
            headers={
                "User-Agent": "GeminiSpeedTest/1.0",
                "Accept": "application/json",
                "Content-Type": "application/json"
            },
            follow_redirects=True
        )
        
        logging.info(f"Serverless Function client initialized for {self.url}")
    
    def test_connection(self):
        """Test Serverless Function connectivity"""
        try:
            test_prompt = "Say 'OK'"
            response = self.client.post(
                self.url,
                json={"prompt": test_prompt},
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            logging.error(f"Serverless Function connection test failed: {e}")
            return False
    
    def _detect_cold_start(self, response_time):
        """
        Detect cold start based on response time patterns
        First request or unusually high response time indicates cold start
        """
        cold_start_threshold = 2.0  # seconds
        
        if self.first_request:
            self.first_request = False
            if response_time > cold_start_threshold:
                self.cold_starts_detected += 1
                self.cold_start_time = response_time
                return True
        elif response_time > cold_start_threshold:
            # Potential cold start during testing
            self.cold_starts_detected += 1
            return True
        
        return False
    
    def generate_content(self, prompt):
        """
        Generate content using Serverless Function with cold start detection
        """
        try:
            # Precise timing measurement
            start_time = time.perf_counter()
            
            response = self.client.post(
                self.url,
                json={"prompt": prompt},
                timeout=self.timeout
            )
            
            end_time = time.perf_counter()
            elapsed = end_time - start_time
            
            response.raise_for_status()
            
            # Parse response
            result = response.json()
            text = result.get("response", result.get("text", ""))
            
            # Detect cold start
            is_cold_start = self._detect_cold_start(elapsed)
            
            self.successful_requests += 1
            
            status = "COLD START" if is_cold_start else "SUCCESS"
            logging.info(f"Serverless Function {status}: {elapsed:.3f}s, {len(text)} chars")
            
            return {
                "success": True,
                "time": elapsed,
                "response": text,
                "method": "serverless_function",
                "is_cold_start": is_cold_start,
                "status_code": response.status_code,
                "response_size": len(response.content),
                "character_count": len(text),
                "execution_time": elapsed - (0.1 if not is_cold_start else 0.5)  # Estimate network overhead
            }
            
        except httpx.TimeoutException as e:
            self.failed_requests += 1
            logging.error(f"Serverless Function TIMEOUT: {e}")
            return {
                "success": False,
                "time": None,
                "error": f"Timeout: {e}",
                "error_type": "timeout",
                "method": "serverless_function"
            }
            
        except httpx.HTTPStatusError as e:
            self.failed_requests += 1
            logging.error(f"Serverless Function HTTP ERROR: {e.response.status_code}")
            return {
                "success": False,
                "time": None,
                "error": f"HTTP {e.response.status_code}: {e.response.text}",
                "error_type": "http",
                "method": "serverless_function",
                "status_code": e.response.status_code
            }
            
        except Exception as e:
            self.failed_requests += 1
            logging.error(f"Serverless Function UNEXPECTED ERROR: {type(e).__name__}: {e}")
            return {
                "success": False,
                "time": None,
                "error": f"{type(e).__name__}: {e}",
                "error_type": "unexpected",
                "method": "serverless_function"
            }
    
    def measure_streaming_performance(self, prompt):
        """
        Measure streaming performance with cold start awareness
        """
        try:
            start_time = time.perf_counter()
            first_byte_time = None
            chunks_received = 0
            total_bytes = 0
            
            with self.client.stream('POST', self.url, json={"prompt": prompt}) as response:
                response.raise_for_status()
                
                content = b""
                for chunk in response.iter_bytes():
                    if first_byte_time is None:
                        first_byte_time = time.perf_counter()
                    
                    content += chunk
                    chunks_received += 1
                    total_bytes += len(chunk)
                
                end_time = time.perf_counter()
            
            # Calculate metrics
            total_time = end_time - start_time
            ttfb = first_byte_time - start_time if first_byte_time else total_time
            processing_time = end_time - first_byte_time if first_byte_time else 0
            
            # Detect cold start
            is_cold_start = self._detect_cold_start(total_time)
            
            # Parse response
            result = json.loads(content.decode('utf-8'))
            text = result.get("response", result.get("text", ""))
            
            self.successful_requests += 1
            
            return {
                "success": True,
                "total_time": total_time,
                "ttfb": ttfb,
                "processing_time": processing_time,
                "response": text,
                "character_count": len(text),
                "chunks_received": chunks_received,
                "total_bytes": total_bytes,
                "chars_per_second": len(text) / total_time if total_time > 0 else 0,
                "is_cold_start": is_cold_start,
                "method": "serverless_function",
                "measurement_type": "streaming"
            }
            
        except Exception as e:
            self.failed_requests += 1
            logging.error(f"Serverless Function streaming error: {e}")
            return {
                "success": False,
                "error": str(e),
                "method": "serverless_function",
                "measurement_type": "streaming"
            }
    
    def get_stats(self):
        """Get client statistics including cold start info"""
        total = self.successful_requests + self.failed_requests
        return {
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "success_rate": self.successful_requests / total if total > 0 else 0.0,
            "cold_starts_detected": self.cold_starts_detected,
            "cold_start_rate": self.cold_starts_detected / self.successful_requests if self.successful_requests > 0 else 0.0,
            "method": "serverless_function"
        }
    
    def __del__(self):
        """Clean up HTTP client"""
        try:
            if hasattr(self, 'client'):
                self.client.close()
        except:
            pass
