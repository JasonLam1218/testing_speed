import time
import statistics
import logging
import json
from datetime import datetime
from src.edge_function_client import EdgeFunctionClient
from src.serverless_function_client import ServerlessFunctionClient
from src.socks5_client import SOCKS5Client
from src.streaming_metrics import StreamingMetrics
from tests.test_scenarios import TestScenarios
from config.settings import Config

class MultiDeploymentTestRunner:
    """
    Unified test orchestrator for running performance tests across
    Edge Functions, Serverless Functions, and SOCKS5 proxies.
    """
    
    def __init__(self, test_methods=None, regions=None, iterations=1, delay=8, 
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
            "test_info": {},
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
        
        # Initialize streaming metrics if needed
        self.streaming_metrics = StreamingMetrics() if test_mode in ["streaming", "both"] else None
        
        logging.info(f"Multi-deployment test runner initialized")
        logging.info(f"Methods: {', '.join(self.test_methods)}")
        logging.info(f"Test mode: {test_mode}")
    
    def run_comprehensive_tests(self, scenario_category):
        """
        Execute comprehensive testing across all deployment methods
        """
        start_time = datetime.now()
        
        # Test metadata
        self.results["test_info"] = {
            "start_time": start_time.isoformat(),
            "test_type": "Multi_Deployment_Analysis",
            "iterations": self.iterations,
            "delay_between_calls": self.delay,
            "test_mode": self.test_mode,
            "methods_tested": self.test_methods,
            "regions_tested": len(self.regions) if "socks5_proxy" in self.test_methods else 1
        }
        
        # Get scenarios
        if scenario_category == "all":
            scenarios = TestScenarios.get_all_scenarios()
        else:
            scenarios = TestScenarios.get_scenarios_by_category(scenario_category)
        
        self.results["test_info"]["scenarios_count"] = len(scenarios)
        
        logging.info(f"Starting comprehensive tests: {len(scenarios)} scenarios × {len(self.test_methods)} methods")
        
        # Test each deployment method
        for method in self.test_methods:
            logging.info(f"Testing deployment method: {method}")
            
            if method == "edge_function":
                results = self._test_edge_function(scenarios)
            elif method == "serverless_function":
                results = self._test_serverless_function(scenarios)
            elif method == "socks5_proxy":
                results = self._test_socks5_proxy(scenarios)
            else:
                logging.warning(f"Unknown deployment method: {method}")
                continue
            
            self.results["deployments"][method] = results
            
            # Brief pause between deployment methods
            if method != self.test_methods[-1]:
                time.sleep(self.delay)
        
        # Calculate global statistics and recommendations
        end_time = datetime.now()
        self.results["test_info"]["end_time"] = end_time.isoformat()
        self.results["test_info"]["duration"] = (end_time - start_time).total_seconds()
        
        self._calculate_global_stats()
        self._generate_recommendations()
        
        # Save results
        self._save_results()
        
        return self.results
    
    def _test_edge_function(self, scenarios):
        """Test Edge Function deployment"""
        client = EdgeFunctionClient()
        
        if not client.test_connection():
            return {
                "connection_status": "failed",
                "summary": {"success_rate": 0.0},
                "scenarios": {},
                "errors": {"connection": "Failed to connect to Edge Function"}
            }
        
        return self._run_deployment_tests(client, scenarios, "edge_function")
    
    def _test_serverless_function(self, scenarios):
        """Test Serverless Function deployment"""
        client = ServerlessFunctionClient()
        
        if not client.test_connection():
            return {
                "connection_status": "failed",
                "summary": {"success_rate": 0.0},
                "scenarios": {},
                "errors": {"connection": "Failed to connect to Serverless Function"}
            }
        
        return self._run_deployment_tests(client, scenarios, "serverless_function")
    
    def _test_socks5_proxy(self, scenarios):
        """Test SOCKS5 proxy deployment across regions"""
        regional_results = {}
        all_response_times = []
        successful_scenarios = 0
        total_scenarios = len(scenarios) * len(self.regions)
        
        for region in self.regions:
            logging.info(f"Testing SOCKS5 region: {region}")
            client = SOCKS5Client(region)
            
            if not client.test_connection():
                regional_results[region] = {
                    "connection_status": "failed",
                    "scenarios": {},
                    "errors": {"connection": "Failed to connect"}
                }
                continue
            
            region_result = self._run_deployment_tests(client, scenarios, f"socks5_{region}")
            regional_results[region] = region_result
            
            # Aggregate regional data
            if region_result.get("summary", {}).get("avg_response_time"):
                all_response_times.extend(region_result["response_times"])
                successful_scenarios += region_result["summary"]["successful_scenarios"]
        
        # Calculate overall SOCKS5 summary
        summary = {}
        if all_response_times:
            summary = {
                "avg_response_time": statistics.mean(all_response_times),
                "min_response_time": min(all_response_times),
                "max_response_time": max(all_response_times),
                "std_response_time": statistics.stdev(all_response_times) if len(all_response_times) > 1 else 0.0,
                "success_rate": successful_scenarios / total_scenarios,
                "successful_scenarios": successful_scenarios,
                "total_scenarios": total_scenarios,
                "regions_tested": len([r for r in regional_results.values() if r.get("connection_status") == "connected"])
            }
        else:
            summary = {"success_rate": 0.0, "total_scenarios": total_scenarios}
        
        return {
            "connection_status": "connected" if any(r.get("connection_status") == "connected" for r in regional_results.values()) else "failed",
            "summary": summary,
            "regional_results": regional_results,
            "response_times": all_response_times
        }
    
    def _run_deployment_tests(self, client, scenarios, method_name):
        """
        Run tests for a specific deployment method
        """
        response_times = []
        successful_scenarios = 0
        scenario_results = {}
        errors = {}
        
        for scenario in scenarios:
            logging.info(f"[{method_name}] Testing scenario: {scenario['name']}")
            
            scenario_times = []
            scenario_errors = []
            
            for iteration in range(self.iterations):
                if self.test_mode == "streaming" and hasattr(client, 'measure_streaming_performance'):
                    result = client.measure_streaming_performance(scenario["prompt"])
                else:
                    result = client.generate_content(scenario["prompt"])
                
                if result["success"]:
                    response_time = result.get("total_time", result.get("time"))
                    scenario_times.append(response_time)
                    response_times.append(response_time)
                    
                    if self.save_raw:
                        # Store raw response for analysis
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
                scenario_stats = {
                    "avg_time": statistics.mean(scenario_times),
                    "min_time": min(scenario_times),
                    "max_time": max(scenario_times),
                    "std_time": statistics.stdev(scenario_times) if len(scenario_times) > 1 else 0.0,
                    "success_rate": len(scenario_times) / self.iterations,
                    "iterations_successful": len(scenario_times),
                    "iterations_failed": len(scenario_errors)
                }
            else:
                scenario_stats = {
                    "avg_time": None,
                    "success_rate": 0.0,
                    "iterations_successful": 0,
                    "iterations_failed": len(scenario_errors)
                }
            
            scenario_results[scenario["name"]] = scenario_stats
            
            if scenario_errors:
                errors[scenario["name"]] = scenario_errors
            
            # Brief pause between scenarios
            time.sleep(self.delay / 2)
        
        # Calculate deployment summary
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
                "total_measurements": len(response_times)
            }
        else:
            summary = {
                "success_rate": 0.0,
                "total_scenarios": len(scenarios)
            }
        
        # Add client stats if available
        if hasattr(client, 'get_stats'):
            summary.update(client.get_stats())
        
        return {
            "connection_status": "connected",
            "summary": summary,
            "scenarios": scenario_results,
            "errors": errors,
            "response_times": response_times
        }
    
    def _calculate_global_stats(self):
        """Calculate global statistics across all deployment methods"""
        all_response_times = []
        method_averages = {}
        
        for method, data in self.results["deployments"].items():
            if data.get("response_times"):
                times = data["response_times"]
                all_response_times.extend(times)
                method_averages[method] = statistics.mean(times)
        
        if all_response_times:
            self.results["global_stats"] = {
                "total_measurements": len(all_response_times),
                "global_avg_response_time": statistics.mean(all_response_times),
                "global_min_response_time": min(all_response_times),
                "global_max_response_time": max(all_response_times),
                "global_std_response_time": statistics.stdev(all_response_times),
                "fastest_method": min(method_averages.items(), key=lambda x: x[1])[0] if method_averages else None,
                "slowest_method": max(method_averages.items(), key=lambda x: x[1])[0] if method_averages else None,
                "performance_range": max(method_averages.values()) - min(method_averages.values()) if method_averages else 0,
                "methods_tested": len(method_averages)
            }
        else:
            self.results["global_stats"] = {
                "total_measurements": 0,
                "methods_tested": len(self.test_methods)
            }
    
    def _generate_recommendations(self):
        """Generate deployment recommendations based on test results"""
        recommendations = {}
        method_performance = {}
        
        # Collect performance data
        for method, data in self.results["deployments"].items():
            summary = data.get("summary", {})
            if summary.get("avg_response_time") and summary.get("success_rate", 0) > 0.5:
                method_performance[method] = {
                    "avg_time": summary["avg_response_time"],
                    "success_rate": summary["success_rate"],
                    "score": summary["success_rate"] / summary["avg_response_time"]  # Higher is better
                }
        
        if method_performance:
            # Primary recommendation (best overall score)
            primary = max(method_performance.items(), key=lambda x: x[1]["score"])
            recommendations["primary_deployment"] = {
                "method": primary[0],
                "avg_time": primary[1]["avg_time"],
                "success_rate": primary[1]["success_rate"],
                "reasoning": "Best balance of speed and reliability"
            }
            
            # Fastest deployment
            fastest = min(method_performance.items(), key=lambda x: x[1]["avg_time"])
            recommendations["fastest_deployment"] = {
                "method": fastest[0],
                "avg_time": fastest[1]["avg_time"],
                "success_rate": fastest[1]["success_rate"]
            }
            
            # Most reliable deployment
            most_reliable = max(method_performance.items(), key=lambda x: x[1]["success_rate"])
            recommendations["most_reliable"] = {
                "method": most_reliable[0],
                "avg_time": most_reliable[1]["avg_time"],
                "success_rate": most_reliable[1]["success_rate"]
            }
            
            # Use case recommendations
            recommendations["use_cases"] = {
                "simple_prompts": fastest[0] if fastest[1]["avg_time"] < Config.GOOD_THRESHOLD else primary[0],
                "complex_prompts": most_reliable[0] if most_reliable[1]["success_rate"] > 0.95 else primary[0],
                "production_workload": primary[0]
            }
        
        self.results["recommendations"] = recommendations
    
    def _save_results(self):
        """Save comprehensive results to file"""
        filename = f"{Config.RESULTS_DIR}/multi_deployment_results_{datetime.now():%Y%m%d_%H%M%S}.json"
        
        with open(filename, "w") as f:
            json.dump(self.results, f, indent=2, default=str)
        
        logging.info(f"Results saved to: {filename}")
        return filename
