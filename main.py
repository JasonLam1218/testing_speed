#!/usr/bin/env python3

import argparse
import sys

from config.settings import Config
from src.utils import ValidationUtils
from src.socks5_test_runner import SOCKS5TestRunner
from src.socks5_analyzer import SOCKS5RegionalAnalyzer
from src.socks5_ttfb_test_runner import SOCKS5TTFBTestRunner
from src.socks5_ttfb_analyzer import SOCKS5TTFBAnalyzer

def parse():
    p = argparse.ArgumentParser(description="SOCKS5 Regional Speed Test for Gemini API")
    p.add_argument("--regions", nargs="+", default=Config.NORDVPN_REGIONS,
                   help="NordVPN region codes to test")
    p.add_argument("--scenarios", choices=["simple","medium","complex","all"], default="all",
                   help="Test scenario categories")
    p.add_argument("--iterations", type=int, default=Config.TEST_ITERATIONS,
                   help="Number of iterations per scenario")
    p.add_argument("--delay", type=int, default=Config.API_DELAY,
                   help="Delay between API calls in seconds")
    p.add_argument("--test-mode", choices=["total", "ttfb", "both"], default="total",
                   help="Test mode: total response time, TTFB analysis, or both")
    p.add_argument("--verbose", action="store_true")
    return p.parse_args()

def main():
    args = parse()
    
    # Override config values with CLI arguments
    Config.NORDVPN_REGIONS = args.regions
    Config.TEST_ITERATIONS = args.iterations
    Config.API_DELAY = args.delay
    
    # Validate environment
    validation = ValidationUtils.validate_environment()
    if not validation["valid"]:
        print("❌ Environment validation failed:")
        for error in validation["errors"]:
            print(f"  - {error}")
        sys.exit(1)
    
    print("✅ Environment validation passed")
    print(f"🚀 Starting analysis across {len(Config.NORDVPN_REGIONS)} regions...")
    print(f"📊 Test mode: {args.test_mode}")
    
    # Run basic total response time tests
    if args.test_mode in ["total", "both"]:
        print("\n🔄 Running basic response time tests...")
        runner = SOCKS5TestRunner()
        results = runner.run(args.scenarios)
        analyzer = SOCKS5RegionalAnalyzer(results)
        report_file = analyzer.save()
        print(f"📄 Basic report saved to: {report_file}")
        
        # Print quick summary
        print("\n🏆 Basic Results Summary:")
        for region, data in results["regions"].items():
            if data.get("connected") and data.get("summary", {}).get("avg_response"):
                summary = data["summary"]
                print(f"  ✅ {region}: {summary['avg_response']:.3f}s avg, {summary['success_rate']:.1%} success")
            else:
                print(f"  ❌ {region}: Connection failed")
    
    # Run enhanced TTFB analysis
    if args.test_mode in ["ttfb", "both"]:
        print("\n⚡ Running enhanced TTFB analysis...")
        ttfb_runner = SOCKS5TTFBTestRunner()
        ttfb_results = ttfb_runner.run(args.scenarios)
        ttfb_analyzer = SOCKS5TTFBAnalyzer(ttfb_results)
        ttfb_report_file = ttfb_analyzer.save_report()
        print(f"📄 TTFB analysis saved to: {ttfb_report_file}")
        
        # Print comprehensive summary
        global_stats = ttfb_results.get("global_stats", {})
        if global_stats.get("fastest_region"):
            print(f"\n⚡ TTFB Analysis Summary:")
            print(f"  🏆 Fastest Region: {global_stats['fastest_region']}")
            print(f"  🐌 Slowest Region: {global_stats['slowest_region']}")
            print(f"  📊 Global Average: {global_stats['global_avg_ttfb']:.3f}s")
            print(f"  📈 Performance Spread: {global_stats['performance_range_seconds']:.3f}s")
            print(f"  ✅ Successful Measurements: {global_stats['total_successful_measurements']}")
        else:
            print("\n❌ No successful TTFB measurements obtained")

if __name__ == "__main__":
    main()
