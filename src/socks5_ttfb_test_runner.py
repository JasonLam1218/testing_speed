import time
import statistics
import logging
import json
from datetime import datetime

from src.socks5_ttfb_client import SOCKS5TTFBClient
from tests.test_scenarios import TestScenarios
from config.settings import Config

class SOCKS5TTFBTestRunner:
    """
    Comprehensive TTFB test runner with statistical analysis and quality metrics.
    """
    
    def __init__(self):
        self.results = {
            "test_info": {},
            "regions": {},
            "global_stats": {}
        }
        
        # Configure detailed logging
        log_filename = f"{Config.RESULTS_DIR}/ttfb_detailed_{datetime.now():%Y%m%d_%H%M%S}.log"
        logging.basicConfig(
            level=logging.INFO,
            handlers=[
                logging.FileHandler(log_filename),
                logging.StreamHandler()
            ],
            format='%(asctime)s - %(levelname)s - [%(name)s] - %(message)s'
        )

    def run(self, scenario_category):
        """Execute comprehensive TTFB testing across regions and scenarios"""
        start_time = datetime.now()
        
        # Test metadata
        self.results["test_info"] = {
            "start_time": start_time.isoformat(),
            "test_type": "TTFB_Analysis",
            "iterations": Config.TEST_ITERATIONS,
            "delay_between_calls": Config.API_DELAY,
            "regions_tested": len(Config.NORDVPN_REGIONS),
            "measurement_focus": "Time To First Byte"
        }

        # Get test scenarios
        if scenario_category == "all":
            scenarios = TestScenarios.get_all_scenarios()
        else:
            scenarios = TestScenarios.get_scenarios_by_category(scenario_category)
        
        self.results["test_info"]["scenarios_count"] = len(scenarios)
        
        logging.info(f"Starting TTFB analysis: {len(scenarios)} scenarios × {len(Config.NORDVPN_REGIONS)} regions × {Config.TEST_ITERATIONS} iterations")

        # Global statistics tracking
        all_successful_ttfb = []
        all_successful_totals = []
        regional_performance = {}

        # Test each region
        for region_index, region in enumerate(Config.NORDVPN_REGIONS, 1):
            logging.info(f"[{region_index}/{len(Config.NORDVPN_REGIONS)}] Testing region: {region}")
            
            client = SOCKS5TTFBClient(region)
            connected = client.test_connection()
            
            self.results["regions"][region] = {
                "connection_status": "connected" if connected else "failed",
                "scenarios": {},
                "errors": {},
                "region_summary": {}
            }

            if not connected:
                logging.error(f"[{region}] Connection failed - skipping region")
                self.results["regions"][region]["region_summary"] = {
                    "avg_ttfb": None,
                    "avg_total": None,
                    "min_ttfb": None,
                    "max_ttfb": None,
                    "success_rate": 0.0,
                    "scenarios_completed": 0,
                    "total_scenarios": len(scenarios),
                    "quality_score": 0.0
                }
                continue

            # Regional data collection
            region_ttfb_times = []
            region_total_times = []
            successful_scenarios = 0

            # Test each scenario in this region
            for scenario in scenarios:
                logging.info(f"[{region}] Testing scenario: {scenario['name']}")
                
                scenario_ttfb = []
                scenario_totals = []
                scenario_errors = []

                # Multiple iterations for statistical reliability
                for iteration in range(Config.TEST_ITERATIONS):
                    logging.debug(f"[{region}] {scenario['name']} - Iteration {iteration + 1}")
                    
                    result = client.measure_pure_ttfb(scenario["prompt"])
                    
                    if result["success"]:
                        ttfb = result["ttfb"]
                        total = result["total_time"]
                        
                        scenario_ttfb.append(ttfb)
                        scenario_totals.append(total)
                        region_ttfb_times.append(ttfb)
                        region_total_times.append(total)
                        all_successful_ttfb.append(ttfb)
                        all_successful_totals.append(total)
                        
                        # Log individual measurement
                        logging.info(f"[{region}] {scenario['name']} #{iteration + 1}: "
                                   f"TTFB={ttfb:.3f}s, Total={total:.3f}s, "
                                   f"Quality={result.get('timing_quality', 'unknown')}")
                    else:
                        error = result.get('error', 'Unknown error')
                        scenario_errors.append(error)
                        logging.warning(f"[{region}] {scenario['name']} #{iteration + 1} FAILED: {error}")

                    # Respectful delay between API calls
                    if iteration < Config.TEST_ITERATIONS - 1:
                        time.sleep(Config.API_DELAY)

                # Calculate scenario statistics
                if scenario_ttfb:
                    successful_scenarios += 1
                    
                    scenario_stats = {
                        "avg_ttfb": statistics.mean(scenario_ttfb),
                        "min_ttfb": min(scenario_ttfb),
                        "max_ttfb": max(scenario_ttfb),
                        "std_ttfb": statistics.stdev(scenario_ttfb) if len(scenario_ttfb) > 1 else 0.0,
                        "avg_total": statistics.mean(scenario_totals),
                        "min_total": min(scenario_totals),
                        "max_total": max(scenario_totals),
                        "std_total": statistics.stdev(scenario_totals) if len(scenario_totals) > 1 else 0.0,
                        "success_rate": len(scenario_ttfb) / Config.TEST_ITERATIONS,
                        "iterations_successful": len(scenario_ttfb),
                        "iterations_failed": len(scenario_errors),
                        "consistency_score": 1.0 / (1.0 + statistics.stdev(scenario_ttfb)) if len(scenario_ttfb) > 1 else 1.0
                    }
                else:
                    scenario_stats = {
                        "avg_ttfb": None, "min_ttfb": None, "max_ttfb": None, "std_ttfb": None,
                        "avg_total": None, "min_total": None, "max_total": None, "std_total": None,
                        "success_rate": 0.0,
                        "iterations_successful": 0,
                        "iterations_failed": len(scenario_errors),
                        "consistency_score": 0.0
                    }

                self.results["regions"][region]["scenarios"][scenario["name"]] = scenario_stats

                # Record errors for analysis
                if scenario_errors:
                    self.results["regions"][region]["errors"][scenario["name"]] = scenario_errors

                # Brief pause between scenarios
                time.sleep(Config.API_DELAY / 2)

            # Calculate regional summary statistics
            if region_ttfb_times:
                regional_summary = {
                    "avg_ttfb": statistics.mean(region_ttfb_times),
                    "min_ttfb": min(region_ttfb_times),
                    "max_ttfb": max(region_ttfb_times),
                    "std_ttfb": statistics.stdev(region_ttfb_times) if len(region_ttfb_times) > 1 else 0.0,
                    "avg_total": statistics.mean(region_total_times),
                    "min_total": min(region_total_times),
                    "max_total": max(region_total_times),
                    "std_total": statistics.stdev(region_total_times) if len(region_total_times) > 1 else 0.0,
                    "success_rate": successful_scenarios / len(scenarios),
                    "scenarios_completed": successful_scenarios,
                    "total_scenarios": len(scenarios),
                    "total_measurements": len(region_ttfb_times),
                    "quality_score": (successful_scenarios / len(scenarios)) * (1.0 / (1.0 + statistics.stdev(region_ttfb_times))) if len(region_ttfb_times) > 1 else successful_scenarios / len(scenarios)
                }
                
                regional_performance[region] = regional_summary["avg_ttfb"]
                
                logging.info(f"[{region}] COMPLETED - Avg TTFB: {regional_summary['avg_ttfb']:.3f}s, "
                           f"Success: {successful_scenarios}/{len(scenarios)}, "
                           f"Quality: {regional_summary['quality_score']:.2f}")
            else:
                regional_summary = {
                    "avg_ttfb": None, "min_ttfb": None, "max_ttfb": None, "std_ttfb": None,
                    "avg_total": None, "min_total": None, "max_total": None, "std_total": None,
                    "success_rate": 0.0,
                    "scenarios_completed": 0,
                    "total_scenarios": len(scenarios),
                    "total_measurements": 0,
                    "quality_score": 0.0
                }

            self.results["regions"][region]["region_summary"] = regional_summary

        # Calculate global statistics
        end_time = datetime.now()
        test_duration = (end_time - start_time).total_seconds()
        
        if all_successful_ttfb:
            global_stats = {
                "test_duration_seconds": test_duration,
                "end_time": end_time.isoformat(),
                "total_successful_measurements": len(all_successful_ttfb),
                "global_avg_ttfb": statistics.mean(all_successful_ttfb),
                "global_min_ttfb": min(all_successful_ttfb),
                "global_max_ttfb": max(all_successful_ttfb),
                "global_std_ttfb": statistics.stdev(all_successful_ttfb),
                "global_avg_total": statistics.mean(all_successful_totals),
                "fastest_region": min(regional_performance.items(), key=lambda x: x[1])[0] if regional_performance else None,
                "slowest_region": max(regional_performance.items(), key=lambda x: x[1])[0] if regional_performance else None,
                "performance_range_seconds": max(regional_performance.values()) - min(regional_performance.values()) if regional_performance else 0,
                "regions_tested": len([r for r in self.results["regions"].values() if r["connection_status"] == "connected"])
            }
        else:
            global_stats = {
                "test_duration_seconds": test_duration,
                "end_time": end_time.isoformat(),
                "total_successful_measurements": 0,
                "global_avg_ttfb": None,
                "fastest_region": None,
                "slowest_region": None,
                "regions_tested": 0
            }

        self.results["global_stats"] = global_stats

        # Save comprehensive results
        results_filename = f"{Config.RESULTS_DIR}/ttfb_comprehensive_{datetime.now():%Y%m%d_%H%M%S}.json"
        with open(results_filename, "w") as f:
            json.dump(self.results, f, indent=2, default=str)

        logging.info(f"TTFB testing completed in {test_duration:.1f}s - Results saved to {results_filename}")
        
        if global_stats.get("fastest_region"):
            logging.info(f"Performance Winner: {global_stats['fastest_region']} "
                        f"({regional_performance[global_stats['fastest_region']]:.3f}s avg TTFB)")

        return self.results
