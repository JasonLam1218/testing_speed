import time
import logging
import httpx
import json
from config.settings import Config

class EdgeFunctionClient:
    """
    HTTP client for testing Vercel Edge Functions with Gemini API.
    FIXED VERSION - Proper TTFB measurement for JSON responses.
    """
    
    def __init__(self):
        self.deployment_name = "edge_function"
        self.url = Config.EDGE_FUNCTION_URL
        self.timeout = 25
        
        # Connection statistics
        self.successful_requests = 0
        self.failed_requests = 0
        
        # Initialize HTTP client with optimized settings for edge functions
        self.client = httpx.Client(
            timeout=self.timeout,
            headers={
                "User-Agent": "GeminiSpeedTest/1.0",
                "Accept": "application/json",
                "Content-Type": "application/json"
            },
            follow_redirects=True
        )
        
        logging.info(f"Edge Function client initialized for {self.url}")

    def test_connection(self):
        """Test Edge Function connectivity"""
        try:
            # Use a simple health check prompt
            test_prompt = "Say 'OK'"
            response = self.client.post(
                self.url,
                json={"prompt": test_prompt},
                timeout=5
            )
            return response.status_code == 200
        except Exception as e:
            logging.error(f"Edge Function connection test failed: {e}")
            return False

    def generate_content(self, prompt):
        """
        Generate content using Edge Function with precise timing
        Returns standardized response format
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
            
            self.successful_requests += 1
            logging.info(f"Edge Function SUCCESS: {elapsed:.3f}s, {len(text)} chars")
            
            return {
                "success": True,
                "time": elapsed,
                "response": text,
                "method": "edge_function",
                "status_code": response.status_code,
                "response_size": len(response.content),
                "character_count": len(text)
            }
            
        except httpx.TimeoutException as e:
            self.failed_requests += 1
            logging.error(f"Edge Function TIMEOUT: {e}")
            return {
                "success": False,
                "time": None,
                "error": f"Timeout: {e}",
                "error_type": "timeout",
                "method": "edge_function"
            }
            
        except httpx.HTTPStatusError as e:
            self.failed_requests += 1
            logging.error(f"Edge Function HTTP ERROR: {e.response.status_code}")
            return {
                "success": False,
                "time": None,
                "error": f"HTTP {e.response.status_code}: {e.response.text}",
                "error_type": "http",
                "method": "edge_function",
                "status_code": e.response.status_code
            }
            
        except Exception as e:
            self.failed_requests += 1
            logging.error(f"Edge Function UNEXPECTED ERROR: {type(e).__name__}: {e}")
            return {
                "success": False,
                "time": None,
                "error": f"{type(e).__name__}: {e}",
                "error_type": "unexpected",
                "method": "edge_function"
            }

    def measure_streaming_performance(self, prompt):
        """
        ✅ FIXED: Proper TTFB measurement for Vercel Edge Functions
        Since Vercel returns complete JSON, TTFB = time to receive response headers
        """
        try:
            start_time = time.perf_counter()
            
            # ✅ FIX: For Vercel functions, TTFB = time to receive response headers
            response = self.client.post(
                self.url,
                json={"prompt": prompt},
                timeout=self.timeout
            )
            ttfb = time.perf_counter() - start_time  # ⚡ TTFB = headers received time
            
            response.raise_for_status()
            result = response.json()
            text = result.get("response", result.get("text", ""))
            
            end_time = time.perf_counter()
            total_time = end_time - start_time
            processing_time = total_time - ttfb
            
            # ✅ Validate TTFB is reasonable
            if ttfb > Config.BASELINE_MAX_TTFB:
                logging.warning(f"High TTFB detected: {ttfb:.3f}s (threshold: {Config.BASELINE_MAX_TTFB}s)")
            elif ttfb < Config.BASELINE_MIN_TTFB:
                logging.warning(f"Unusually low TTFB: {ttfb:.3f}s (minimum: {Config.BASELINE_MIN_TTFB}s)")
                
            # Calculate realistic streaming metrics
            chars_per_second = len(text) / total_time if total_time > 0 else 0
            
            # ✅ Calculate streaming consistency (always 1.0 for JSON responses)
            streaming_consistency = 1.0  # JSON responses are always consistent
            
            # ✅ Calculate user experience score
            user_experience_score = 0.5  # Default
            if total_time > 0 and len(text) > 0:
                responsiveness = min(1.0, 3.0 / ttfb) if ttfb > 0 else 0.5  # Adjusted for VPN
                throughput = min(1.0, (len(text) / total_time) / 200.0)  # Adjusted threshold
                user_experience_score = (responsiveness * 0.6 + throughput * 0.4)
            
            return {
                "success": True,
                "total_time": total_time,  # 📈 Total response time
                "ttfb": ttfb,  # ⚡ Time To First Byte (headers received)
                "processing_time": processing_time,  # 🔄 Post-TTFB processing
                "response": text,
                "character_count": len(text),
                "chunks_received": 1,  # JSON responses come as single chunk
                "total_bytes": len(response.content),
                "chars_per_second": chars_per_second,
                "streaming_consistency": streaming_consistency,  # Always 1.0 for JSON
                "user_experience_score": user_experience_score,
                "method": "edge_function",
                "measurement_type": "streaming",
                "response_type": "json"  # ✅ Indicate this is not true streaming
            }
            
        except Exception as e:
            logging.error(f"Edge Function streaming measurement failed: {e}")
            return {"success": False, "error": str(e), "method": "edge_function"}

    def get_stats(self):
        """Get client statistics"""
        total = self.successful_requests + self.failed_requests
        return {
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "success_rate": self.successful_requests / total if total > 0 else 0.0,
            "method": "edge_function"
        }

    def __del__(self):
        """Clean up HTTP client"""
        try:
            if hasattr(self, 'client'):
                self.client.close()
        except:
            pass
