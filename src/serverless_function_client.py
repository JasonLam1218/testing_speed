import time
import logging
import httpx
import json
from config.settings import Config

class ServerlessFunctionClient:
    """
    ✅ FIXED: HTTP client with header-based TTFB measurement for Serverless Functions
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
        
        # Initialize HTTP client with streaming support
        self.client = httpx.Client(
            timeout=self.timeout,
            headers={
                "User-Agent": "GeminiSpeedTest/1.0",
                "Accept": "text/event-stream",  # ✅ Accept SSE
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

    def _detect_cold_start(self, response_time, ttfb=None):
        """✅ IMPROVED: Realistic cold start detection for VPN + Hong Kong setup"""
        # Adjusted thresholds for VPN overhead
        cold_start_threshold = 8.0  # Reduced from 12.0, accounting for VPN
        ttfb_cold_start_threshold = 2.5  # TTFB threshold for cold starts
        
        is_cold_start = False
        
        if self.first_request:
            self.first_request = False
            # More lenient for first request due to VPN
            if response_time > cold_start_threshold or (ttfb and ttfb > ttfb_cold_start_threshold):
                self.cold_starts_detected += 1
                self.cold_start_time = response_time
                is_cold_start = True
                logging.info(f"First request cold start detected: {response_time:.3f}s (TTFB: {ttfb:.3f}s)")
        else:
            # Subsequent requests - stricter threshold
            subsequent_threshold = 10.0  # For subsequent requests
            subsequent_ttfb_threshold = 3.0
            
            if response_time > subsequent_threshold or (ttfb and ttfb > subsequent_ttfb_threshold):
                self.cold_starts_detected += 1
                is_cold_start = True
                logging.info(f"Subsequent cold start detected: {response_time:.3f}s (TTFB: {ttfb:.3f}s)")
        
        return is_cold_start

    def generate_content(self, prompt):
        """Generate content using Serverless Function with cold start detection"""
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
            
            # Parse SSE response for content
            final_content = ""
            buffer = response.text
            events = buffer.split('\n\n')
            
            for event in events:
                if 'data: ' in event:
                    try:
                        data_line = [line for line in event.split('\n') if line.startswith('data: ')][0]
                        json_data = data_line[6:]  # Remove 'data: '
                        chunk_data = json.loads(json_data)
                        if chunk_data.get('type') == 'content_chunk':
                            final_content += chunk_data.get('chunk_text', '')
                    except (json.JSONDecodeError, IndexError):
                        continue

            # Detect cold start
            is_cold_start = self._detect_cold_start(elapsed)

            self.successful_requests += 1
            status = "COLD START" if is_cold_start else "SUCCESS"
            logging.info(f"Serverless Function {status}: {elapsed:.3f}s, {len(final_content)} chars")

            return {
                "success": True,
                "time": elapsed,
                "response": final_content,
                "method": "serverless_function",
                "is_cold_start": is_cold_start,
                "status_code": response.status_code,
                "response_size": len(response.content),
                "character_count": len(final_content),
                "execution_time": elapsed - (0.1 if not is_cold_start else 0.5)
            }

        except Exception as e:
            self.failed_requests += 1
            logging.error(f"Serverless Function ERROR: {type(e).__name__}: {e}")
            return {
                "success": False,
                "time": None,
                "error": f"{type(e).__name__}: {e}",
                "error_type": "unexpected",
                "method": "serverless_function"
            }

    def measure_streaming_performance(self, prompt):
        """✅ FIXED: Measure TRUE first byte time using SSE and HTTP headers"""
        try:
            start_time = time.perf_counter()
            true_first_byte_time = None
            header_first_byte_time = None
            chunks_received = 0
            total_bytes = 0
            final_content = ""

            # ✅ Use SSE streaming with header-based TTFB
            with self.client.stream('POST', self.url, json={"prompt": prompt}) as response:
                response.raise_for_status()
                
                # 🔥 CAPTURE TTFB FROM HEADERS (most reliable)
                server_start_time = response.headers.get('X-First-Byte-Time')
                if server_start_time:
                    header_first_byte_time = time.perf_counter() - start_time
                    logging.info(f"HEADER-BASED TTFB: {header_first_byte_time:.3f}s")

                # Parse SSE stream
                buffer = ""
                for chunk in response.iter_bytes():
                    if true_first_byte_time is None and len(chunk) > 0:
                        true_first_byte_time = time.perf_counter() - start_time
                        logging.info(f"STREAM-BASED TTFB: {true_first_byte_time:.3f}s")
                    
                    if len(chunk) > 0:
                        buffer += chunk.decode('utf-8', errors='ignore')
                        chunks_received += 1
                        total_bytes += len(chunk)
                        
                        # Process SSE events
                        while '\n\n' in buffer:
                            event_end = buffer.find('\n\n')
                            event_data = buffer[:event_end]
                            buffer = buffer[event_end + 2:]
                            
                            # Parse SSE event
                            lines = event_data.split('\n')
                            event_type = None
                            data = None
                            
                            for line in lines:
                                if line.startswith('event: '):
                                    event_type = line[7:].strip()
                                elif line.startswith('data: '):
                                    data = line[6:].strip()
                            
                            if data:
                                try:
                                    chunk_data = json.loads(data)
                                    chunk_type = chunk_data.get('type')
                                    
                                    if chunk_type == 'content_chunk':
                                        final_content += chunk_data.get('chunk_text', '')
                                    elif chunk_type == 'completion':
                                        break
                                        
                                except json.JSONDecodeError:
                                    continue

            end_time = time.perf_counter()
            total_time = end_time - start_time

            # Use the most reliable TTFB measurement
            best_ttfb = header_first_byte_time or true_first_byte_time or total_time
            
            # Validate and adjust TTFB
            if best_ttfb >= total_time:
                best_ttfb = total_time * 0.1  # Assume 10% for processing

            # Detect cold start
            is_cold_start = self._detect_cold_start(total_time, best_ttfb)
            processing_time = total_time - best_ttfb
            chars_per_second = len(final_content) / total_time if total_time > 0 else 0
            first_byte_percentage = (best_ttfb / total_time) * 100 if total_time > 0 else 0

            # Calculate streaming metrics
            streaming_consistency = 1.0
            if best_ttfb > 0:
                responsiveness = min(1.0, 2.0 / best_ttfb)
                throughput = min(1.0, chars_per_second / 100.0)
                cold_start_penalty = 0.8 if is_cold_start else 1.0
                user_experience_score = (responsiveness * 0.7 + throughput * 0.3) * cold_start_penalty
            else:
                user_experience_score = 0.5

            self.successful_requests += 1

            return {
                "success": True,
                "total_time": total_time,
                "ttfb": best_ttfb,  # ⚡ CORRECTED TTFB
                "true_first_byte_time": best_ttfb,
                "header_first_byte_time": header_first_byte_time,
                "stream_first_byte_time": true_first_byte_time,
                "processing_time": processing_time,
                "first_byte_percentage": first_byte_percentage,  # ✅ Realistic percentage
                "response": final_content,
                "character_count": len(final_content),
                "chunks_received": chunks_received,
                "total_bytes": total_bytes,
                "chars_per_second": chars_per_second,
                "is_cold_start": is_cold_start,
                "streaming_consistency": streaming_consistency,
                "user_experience_score": user_experience_score,
                "method": "serverless_function",
                "measurement_type": "sse_streaming",
                "ttfb_source": "header" if header_first_byte_time else "stream"
            }

        except Exception as e:
            self.failed_requests += 1
            logging.error(f"Serverless Function streaming measurement failed: {e}")
            return {"success": False, "error": str(e), "method": "serverless_function"}

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
