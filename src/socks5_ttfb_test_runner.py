import time
import statistics
import logging
import json
from datetime import datetime
from src.socks5_ttfb_client import SOCKS5TTFBClient
from tests.test_scenarios import TestScenarios
from config.settings import Config

class SOCKS5TTFBTestRunner:
    def __init__(self):
        self.results = {
            "info": {},
            "regions": {}
        }
        
        logging.basicConfig(
            level=logging.INFO,
            handlers=[
                logging.FileHandler(f"{Config.RESULTS_DIR}/ttfb_log_{datetime.now():%Y%m%d_%H%M%S}.txt"),
                logging.StreamHandler()
            ]
        )

    def run(self, scenario_cat):
        start_time = datetime.now()
        self.results["info"] = {
            "start": start_time.isoformat(),
            "iterations": Config.TEST_ITERATIONS,
            "delay": Config.API_DELAY,
            "measurement_type": "TTFB_and_Total"
        }

        if scenario_cat == "all":
            scenarios = TestScenarios.get_all_scenarios()
        else:
            scenarios = TestScenarios.get_scenarios_by_category(scenario_cat)

        for region in Config.NORDVPN_REGIONS:
            client = SOCKS5TTFBClient(region)
            connected = client.test_connection()
            
            self.results["regions"][region] = {
                "connected": connected,
                "scenarios": {},
                "errors": {}
            }

            if not connected:
                self.results["regions"][region]["summary"] = {
                    "avg_ttfb": None,
                    "avg_total": None,
                    "min_ttfb": None,
                    "max_ttfb": None,
                    "success_rate": 0.0,
                    "successful_scenarios": 0,
                    "total_scenarios": len(scenarios)
                }
                continue

            all_ttfb_times = []
            all_total_times = []
            successful_scenarios = 0

            for s in scenarios:
                scenario_ttfb = []
                scenario_total = []
                scenario_errors = []

                for i in range(Config.TEST_ITERATIONS):
                    res = client.generate_content_with_ttfb(s["prompt"])
                    
                    if res["success"]:
                        scenario_ttfb.append(res["ttfb"])
                        scenario_total.append(res["total_time"])
                        all_ttfb_times.append(res["ttfb"])
                        all_total_times.append(res["total_time"])
                        logging.info(f"{region} {s['name']} TTFB={res['ttfb']:.3f}s Total={res['total_time']:.3f}s")
                    else:
                        scenario_errors.append(res.get('error', 'Unknown error'))
                        logging.warning(f"{region} {s['name']} failed: {res.get('error', 'Unknown error')}")

                    if i < Config.TEST_ITERATIONS - 1:
                        time.sleep(Config.API_DELAY)

                # Calculate per-scenario statistics
                if scenario_ttfb:
                    successful_scenarios += 1
                    stats = {
                        "avg_ttfb": statistics.mean(scenario_ttfb),
                        "min_ttfb": min(scenario_ttfb),
                        "max_ttfb": max(scenario_ttfb),
                        "std_ttfb": statistics.stdev(scenario_ttfb) if len(scenario_ttfb) > 1 else 0.0,
                        "avg_total": statistics.mean(scenario_total),
                        "min_total": min(scenario_total),
                        "max_total": max(scenario_total),
                        "std_total": statistics.stdev(scenario_total) if len(scenario_total) > 1 else 0.0,
                        "avg_processing": statistics.mean([total - ttfb for total, ttfb in zip(scenario_total, scenario_ttfb)]),  # ✅ Add this
                        "success_rate": len(scenario_ttfb) / Config.TEST_ITERATIONS,
                        "error_count": len(scenario_errors)
                    }
                else:
                    stats = {
                        "avg_ttfb": None, "min_ttfb": None, "max_ttfb": None, "std_ttfb": None,
                        "avg_total": None, "min_total": None, "max_total": None, "std_total": None,
                        "success_rate": 0.0,
                        "error_count": len(scenario_errors)
                    }

                self.results["regions"][region]["scenarios"][s["name"]] = stats
                
                if scenario_errors:
                    self.results["regions"][region]["errors"][s["name"]] = len(scenario_errors)

                time.sleep(Config.API_DELAY)

            # Calculate overall region summary statistics
            if all_ttfb_times:
                self.results["regions"][region]["summary"] = {
                    "avg_ttfb": statistics.mean(all_ttfb_times),
                    "min_ttfb": min(all_ttfb_times),
                    "max_ttfb": max(all_ttfb_times),
                    "std_ttfb": statistics.stdev(all_ttfb_times) if len(all_ttfb_times) > 1 else 0.0,
                    "avg_total": statistics.mean(all_total_times),
                    "min_total": min(all_total_times),
                    "max_total": max(all_total_times),
                    "std_total": statistics.stdev(all_total_times) if len(all_total_times) > 1 else 0.0,
                    "success_rate": successful_scenarios / len(scenarios),
                    "successful_scenarios": successful_scenarios,
                    "total_scenarios": len(scenarios)
                }
            else:
                self.results["regions"][region]["summary"] = {
                    "avg_ttfb": None, "min_ttfb": None, "max_ttfb": None, "std_ttfb": None,
                    "avg_total": None, "min_total": None, "max_total": None, "std_total": None,
                    "success_rate": 0.0,
                    "successful_scenarios": 0,
                    "total_scenarios": len(scenarios)
                }

        end_time = datetime.now()
        self.results["info"]["end"] = end_time.isoformat()
        self.results["info"]["duration"] = (end_time - start_time).total_seconds()

        # Save raw TTFB results json
        raw_fn = f"{Config.RESULTS_DIR}/ttfb_raw_{datetime.now():%Y%m%d_%H%M%S}.json"
        with open(raw_fn, "w") as f:
            json.dump(self.results, f, indent=2)

        return self.results
