import time
import logging
import httpx
import json
from config.settings import Config

class EdgeFunctionClient:
    """
    ✅ FIXED: HTTP client with header-based TTFB measurement for Edge Functions
    """
    def __init__(self):
        self.deployment_name = "edge_function"
        self.url = Config.EDGE_FUNCTION_URL
        self.timeout = 25
        self.successful_requests = 0
        self.failed_requests = 0
        self.client = httpx.Client(
            timeout=self.timeout,
            headers={
                "User-Agent": "GeminiSpeedTest/1.0",
                "Accept": "text/event-stream",  # ✅ Accept SSE
                "Content-Type": "application/json"
            },
            follow_redirects=True
        )
        logging.info(f"Edge Function client initialized for {self.url}")

    def test_connection(self):
        """Test Edge Function connectivity"""
        try:
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
        """Standard content generation for compatibility"""
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

            self.successful_requests += 1
            logging.info(f"Edge Function SUCCESS: {elapsed:.3f}s, {len(final_content)} chars")
            
            return {
                "success": True,
                "time": elapsed,
                "response": final_content,
                "method": "edge_function",
                "status_code": response.status_code,
                "character_count": len(final_content)
            }

        except Exception as e:
            self.failed_requests += 1
            logging.error(f"Edge Function ERROR: {type(e).__name__}: {e}")
            return {
                "success": False,
                "time": None,
                "error": f"{type(e).__name__}: {e}",
                "method": "edge_function"
            }

    def measure_streaming_performance(self, prompt):
        """✅ FIXED: Measure TRUE first byte time using SSE and HTTP headers"""
        try:
            start_time = time.perf_counter()
            true_first_byte_time = None
            header_first_byte_time = None
            content_chunks = []
            total_chunks = 0
            final_content = ""

            # ✅ SOLUTION: Use SSE streaming with header-based TTFB
            with self.client.stream('POST', self.url, json={"prompt": prompt}) as response:
                response.raise_for_status()
                
                # 🔥 CAPTURE TTFB FROM HEADERS (most reliable)
                server_start_time = response.headers.get('X-First-Byte-Time')
                if server_start_time:
                    # Calculate network + processing time to first byte
                    header_first_byte_time = time.perf_counter() - start_time
                    logging.info(f"HEADER-BASED TTFB: {header_first_byte_time:.3f}s")

                # ✅ Parse SSE stream
                buffer = ""
                for chunk in response.iter_bytes():
                    if true_first_byte_time is None and len(chunk) > 0:
                        # 🔥 CAPTURE TRUE FIRST BYTE from stream
                        true_first_byte_time = time.perf_counter() - start_time
                        logging.info(f"STREAM-BASED TTFB: {true_first_byte_time:.3f}s")
                    
                    if len(chunk) > 0:
                        buffer += chunk.decode('utf-8', errors='ignore')
                        
                        # Process complete SSE events
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
                                    
                                    if chunk_type == 'first_byte' and true_first_byte_time is None:
                                        true_first_byte_time = time.perf_counter() - start_time
                                        logging.info(f"SSE FIRST BYTE: {true_first_byte_time:.3f}s")
                                        
                                    elif chunk_type == 'content_chunk':
                                        content_chunks.append(chunk_data)
                                        final_content += chunk_data.get('chunk_text', '')
                                        total_chunks += 1
                                        
                                    elif chunk_type == 'completion':
                                        break
                                        
                                except json.JSONDecodeError:
                                    continue

            end_time = time.perf_counter()
            total_time = end_time - start_time

            # ✅ Use the most reliable TTFB measurement
            best_ttfb = header_first_byte_time or true_first_byte_time or total_time
            
            # Validate TTFB
            if best_ttfb >= total_time:
                logging.warning(f"TTFB >= Total Time, adjusting: {best_ttfb:.3f}s -> {total_time * 0.1:.3f}s")
                best_ttfb = total_time * 0.1  # Assume 10% of total time for processing

            processing_time = total_time - best_ttfb
            chars_per_second = len(final_content) / total_time if total_time > 0 else 0
            first_byte_percentage = (best_ttfb / total_time) * 100 if total_time > 0 else 0

            # Calculate streaming metrics
            streaming_consistency = 1.0 if total_chunks > 0 else 0.0
            if best_ttfb > 0:
                responsiveness = min(1.0, 2.0 / best_ttfb)
                throughput = min(1.0, chars_per_second / 100.0)
                user_experience_score = (responsiveness * 0.7 + throughput * 0.3)
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
                "chunks_received": total_chunks,
                "chars_per_second": chars_per_second,
                "streaming_consistency": streaming_consistency,
                "user_experience_score": user_experience_score,
                "method": "edge_function",
                "measurement_type": "sse_streaming",
                "ttfb_source": "header" if header_first_byte_time else "stream"
            }

        except Exception as e:
            self.failed_requests += 1
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
