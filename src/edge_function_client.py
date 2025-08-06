import time
import logging
import httpx
import json
from config.settings import Config

class EdgeFunctionClient:
    """
    HTTP client for testing Vercel Edge Functions with Gemini API.
    Optimized for edge computing with minimal latency measurements.
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
        Measure streaming performance metrics for edge functions
        FIXED VERSION - Includes all required streaming metrics
        """
        try:
            # Track streaming metrics
            start_time = time.perf_counter()
            first_byte_time = None
            chunks_received = 0
            total_bytes = 0
            
            with self.client.stream('POST', self.url, json={"prompt": prompt}) as response:
                response.raise_for_status()
                content = b""
                
                for chunk in response.iter_bytes():
                    if first_byte_time is None:
                        first_byte_time = time.perf_counter()  # 📊 TTFB captured here
                    
                    content += chunk
                    chunks_received += 1
                    total_bytes += len(chunk)
            
            end_time = time.perf_counter()
            
            # Calculate comprehensive metrics
            total_time = end_time - start_time
            ttfb = first_byte_time - start_time if first_byte_time else total_time
            processing_time = end_time - first_byte_time if first_byte_time else 0
            
            # Parse final response
            result = json.loads(content.decode('utf-8'))
            text = result.get("response", result.get("text", ""))
            
            # ✅ Calculate streaming consistency
            streaming_consistency = 1.0 if chunks_received > 0 else 0.0
            if chunks_received > 1:
                # Simple consistency metric based on chunk distribution
                avg_chunk_size = total_bytes / chunks_received if chunks_received > 0 else 0
                chunk_variance = abs(len(text) / chunks_received - avg_chunk_size) if chunks_received > 0 else 0
                streaming_consistency = max(0.0, 1.0 - (chunk_variance / avg_chunk_size)) if avg_chunk_size > 0 else 1.0
            
            # ✅ Calculate user experience score
            user_experience_score = 0.5  # Default moderate score
            if total_time > 0 and len(text) > 0:
                responsiveness = min(1.0, 5.0 / ttfb) if ttfb > 0 else 0.5
                throughput = min(1.0, (len(text) / total_time) / 100.0)
                user_experience_score = (responsiveness * 0.6 + throughput * 0.4)

            return {
                "success": True,
                "total_time": total_time,  # 📈 Total response time
                "ttfb": ttfb,  # ⚡ Time To First Byte
                "processing_time": processing_time,  # 🔄 Post-TTFB processing
                "response": text,
                "character_count": len(text),
                "chunks_received": chunks_received,
                "total_bytes": total_bytes,
                "chars_per_second": len(text) / total_time if total_time > 0 else 0,
                "streaming_consistency": streaming_consistency,  # ✅ Add this
                "user_experience_score": user_experience_score,  # ✅ Add this
                "method": "edge_function",
                "measurement_type": "streaming"
            }
            
        except Exception as e:
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
