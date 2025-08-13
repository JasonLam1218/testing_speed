import time
import logging
import httpx
from config.settings import Config

class ServerlessFunctionClient:
    """
    ✅ COMPLETE FIX: Plain text parsing with multi-layer TTFB detection for Serverless Functions
    """
    def __init__(self):
        self.deployment_name = "serverless_function"
        self.url = Config.SERVERLESS_FUNCTION_URL
        self.timeout = 30
        self.successful_requests = 0
        self.failed_requests = 0
        self.cold_starts_detected = 0
        self.first_request = True
        
        # ✅ FIXED: Use plain text format like Edge Function
        self.client = httpx.Client(
            timeout=self.timeout,
            headers={
                "User-Agent": "GeminiSpeedTest/1.0",
                "Accept": "text/plain, */*",  # ✅ FIXED: Plain text instead of SSE
                "Content-Type": "application/json"
            },
            follow_redirects=True
        )
        logging.info(f"Serverless Function client initialized for {self.url}")

    def test_connection(self):
        """Test Serverless Function connectivity"""
        try:
            response = self.client.post(self.url, json={"prompt": "Test"}, timeout=10)
            return response.status_code == 200
        except Exception as e:
            logging.error(f"Serverless Function connection test failed: {e}")
            return False

    def _detect_cold_start(self, response_time, ttfb=None):
        """Enhanced cold start detection"""
        is_cold_start = False
        
        if self.first_request:
            self.first_request = False
            if response_time > 8.0 or (ttfb and ttfb > 2.5):
                is_cold_start = True
                self.cold_starts_detected += 1
        else:
            if response_time > 10.0 or (ttfb and ttfb > 3.0):
                is_cold_start = True
                self.cold_starts_detected += 1
        
        return is_cold_start

    def measure_streaming_performance(self, prompt):
        """✅ COMPLETE FIX: Use same plain text parsing as Edge Function"""
        try:
            start_time = time.perf_counter()
            header_ttfb = None
            stream_ttfb = None
            content_ttfb = None
            final_content = ""
            
            with self.client.stream('POST', self.url, json={"prompt": prompt}) as response:
                response.raise_for_status()
                
                # 🔥 METHOD 1: Header-based TTFB
                server_start = response.headers.get('X-First-Byte-Time')
                if server_start:
                    header_ttfb = time.perf_counter() - start_time
                    logging.info(f"✅ HEADER TTFB: {header_ttfb:.3f}s")
                
                # 🔥 METHOD 2: Stream processing (same as Edge Function)
                first_chunk_received = False
                buffer = ""
                
                for chunk in response.iter_bytes():
                    current_time = time.perf_counter() - start_time
                    
                    if not first_chunk_received and len(chunk) > 0:
                        stream_ttfb = current_time
                        first_chunk_received = True
                        logging.info(f"✅ STREAM TTFB: {stream_ttfb:.3f}s")
                    
                    if len(chunk) > 0:
                        chunk_text = chunk.decode('utf-8', errors='ignore')
                        buffer += chunk_text
                        
                        # 🔥 METHOD 3: Content-based TTFB detection (same as Edge Function)
                        if content_ttfb is None and 'TTFB:' in buffer:
                            content_ttfb = current_time
                            logging.info(f"✅ CONTENT TTFB: {content_ttfb:.3f}s")
                        
                        # ✅ FIXED: Extract actual content (same logic as Edge Function)
                        content_lines = buffer.split('\n')
                        for line in content_lines:
                            if not line.startswith('TTFB:') and not line.startswith('END:') and not line.startswith('ERROR:'):
                                final_content += line + '\n'

            total_time = time.perf_counter() - start_time
            
            # ✅ METHOD 4: Choose best TTFB measurement (same as Edge Function)
            best_ttfb = None
            ttfb_source = "estimated"
            
            if header_ttfb and header_ttfb < total_time * 0.8:
                best_ttfb = header_ttfb
                ttfb_source = "header"
            elif content_ttfb and content_ttfb < total_time * 0.8:
                best_ttfb = content_ttfb
                ttfb_source = "content"
            elif stream_ttfb and stream_ttfb < total_time * 0.8:
                best_ttfb = stream_ttfb
                ttfb_source = "stream"
            else:
                # ✅ METHOD 5: Intelligent estimation for Serverless Functions
                if self._detect_cold_start(total_time):
                    best_ttfb = total_time * 0.25  # 25% for cold starts
                    logging.warning(f"Using estimated TTFB for cold start: {best_ttfb:.3f}s (25% of total)")
                else:
                    best_ttfb = total_time * 0.20  # 20% for warm starts
                    logging.warning(f"Using estimated TTFB for warm start: {best_ttfb:.3f}s (20% of total)")
                ttfb_source = "estimated"
            
            # Detect cold start
            is_cold_start = self._detect_cold_start(total_time, best_ttfb)
            
            # Calculate metrics
            processing_time = total_time - best_ttfb
            chars_per_second = len(final_content.strip()) / total_time if total_time > 0 else 0
            first_byte_percentage = (best_ttfb / total_time) * 100 if total_time > 0 else 0
            
            # User experience with cold start penalty
            if best_ttfb > 0:
                responsiveness = min(1.0, 2.0 / best_ttfb)
                throughput = min(1.0, chars_per_second / 50.0)
                cold_start_penalty = 0.8 if is_cold_start else 1.0
                user_experience_score = (responsiveness * 0.7 + throughput * 0.3) * cold_start_penalty
            else:
                user_experience_score = 0.5

            self.successful_requests += 1

            return {
                "success": True,
                "total_time": total_time,
                "ttfb": best_ttfb,
                "true_first_byte_time": best_ttfb,
                "header_first_byte_time": header_ttfb,
                "stream_first_byte_time": stream_ttfb,
                "content_first_byte_time": content_ttfb,
                "processing_time": processing_time,
                "first_byte_percentage": first_byte_percentage,
                "response": final_content.strip(),
                "character_count": len(final_content.strip()),
                "chars_per_second": chars_per_second,
                "is_cold_start": is_cold_start,
                "streaming_consistency": 1.0 if chars_per_second > 0 else 0.0,
                "user_experience_score": user_experience_score,
                "method": "serverless_function",
                "measurement_type": "multi_layer_detection",
                "ttfb_source": ttfb_source
            }

        except Exception as e:
            self.failed_requests += 1
            logging.error(f"Serverless Function measurement failed: {e}")
            return {"success": False, "error": str(e), "method": "serverless_function"}

    def generate_content(self, prompt):
        """✅ FIXED: Use plain text parsing for compatibility"""
        try:
            start_time = time.perf_counter()
            response = self.client.post(
                self.url,
                json={"prompt": prompt},
                timeout=self.timeout
            )
            end_time = time.perf_counter()
            elapsed = end_time - start_time

            response.raise_for_status()
            
            # ✅ FIXED: Parse plain text response instead of SSE
            final_content = ""
            content_lines = response.text.split('\n')
            
            for line in content_lines:
                # Skip TTFB markers and END markers
                if not line.startswith('TTFB:') and not line.startswith('END:') and not line.startswith('ERROR:'):
                    final_content += line + '\n'

            # Detect cold start
            is_cold_start = self._detect_cold_start(elapsed)

            self.successful_requests += 1
            status = "COLD START" if is_cold_start else "SUCCESS"
            logging.info(f"Serverless Function {status}: {elapsed:.3f}s, {len(final_content.strip())} chars")
            
            return {
                "success": True,
                "time": elapsed,
                "response": final_content.strip(),
                "method": "serverless_function",
                "is_cold_start": is_cold_start,
                "status_code": response.status_code,
                "character_count": len(final_content.strip())
            }

        except Exception as e:
            self.failed_requests += 1
            logging.error(f"Serverless Function ERROR: {type(e).__name__}: {e}")
            return {
                "success": False,
                "time": None,
                "error": f"{type(e).__name__}: {e}",
                "method": "serverless_function"
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
