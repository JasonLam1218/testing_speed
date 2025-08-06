import time
import statistics
import logging
import json
from datetime import datetime
from src.edge_function_client import EdgeFunctionClient
from src.serverless_function_client import ServerlessFunctionClient
from src.socks5_client import SOCKS5Client
from tests.test_scenarios import TestScenarios
from config.settings import Config

class MultiDeploymentTestRunner:
    """
    Unified test runner for comprehensive multi-deployment performance analysis.
    Supports Edge Functions, Serverless Functions, and SOCKS5 proxies.
    """
    
    def __init__(self, test_methods=None, regions=None, iterations=1, delay=1, 
                 test_mode="total", save_raw=False, verbose=False):
        self.test_methods = test_methods or Config.DEPLOYMENT_METHODS
        self.regions = regions or Config.NORDVPN_REGIONS
        self.iterations = iterations
        self.delay = delay
        self.test_mode = test_mode
        self.save_raw = save_raw
        self.verbose = verbose
        
        # Results structure
        self.results = {
            "test_info": {
                "start_time": datetime.now().isoformat(),
                "methods_tested": self.test_methods,
                "test_mode": self.test_mode,
                "iterations": self.iterations,
                "regions": self.regions if "socks5_proxy" in self.test_methods else None
            },
            "deployments": {},
            "global_stats": {},
            "recommendations": {}
        }
        
        # Configure logging
        log_filename = f"{Config.RESULTS_DIR}/multi_deployment_{datetime.now():%Y%m%d_%H%M%S}.log"
        logging.basicConfig(
            level=logging.DEBUG if verbose else logging.INFO,
            handlers=[
                logging.FileHandler(log_filename),
                logging.StreamHandler()
            ],
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
        logging.info("Multi-deployment test runner initialized")
        logging.info(f"Methods: {', '.join(self.test_methods)}")
        logging.info(f"Test mode: {self.test_mode}")
        logging.info(f"Starting comprehensive tests: {len(TestScenarios.get_all_scenarios())} scenarios × {len(self.test_methods)} methods")

    def run_comprehensive_tests(self, scenario_category):
        """Run comprehensive tests across all deployment methods"""
        start_time = time.time()
        
        # Get scenarios
        if scenario_category == "all":
            scenarios = TestScenarios.get_all_scenarios()
        else:
            scenarios = TestScenarios.get_scenarios_by_category(scenario_category)
        
        self.results["test_info"]["scenarios_count"] = len(scenarios)
        
        # Test each deployment method
        for method in self.test_methods:
            logging.info(f"Testing deployment method: {method}")
            
            if method == "edge_function":
                self.results["deployments"]["edge_function"] = self._test_edge_function(scenarios)
            elif method == "serverless_function":
                self.results["deployments"]["serverless_function"] = self._test_serverless_function(scenarios)
            elif method == "socks5_proxy":
                self.results["deployments"]["socks5_proxy"] = self._test_socks5_proxy(scenarios)
        
        # Calculate global statistics and recommendations
        end_time = time.time()
        self.results["test_info"]["end_time"] = datetime.now().isoformat()
        self.results["test_info"]["duration"] = end_time - start_time
        
        self._calculate_global_statistics()
        self._generate_recommendations()
        
        # Save results
        results_filename = f"{Config.RESULTS_DIR}/multi_deployment_results_{datetime.now():%Y%m%d_%H%M%S}.json"
        with open(results_filename, "w") as f:
            json.dump(self.results, f, indent=2, default=str)
        
        logging.info(f"Comprehensive testing completed in {self.results['test_info']['duration']:.1f}s")
        return self.results

    def _test_edge_function(self, scenarios):
        """Test Edge Function deployment"""
        client = EdgeFunctionClient()
        if not client.test_connection():
            return {"connection_status": "failed", "error": "Connection test failed"}
        return self._run_deployment_tests(client, scenarios, "edge_function")

    def _test_serverless_function(self, scenarios):
        """Test Serverless Function deployment"""  
        client = ServerlessFunctionClient()
        if not client.test_connection():
            return {"connection_status": "failed", "error": "Connection test failed"}
        return self._run_deployment_tests(client, scenarios, "serverless_function")

    def _test_socks5_proxy(self, scenarios):
        """Test SOCKS5 proxy deployment across multiple regions"""
        regional_results = {}
        all_response_times = []
        all_ttfb_times = []
        successful_regions = 0
        
        for region in self.regions:
            logging.info(f"Testing SOCKS5 region: {region}")
            client = SOCKS5Client(region)
            
            if not client.test_connection():
                regional_results[region] = {
                    "connection_status": "failed",
                    "scenarios": {},
                    "errors": {},
                    "summary": {
                        "avg_response_time": None,
                        "success_rate": 0.0,
                        "total_measurements": 0
                    }
                }
                continue
                
            region_result = self._run_deployment_tests(client, scenarios, f"socks5_{region}")
            regional_results[region] = region_result
            
            if region_result.get("summary", {}).get("avg_response_time"):
                successful_regions += 1
                region_times = region_result.get("response_times", [])
                all_response_times.extend(region_times)
                
                # Add TTFB times if available
                region_ttfb = region_result.get("summary", {}).get("avg_ttfb")
                if region_ttfb:
                    all_ttfb_times.extend([region_ttfb] * len(region_times))
        
        # Aggregate SOCKS5 results
        if all_response_times:
            summary = {
                "avg_response_time": statistics.mean(all_response_times),
                "min_response_time": min(all_response_times),
                "max_response_time": max(all_response_times),
                "std_response_time": statistics.stdev(all_response_times) if len(all_response_times) > 1 else 0.0,
                "success_rate": successful_regions / len(self.regions),
                "total_measurements": len(all_response_times),
                "regions_tested": len(self.regions),
                "successful_regions": successful_regions
            }
            
            if all_ttfb_times:
                summary.update({
                    "avg_ttfb": statistics.mean(all_ttfb_times),
                    "min_ttfb": min(all_ttfb_times),
                    "max_ttfb": max(all_ttfb_times),
                    "std_ttfb": statistics.stdev(all_ttfb_times) if len(all_ttfb_times) > 1 else 0.0
                })
        else:
            summary = {
                "avg_response_time": None,
                "success_rate": 0.0,
                "total_measurements": 0,
                "regions_tested": len(self.regions),
                "successful_regions": 0
            }
        
        return {
            "connection_status": "connected" if successful_regions > 0 else "failed",
            "regional_results": regional_results,
            "summary": summary,
            "response_times": all_response_times
        }

    def _run_deployment_tests(self, client, scenarios, method_name):
        """
        Run tests for a specific deployment method with enhanced validation
        FIXED VERSION - Properly handles streaming data collection for all modes
        """
        response_times = []
        ttfb_times = []
        streaming_metrics_list = []
        scenario_streaming = []
        successful_scenarios = 0
        scenario_results = {}
        errors = {}

        for scenario in scenarios:
            logging.info(f"[{method_name}] Testing scenario: {scenario['name']}")
            scenario_times = []
            scenario_ttfb = []
            scenario_streaming_data = []
            scenario_errors = []

            for iteration in range(self.iterations):
                # Choose measurement method based on test_mode
                if self.test_mode == "streaming" and hasattr(client, 'measure_streaming_performance'):
                    result = client.measure_streaming_performance(scenario["prompt"])
                    if result["success"]:
                        streaming_metrics_list.append(result)
                        scenario_streaming_data.append(result)
                elif self.test_mode == "both":
                    # ✅ FIX: Run both streaming and total measurements
                    streaming_result = None
                    if hasattr(client, 'measure_streaming_performance'):
                        streaming_result = client.measure_streaming_performance(scenario["prompt"])
                        if streaming_result["success"]:
                            scenario_streaming.append(streaming_result)
                            streaming_metrics_list.append(streaming_result)
                            scenario_streaming_data.append(streaming_result)
                            ttfb_times.append(streaming_result.get("ttfb", 0))
                    
                    # Also run standard measurement
                    result = client.generate_content(scenario["prompt"])
                else:
                    result = client.generate_content(scenario["prompt"])

                # ✅ Baseline validation
                result = self._validate_performance_baseline(result, method_name, scenario["name"])

                if result["success"]:
                    # For streaming: use total_time, for standard: use time
                    response_time = result.get("total_time", result.get("time"))
                    scenario_times.append(response_time)
                    response_times.append(response_time)

                    # Store TTFB if available and not already stored
                    if "ttfb" in result and result["ttfb"] not in ttfb_times:
                        ttfb_times.append(result["ttfb"])
                        scenario_ttfb.append(result["ttfb"])

                    if self.save_raw:
                        result["scenario"] = scenario["name"]
                        result["iteration"] = iteration

                    logging.debug(f"[{method_name}] {scenario['name']} #{iteration + 1}: {response_time:.3f}s")
                else:
                    scenario_errors.append(result.get("error", "Unknown error"))
                    logging.warning(f"[{method_name}] {scenario['name']} #{iteration + 1} FAILED: {result.get('error')}")

                # Delay between iterations
                if iteration < self.iterations - 1:
                    time.sleep(self.delay)

            # Calculate scenario statistics
            if scenario_times:
                successful_scenarios += 1
                scenario_results[scenario["name"]] = {
                    "avg_time": statistics.mean(scenario_times),
                    "min_time": min(scenario_times),
                    "max_time": max(scenario_times),
                    "std_time": statistics.stdev(scenario_times) if len(scenario_times) > 1 else 0.0,
                    "success_rate": len(scenario_times) / self.iterations,
                    "iterations": len(scenario_times),
                    "category": scenario.get("category", "unknown")
                }
                
                # Add TTFB data if available
                if scenario_ttfb:
                    scenario_results[scenario["name"]].update({
                        "avg_ttfb": statistics.mean(scenario_ttfb),
                        "min_ttfb": min(scenario_ttfb),
                        "max_ttfb": max(scenario_ttfb)
                    })
                
                # Add streaming data if available
                if scenario_streaming_data:
                    scenario_results[scenario["name"]].update({
                        "streaming_data": scenario_streaming_data,
                        "avg_chars_per_second": statistics.mean([s.get("chars_per_second", 0) for s in scenario_streaming_data]),
                        "streaming_consistency": statistics.mean([s.get("streaming_consistency", 1.0) for s in scenario_streaming_data])
                    })
            else:
                scenario_results[scenario["name"]] = {
                    "avg_time": None,
                    "success_rate": 0.0,
                    "iterations": 0,
                    "category": scenario.get("category", "unknown")
                }

            if scenario_errors:
                errors[scenario["name"]] = scenario_errors

            # Brief delay between scenarios
            time.sleep(self.delay)

        # Calculate deployment summary with streaming metrics
        summary = {}
        if response_times:
            summary = {
                "avg_response_time": statistics.mean(response_times),
                "min_response_time": min(response_times),
                "max_response_time": max(response_times),
                "std_response_time": statistics.stdev(response_times) if len(response_times) > 1 else 0.0,
                "success_rate": successful_scenarios / len(scenarios),
                "successful_scenarios": successful_scenarios,
                "total_scenarios": len(scenarios),
                "total_measurements": len(response_times),
                "method": method_name.split('_')[0] if '_' in method_name else method_name
            }

            # Add TTFB summary if available
            if ttfb_times:
                summary.update({
                    "avg_ttfb": statistics.mean(ttfb_times),
                    "min_ttfb": min(ttfb_times),
                    "max_ttfb": max(ttfb_times),
                    "std_ttfb": statistics.stdev(ttfb_times) if len(ttfb_times) > 1 else 0.0
                })

        # Add client stats if available
        if hasattr(client, 'get_stats'):
            client_stats = client.get_stats()
            summary.update(client_stats)

        result_data = {
            "connection_status": "connected",
            "summary": summary,
            "scenarios": scenario_results,
            "errors": errors,
            "response_times": response_times
        }

        # ✅ FIX: Add streaming metrics with proper error handling
        streaming_data_source = streaming_metrics_list if streaming_metrics_list else scenario_streaming
        
        if streaming_data_source:
            # Filter out None values and ensure we have valid data
            valid_streaming_data = [s for s in streaming_data_source if s and s.get("success")]
            
            if valid_streaming_data:
                # Helper function to safely calculate mean with fallback
                def safe_mean(values, fallback=0.0):
                    valid_values = [v for v in values if v is not None and isinstance(v, (int, float))]
                    return statistics.mean(valid_values) if valid_values else fallback
                
                # Add streaming metrics to each scenario that has streaming data
                for scenario_name, scenario_data in scenario_results.items():
                    if scenario_data.get("streaming_data"):
                        streaming_subset = scenario_data["streaming_data"]
                        scenario_data.update({
                            "streaming_metrics": {
                                "avg_ttfb": safe_mean([s.get("ttfb") for s in streaming_subset]),
                                "avg_chars_per_second": safe_mean([s.get("chars_per_second") for s in streaming_subset]),
                                "streaming_consistency": safe_mean([s.get("streaming_consistency") for s in streaming_subset], 1.0),
                                "user_experience_score": safe_mean([s.get("user_experience_score") for s in streaming_subset], 0.5)
                            }
                        })
                
                result_data["streaming_metrics"] = {
                    "measurements": valid_streaming_data,
                    "avg_ttfb": safe_mean([s.get("ttfb") for s in valid_streaming_data]),
                    "avg_chars_per_second": safe_mean([s.get("chars_per_second") for s in valid_streaming_data]),
                    "streaming_consistency": safe_mean([s.get("streaming_consistency") for s in valid_streaming_data], 1.0),
                    "user_experience_score": safe_mean([s.get("user_experience_score") for s in valid_streaming_data], 0.5)
                }

        return result_data

    def _validate_performance_baseline(self, result, method_name, scenario_name):
        """Validate performance results for realistic values"""
        if not result.get("success"):
            return result
            
        response_time = result.get("total_time", result.get("time"))
        
        if response_time is None:
            return result
            
        # Baseline validation
        if response_time < Config.BASELINE_MIN_RESPONSE_TIME:
            logging.warning(f"[{method_name}] {scenario_name}: Unusually fast response ({response_time:.3f}s)")
        elif response_time > Config.BASELINE_MAX_RESPONSE_TIME:
            logging.error(f"[{method_name}] {scenario_name}: Response exceeded maximum threshold ({response_time:.3f}s)")
            result["success"] = False
            result["error"] = f"Response time exceeded {Config.BASELINE_MAX_RESPONSE_TIME}s threshold"
        elif response_time > Config.BASELINE_WARNING_THRESHOLD:
            logging.warning(f"[{method_name}] {scenario_name}: Slow response detected ({response_time:.3f}s)")
            
        return result

    def _calculate_global_statistics(self):
        """Calculate global performance statistics"""
        all_times = []
        method_averages = {}
        
        for method, data in self.results["deployments"].items():
            summary = data.get("summary", {})
            if summary.get("avg_response_time"):
                method_averages[method] = summary["avg_response_time"]
                times = data.get("response_times", [])
                all_times.extend(times)
        
        if all_times:
            self.results["global_stats"] = {
                "global_avg_response_time": statistics.mean(all_times),
                "global_min_response_time": min(all_times),
                "global_max_response_time": max(all_times),
                "global_std_response_time": statistics.stdev(all_times) if len(all_times) > 1 else 0.0,
                "methods_tested": len(method_averages),
                "total_measurements": len(all_times),
                "performance_range": max(method_averages.values()) - min(method_averages.values()) if method_averages else 0
            }

    def _generate_recommendations(self):
        """Generate deployment recommendations based on test results"""
        method_rankings = []
        
        for method, data in self.results["deployments"].items():
            summary = data.get("summary", {})
            if summary.get("avg_response_time"):
                score = summary["success_rate"] / summary["avg_response_time"]
                method_rankings.append({
                    "method": method,
                    "avg_time": summary["avg_response_time"],
                    "success_rate": summary["success_rate"],
                    "score": score
                })
        
        # Sort by performance score (higher is better)
        method_rankings.sort(key=lambda x: x["score"], reverse=True)
        
        if method_rankings:
            primary = method_rankings[0]
            self.results["recommendations"]["primary_deployment"] = {
                "method": primary["method"],
                "avg_time": primary["avg_time"],
                "success_rate": primary["success_rate"],
                "reasoning": f"Best overall performance with {primary['avg_time']:.3f}s average response time and {primary['success_rate']:.1%} success rate"
            }
            
            # Fastest deployment
            fastest = min(method_rankings, key=lambda x: x["avg_time"])
            self.results["recommendations"]["fastest_deployment"] = {
                "method": fastest["method"],
                "avg_time": fastest["avg_time"],
                "success_rate": fastest["success_rate"]
            }
            
            # Most reliable
            most_reliable = max(method_rankings, key=lambda x: x["success_rate"])
            self.results["recommendations"]["most_reliable"] = {
                "method": most_reliable["method"],
                "avg_time": most_reliable["avg_time"],
                "success_rate": most_reliable["success_rate"]
            }
