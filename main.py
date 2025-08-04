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
                   help="Test mode: total response time, TTFB, or both")
    p.add_argument("--verbose", action="store_true")
    return p.parse_args()

def main():
    args = parse()
    
    # Override config values with CLI arguments
    Config.NORDVPN_REGIONS = args.regions
    Config.TEST_ITERATIONS = args.iterations
    Config.API_DELAY = args.delay
    
    # Validate environment
    v = ValidationUtils.validate_environment()
    if not v["valid"]:
        print("❌ Environment validation failed:")
        for error in v["errors"]:
            print(f"  - {error}")
        sys.exit(1)
    
    print("✅ Environment validation passed")
    print(f"🚀 Starting speed test across {len(Config.NORDVPN_REGIONS)} regions...")
    print(f"📊 Test mode: {args.test_mode}")
    
    if args.test_mode in ["total", "both"]:
        print("\n🔄 Running total response time tests...")
        runner = SOCKS5TestRunner()
        results = runner.run(args.scenarios)
        
        analyzer = SOCKS5RegionalAnalyzer(results)
        report_file = analyzer.save()
        print(f"📄 Total time report saved to: {report_file}")
        
        # Print quick summary
        print("\n🏆 Total Time Results Summary:")
        for region, data in results["regions"].items():
            if data.get("connected") and data["summary"]["avg_response"]:
                summary = data["summary"]
                print(f"  ✅ {region}: Avg={summary['avg_response']:.3f}s, Success={summary['success_rate']:.1%}")
            else:
                print(f"  ❌ {region}: Connection failed or no successful requests")
    
    if args.test_mode in ["ttfb", "both"]:
        print("\n⚡ Running TTFB tests...")
        ttfb_runner = SOCKS5TTFBTestRunner()
        ttfb_results = ttfb_runner.run(args.scenarios)
        
        ttfb_analyzer = SOCKS5TTFBAnalyzer(ttfb_results)
        ttfb_report_file = ttfb_analyzer.save()
        print(f"📄 TTFB report saved to: {ttfb_report_file}")
        
        # Print quick TTFB summary
        print("\n⚡ TTFB Results Summary:")
        for region, data in ttfb_results["regions"].items():
            if data.get("connected") and data["summary"]["avg_ttfb"]:
                summary = data["summary"]
                print(f"  ✅ {region}: TTFB={summary['avg_ttfb']:.3f}s, Total={summary['avg_total']:.3f}s, Success={summary['success_rate']:.1%}")
            else:
                print(f"  ❌ {region}: Connection failed or no successful requests")

if __name__ == "__main__":
    main()
