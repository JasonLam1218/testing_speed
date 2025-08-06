import time
import statistics
import logging
from typing import List, Dict, Any

class StreamingMetrics:
    """
    Advanced streaming performance metrics collection and analysis.
    Captures user-perceived performance beyond traditional response times.
    """
    
    def __init__(self):
        self.metrics_history = []
        self.chunk_timings = []
        
    def measure_streaming_response(self, response_iterator, start_time: float):
        """
        Measure streaming performance metrics from response iterator
        """
        metrics = {
            "start_time": start_time,
            "first_byte_time": None,
            "chunks": [],
            "character_timings": [],
            "total_characters": 0,
            "total_chunks": 0,
            "end_time": None
        }
        
        character_count = 0
        chunk_count = 0
        
        try:
            for chunk in response_iterator:
                current_time = time.perf_counter()
                
                # Record first byte timing
                if metrics["first_byte_time"] is None:
                    metrics["first_byte_time"] = current_time
                
                # Process chunk
                chunk_size = len(chunk)
                chunk_text = chunk.decode('utf-8') if isinstance(chunk, bytes) else str(chunk)
                chunk_chars = len(chunk_text)
                
                # Record chunk metrics
                chunk_metrics = {
                    "timestamp": current_time,
                    "size_bytes": chunk_size,
                    "character_count": chunk_chars,
                    "cumulative_chars": character_count + chunk_chars,
                    "chunk_index": chunk_count
                }
                
                metrics["chunks"].append(chunk_metrics)
                
                # Record character-level timing
                for i, char in enumerate(chunk_text):
                    character_count += 1
                    metrics["character_timings"].append({
                        "char_index": character_count,
                        "timestamp": current_time + (i / len(chunk_text)) * 0.001,  # Estimated character timing
                        "character": char
                    })
                
                chunk_count += 1
            
            metrics["end_time"] = time.perf_counter()
            metrics["total_characters"] = character_count
            metrics["total_chunks"] = chunk_count
            
        except Exception as e:
            logging.error(f"Streaming metrics collection error: {e}")
            metrics["error"] = str(e)
        
        return self._calculate_streaming_metrics(metrics)
    
    def _calculate_streaming_metrics(self, raw_metrics):
        """Calculate advanced streaming performance metrics"""
        
        # Extract values from raw_metrics dictionary
        start_time = raw_metrics["start_time"]
        end_time = raw_metrics["end_time"]
        first_byte_time = raw_metrics["first_byte_time"]
        total_chars = raw_metrics["total_characters"]
        total_chunks = raw_metrics["total_chunks"]
        chunks = raw_metrics["chunks"]
        
        # Handle case where first_byte_time might be None
        if first_byte_time is None:
            first_byte_time = start_time
        
        # Basic timing metrics
        total_time = end_time - start_time
        time_to_first_byte = first_byte_time - start_time
        streaming_time = end_time - first_byte_time
        
        # Character generation metrics
        chars_per_second = total_chars / total_time if total_time > 0 else 0
        chars_per_second_streaming = total_chars / streaming_time if streaming_time > 0 else 0
        
        # Streaming consistency metrics
        chunk_intervals = []
        if len(chunks) > 1:  # Add safety check
            for i in range(1, len(chunks)):
                interval = chunks[i]["timestamp"] - chunks[i-1]["timestamp"]
                chunk_intervals.append(interval)
        
        avg_chunk_interval = statistics.mean(chunk_intervals) if chunk_intervals else 0
        chunk_interval_std = statistics.stdev(chunk_intervals) if len(chunk_intervals) > 1 else 0
        streaming_consistency = 1.0 / (1.0 + chunk_interval_std) if chunk_interval_std > 0 else 1.0
        
        # User-perceived metrics
        perceived_responsiveness = self._calculate_perceived_responsiveness(
            time_to_first_byte, chars_per_second_streaming, streaming_consistency
        )
        
        return {
            "timing": {
                "total_time": total_time,
                "time_to_first_byte": time_to_first_byte,     # 📊 TTFB
                "streaming_time": streaming_time,
                "ttfb_percentage": (time_to_first_byte / total_time) * 100 if total_time > 0 else 0
            },
            "generation": {
                "total_characters": total_chars,
                "chars_per_second_overall": chars_per_second,
                "chars_per_second_streaming": chars_per_second_streaming
            },
            "streaming": {
                "total_chunks": total_chunks,
                "avg_chunk_interval": avg_chunk_interval,
                "streaming_consistency": streaming_consistency
            },
            "user_experience": {
                "perceived_responsiveness": perceived_responsiveness,
                "quality_score": self._calculate_quality_score(time_to_first_byte, chars_per_second, streaming_consistency)
            }
        }
    
    def _calculate_perceived_responsiveness(self, ttfb: float, streaming_rate: float, consistency: float) -> float:
        """
        Calculate user-perceived responsiveness score (0-1, higher is better)
        """
        # TTFB component (faster is better)
        ttfb_score = max(0, 1 - (ttfb / 5.0))  # Normalize to 5 seconds max
        
        # Streaming rate component (faster is better)
        rate_score = min(1.0, streaming_rate / 50.0)  # Normalize to 50 chars/sec
        
        # Consistency component (smoother is better)
        consistency_score = consistency
        
        # Weighted combination
        responsiveness = (
            ttfb_score * 0.4 +      # 40% weight on first response
            rate_score * 0.35 +      # 35% weight on generation speed
            consistency_score * 0.25  # 25% weight on smoothness
        )
        
        return max(0, min(1, responsiveness))
    
    def _calculate_quality_score(self, ttfb: float, chars_per_sec: float, consistency: float) -> float:
        """
        Calculate overall quality score for streaming performance
        """
        # Performance thresholds
        excellent_ttfb = 1.0
        good_ttfb = 3.0
        excellent_rate = 40.0
        good_rate = 20.0
        
        # TTFB quality
        if ttfb <= excellent_ttfb:
            ttfb_quality = 1.0
        elif ttfb <= good_ttfb:
            ttfb_quality = 0.7
        else:
            ttfb_quality = max(0.1, 0.7 - (ttfb - good_ttfb) * 0.1)
        
        # Rate quality
        if chars_per_sec >= excellent_rate:
            rate_quality = 1.0
        elif chars_per_sec >= good_rate:
            rate_quality = 0.7
        else:
            rate_quality = max(0.1, chars_per_sec / good_rate * 0.7)
        
        # Combined quality score
        quality = (ttfb_quality * 0.4 + rate_quality * 0.4 + consistency * 0.2)
        return max(0, min(1, quality))
    
    def analyze_historical_performance(self) -> Dict[str, Any]:
        """
        Analyze historical streaming performance data
        """
        if not self.metrics_history:
            return {"error": "No historical data available"}
        
        # Extract key metrics
        ttfb_values = [m["timing"]["time_to_first_byte"] for m in self.metrics_history if m["success"]]
        streaming_rates = [m["generation"]["chars_per_second_streaming"] for m in self.metrics_history if m["success"]]
        quality_scores = [m["user_experience"]["quality_score"] for m in self.metrics_history if m["success"]]
        
        if not ttfb_values:
            return {"error": "No successful measurements in history"}
        
        analysis = {
            "measurements_count": len(ttfb_values),
            "time_to_first_byte": {
                "avg": statistics.mean(ttfb_values),
                "min": min(ttfb_values),
                "max": max(ttfb_values),
                "std": statistics.stdev(ttfb_values) if len(ttfb_values) > 1 else 0
            },
            "streaming_rate": {
                "avg": statistics.mean(streaming_rates),
                "min": min(streaming_rates),
                "max": max(streaming_rates),
                "std": statistics.stdev(streaming_rates) if len(streaming_rates) > 1 else 0
            },
            "quality": {
                "avg": statistics.mean(quality_scores),
                "min": min(quality_scores),
                "max": max(quality_scores),
                "std": statistics.stdev(quality_scores) if len(quality_scores) > 1 else 0
            }
        }
        
        # Performance trends
        if len(ttfb_values) >= 3:
            # Simple trend analysis (improving/degrading)
            recent_third = ttfb_values[-len(ttfb_values)//3:]
            early_third = ttfb_values[:len(ttfb_values)//3]
            
            if statistics.mean(recent_third) < statistics.mean(early_third):
                analysis["trend"] = "improving"
            elif statistics.mean(recent_third) > statistics.mean(early_third):
                analysis["trend"] = "degrading"
            else:
                analysis["trend"] = "stable"
        
        return analysis
    
    def get_real_time_metrics(self, window_size: int = 10) -> Dict[str, Any]:
        """
        Get real-time streaming metrics for last N measurements
        """
        if len(self.metrics_history) < window_size:
            window_size = len(self.metrics_history)
        
        if window_size == 0:
            return {"error": "No metrics available"}
        
        recent_metrics = self.metrics_history[-window_size:]
        successful_metrics = [m for m in recent_metrics if m["success"]]
        
        if not successful_metrics:
            return {"error": "No successful measurements in window"}
        
        # Calculate real-time averages
        avg_ttfb = statistics.mean([m["timing"]["time_to_first_byte"] for m in successful_metrics])
        avg_rate = statistics.mean([m["generation"]["chars_per_second_streaming"] for m in successful_metrics])
        avg_quality = statistics.mean([m["user_experience"]["quality_score"] for m in successful_metrics])
        
        return {
            "window_size": len(successful_metrics),
            "avg_time_to_first_byte": avg_ttfb,
            "avg_streaming_rate": avg_rate,
            "avg_quality_score": avg_quality,
            "status": "excellent" if avg_quality > 0.8 else "good" if avg_quality > 0.6 else "poor"
        }
