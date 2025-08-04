import time
import statistics
import logging
import json
from datetime import datetime

from src.socks5_client import SOCKS5Client
from tests.test_scenarios import TestScenarios
from config.settings import Config

class SOCKS5TestRunner:
    def __init__(self):
        self.results = {
            "info": {},
            "regions": {}
        }
        logging.basicConfig(
            level=logging.INFO,
            handlers=[
                logging.FileHandler(f"{Config.RESULTS_DIR}/log_{datetime.now():%Y%m%d_%H%M%S}.txt"),
                logging.StreamHandler()
            ]
        )

    def run(self, scenario_cat):
        start_time = datetime.now()
        self.results["info"] = {
            "start": start_time.isoformat(),
            "iterations": Config.TEST_ITERATIONS,
            "delay": Config.API_DELAY
        }

        if scenario_cat == "all":
            scenarios = TestScenarios.get_all_scenarios()
        else:
            scenarios = TestScenarios.get_scenarios_by_category(scenario_cat)

        for region in Config.NORDVPN_REGIONS:
            client = SOCKS5Client(region)
            connected = client.test_connection()
            self.results["regions"][region] = {
                "connected": connected, 
                "scenarios": {},
                "errors": {}
            }

            if not connected:
                # Set summary for disconnected regions
                self.results["regions"][region]["summary"] = {
                    "avg_response": None,
                    "min_response": None,
                    "max_response": None,
                    "success_rate": 0.0,
                    "successful_scenarios": 0,
                    "total_scenarios": len(scenarios)
                }
                continue

            all_times = []
            successful_scenarios = 0

            for s in scenarios:
                scenario_times = []
                scenario_errors = []
                
                for i in range(Config.TEST_ITERATIONS):
                    res = client.generate_content(s["prompt"])
                    if res["success"]:
                        scenario_times.append(res["time"])
                        all_times.append(res["time"])
                        logging.info(f"{region} {s['name']} {res['time']:.3f}s")
                    else:
                        scenario_errors.append(res.get('error', 'Unknown error'))
                        logging.warning(f"{region} {s['name']} failed: {res.get('error', 'Unknown error')}")
                    
                    if i < Config.TEST_ITERATIONS - 1:
                        time.sleep(Config.API_DELAY)

                # Calculate per-scenario statistics
                if scenario_times:
                    successful_scenarios += 1
                    stats = {
                        "avg": statistics.mean(scenario_times),
                        "min": min(scenario_times),
                        "max": max(scenario_times),
                        "std": statistics.stdev(scenario_times) if len(scenario_times) > 1 else 0.0,
                        "success_rate": len(scenario_times) / Config.TEST_ITERATIONS,
                        "error_count": len(scenario_errors)
                    }
                else:
                    stats = {
                        "avg": None,
                        "min": None,
                        "max": None,
                        "std": None,
                        "success_rate": 0.0,
                        "error_count": len(scenario_errors)
                    }
                
                self.results["regions"][region]["scenarios"][s["name"]] = stats
                if scenario_errors:
                    self.results["regions"][region]["errors"][s["name"]] = len(scenario_errors)
                
                time.sleep(Config.API_DELAY)

            # Calculate overall region summary statistics
            if all_times:
                self.results["regions"][region]["summary"] = {
                    "avg_response": statistics.mean(all_times),
                    "min_response": min(all_times),
                    "max_response": max(all_times),
                    "std_response": statistics.stdev(all_times) if len(all_times) > 1 else 0.0,
                    "success_rate": successful_scenarios / len(scenarios),
                    "successful_scenarios": successful_scenarios,
                    "total_scenarios": len(scenarios)
                }
            else:
                # No successful requests
                self.results["regions"][region]["summary"] = {
                    "avg_response": None,
                    "min_response": None,
                    "max_response": None,
                    "std_response": None,
                    "success_rate": 0.0,
                    "successful_scenarios": 0,
                    "total_scenarios": len(scenarios)
                }

        end_time = datetime.now()
        self.results["info"]["end"] = end_time.isoformat()
        self.results["info"]["duration"] = (end_time - start_time).total_seconds()

        # Save raw results json
        raw_fn = f"{Config.RESULTS_DIR}/raw_{datetime.now():%Y%m%d_%H%M%S}.json"
        with open(raw_fn, "w") as f:
            json.dump(self.results, f, indent=2)

        return self.results
