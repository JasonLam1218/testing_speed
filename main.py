#!/usr/bin/env python3

import argparse
import sys
from config.settings import Config
from src.utils import ValidationUtils
from src.socks5_test_runner import SOCKS5TestRunner
from src.socks5_analyzer import SOCKS5RegionalAnalyzer
from src.socks5_ttfb_test_runner import SOCKS5TTFBTestRunner
from src.socks5_ttfb_analyzer import SOCKS5TTFBAnalyzer
from src.multi_deployment_test_runner import MultiDeploymentTestRunner
from src.multi_deployment_analyzer import MultiDeploymentAnalyzer

def parse():
    p = argparse.ArgumentParser(description="Multi-Deployment Speed Test for Gemini API")
    
    # Test scope
    p.add_argument("--deployment", choices=["edge", "serverless", "socks5", "multi"], default="multi",
                   help="Deployment method to test")
    p.add_argument("--regions", nargs="+", default=Config.NORDVPN_REGIONS,
                   help="NordVPN region codes to test (SOCKS5 only)")
    p.add_argument("--scenarios", choices=["simple","medium","complex","all"], default="all",
                   help="Test scenario categories")
    
    # Test parameters
    p.add_argument("--iterations", type=int, default=Config.TEST_ITERATIONS,
                   help="Number of iterations per scenario")
    p.add_argument("--delay", type=int, default=Config.API_DELAY,
                   help="Delay between API calls in seconds")
    
    # Test modes
    p.add_argument("--test-mode", choices=["total", "ttfb", "both", "streaming"], default="total",
                   help="Test mode: total response time, TTFB analysis, both, or streaming metrics")
    p.add_argument("--analysis-mode", choices=["basic", "comprehensive", "streaming"], default="comprehensive",
                   help="Analysis depth")
    
    # Options
    p.add_argument("--verbose", action="store_true")
    p.add_argument("--save-raw", action="store_true", help="Save raw response data")
    
    return p.parse_args()

def run_legacy_socks5_tests(args):
    """Run original SOCKS5-only tests for backward compatibility"""
    print("🔄 Running legacy SOCKS5 tests...")
    
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
                print(f" ✅ {region}: {summary['avg_response']:.3f}s avg, {summary['success_rate']:.1%} success")
            else:
                print(f" ❌ {region}: Connection failed")
    
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
            print(f" 🏆 Fastest Region: {global_stats['fastest_region']}")
            print(f" 🐌 Slowest Region: {global_stats['slowest_region']}")
            print(f" 📊 Global Average: {global_stats['global_avg_ttfb']:.3f}s")
            print(f" 📈 Performance Spread: {global_stats['performance_range_seconds']:.3f}s")
            print(f" ✅ Successful Measurements: {global_stats['total_successful_measurements']}")
        else:
            print("\n❌ No successful TTFB measurements obtained")

def run_multi_deployment_tests(args):
    """Run comprehensive multi-deployment tests"""
    print("🚀 Running multi-deployment performance analysis...")
    
    # Configure test methods based on deployment argument
    if args.deployment == "multi":
        test_methods = Config.DEPLOYMENT_METHODS
    else:
        method_map = {
            "edge": "edge_function",
            "serverless": "serverless_function", 
            "socks5": "socks5_proxy"
        }
        test_methods = [method_map[args.deployment]]
    
    print(f"📊 Testing deployment methods: {', '.join(test_methods)}")
    print(f"📋 Test mode: {args.test_mode}")
    print(f"🔍 Analysis mode: {args.analysis_mode}")
    
    # Run unified tests
    runner = MultiDeploymentTestRunner(
        test_methods=test_methods,
        regions=args.regions,
        iterations=args.iterations,
        delay=args.delay,
        test_mode=args.test_mode,
        save_raw=args.save_raw,
        verbose=args.verbose
    )
    
    results = runner.run_comprehensive_tests(args.scenarios)
    
    # Generate analysis
    analyzer = MultiDeploymentAnalyzer(results, analysis_mode=args.analysis_mode)
    report_file = analyzer.generate_comprehensive_report()
    
    print(f"\n📄 Comprehensive report saved to: {report_file}")
    
    # Print executive summary
    print("\n🏆 Executive Summary:")
    if results.get("recommendations"):
        recs = results["recommendations"]
        if recs.get("primary_deployment"):
            print(f" 🥇 Best Overall: {recs['primary_deployment']['method']} ({recs['primary_deployment']['avg_time']:.3f}s)")
        if recs.get("fastest_deployment"):
            print(f" ⚡ Fastest: {recs['fastest_deployment']['method']} ({recs['fastest_deployment']['avg_time']:.3f}s)")
        if recs.get("most_reliable"):
            print(f" 🛡️ Most Reliable: {recs['most_reliable']['method']} ({recs['most_reliable']['success_rate']:.1%})")
    
    # Method-specific summaries
    for method, data in results.get("deployments", {}).items():
        if data.get("summary"):
            summary = data["summary"]
            status = "✅" if summary.get("avg_response_time") else "❌"
            time_str = f"{summary['avg_response_time']:.3f}s" if summary.get("avg_response_time") else "Failed"
            rate_str = f"{summary['success_rate']:.1%}" if summary.get("success_rate") else "0%"
            print(f" {status} {Config.get_deployment_config(method)['name']}: {time_str} avg, {rate_str} success")

def main():
    args = parse()
    
    # Override config values with CLI arguments
    Config.NORDVPN_REGIONS = args.regions
    Config.TEST_ITERATIONS = args.iterations
    Config.API_DELAY = args.delay
    
    # Validate environment
    try:
        validation = ValidationUtils.validate_environment()
        if not validation["valid"]:
            print("❌ Environment validation failed:")
            for error in validation["errors"]:
                print(f" - {error}")
            
            # Check if this is just deployment URL warnings
            deployment_warnings = [e for e in validation["errors"] if "not configured" in e]
            critical_errors = [e for e in validation["errors"] if "not configured" not in e]
            
            if critical_errors:
                sys.exit(1)
            elif deployment_warnings and args.deployment in ["edge", "serverless", "multi"]:
                print("\n⚠️ Note: Continue with SOCKS5-only testing until Vercel deployment is complete")
                args.deployment = "socks5"
        else:
            print("✅ Environment validation passed")
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        sys.exit(1)
    
    print(f"🚀 Starting analysis with {args.deployment} deployment(s)...")
    
    # Route to appropriate test runner
    if args.deployment == "socks5" and args.test_mode in ["total", "ttfb", "both"]:
        # Use legacy SOCKS5 runners for backward compatibility
        run_legacy_socks5_tests(args)
    else:
        # Use new multi-deployment framework
        run_multi_deployment_tests(args)

if __name__ == "__main__":
    main()
