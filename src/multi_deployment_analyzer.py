from tabulate import tabulate
from datetime import datetime
from config.settings import Config
import json
import statistics

class MultiDeploymentAnalyzer:
    """
    Comprehensive analyzer for multi-deployment test results.
    Generates comparative reports and deployment recommendations.
    """

    def __init__(self, results, analysis_mode="comprehensive"):
        self.results = results
        self.analysis_mode = analysis_mode
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def generate_comprehensive_report(self):
        """Generate detailed markdown report comparing all deployment methods"""
        content = self._generate_report_content()
        filename = f"{Config.REPORTS_DIR}/multi_deployment_analysis_{datetime.now():%Y%m%d_%H%M%S}.md"
        with open(filename, "w") as f:
            f.write(content)
        return filename

    def _generate_report_content(self):
        """Generate comprehensive report content"""
        test_info = self.results.get("test_info", {})
        global_stats = self.results.get("global_stats", {})
        recommendations = self.results.get("recommendations", {})

        report = []

        # Header and Executive Summary
        report.append("# Multi-Deployment Gemini API Performance Analysis")
        report.append(f"**Generated**: {self.timestamp}")
        report.append("")

        report.append("## Executive Summary")
        report.append("")

        if recommendations.get("primary_deployment"):
            primary = recommendations["primary_deployment"]
            report.append(f"- **Recommended Deployment**: {self._format_method_name(primary['method'])}")
            report.append(f"- **Average Response Time**: {primary['avg_time']:.3f} seconds")
            report.append(f"- **Success Rate**: {primary['success_rate']:.1%}")
            report.append(f"- **Reasoning**: {primary['reasoning']}")
        else:
            report.append("- **Status**: No successful deployments to recommend")

        # Add streaming metrics to executive summary if available
        if test_info.get("test_mode") in ["streaming", "both"]:
            report.append("")
            report.append("### Streaming Performance Highlights")
            streaming_summary = self._generate_streaming_summary()
            report.extend(streaming_summary)

        report.append("")

        # Test Configuration
        report.append("## Test Configuration")
        report.append(f"- **Test Start**: {test_info.get('start_time', 'N/A')}")
        report.append(f"- **Test Duration**: {test_info.get('duration', 0):.1f} seconds")
        report.append(f"- **Deployment Methods**: {', '.join([self._format_method_name(m) for m in test_info.get('methods_tested', [])])}")
        report.append(f"- **Scenarios Tested**: {test_info.get('scenarios_count', 'N/A')}")
        report.append(f"- **Iterations per Scenario**: {test_info.get('iterations', 'N/A')}")
        report.append(f"- **Test Mode**: {test_info.get('test_mode', 'N/A')}")
        report.append("")

        # Performance Rankings
        report.append("## 🏆 Performance Rankings")
        report.append("")
        report.extend(self._generate_performance_rankings())
        report.append("")

        # Deployment Comparison Table with TTFB
        report.append("## 📊 Deployment Method Comparison")
        report.append("")
        comparison_table = self._generate_comparison_table()
        report.append("```")
        report.append(comparison_table)
        report.append("```")
        report.append("")

        # Scenario Analysis (FIXED for SOCKS5)
        if self.analysis_mode in ["comprehensive", "detailed"]:
            report.append("## 📋 Scenario Performance Analysis")
            report.append("")
            scenario_table = self._generate_scenario_analysis()
            report.append("```")
            report.append(scenario_table)
            report.append("```")
            report.append("")

        # Streaming-Specific Analysis
        if test_info.get("test_mode") in ["streaming", "both"]:
            report.append("## ⚡ Streaming & TTFB Analysis")
            report.append("")
            streaming_analysis = self._generate_streaming_analysis()
            report.extend(streaming_analysis)
            report.append("")

        # Detailed Method Analysis
        report.append("## 🔍 Method Analysis")
        report.extend(self._generate_method_analysis())

        # Recommendations
        report.append("## 💡 Deployment Recommendations")
        report.extend(self._generate_deployment_recommendations())

        # Use Case Guidelines
        report.append("## 🎯 Use Case Guidelines")
        report.extend(self._generate_use_case_guidelines())

        # Performance Insights
        if self.analysis_mode == "comprehensive":
            report.append("## 📈 Performance Insights")
            report.extend(self._generate_performance_insights())

        # Error Analysis
        report.append("## ⚠️ Error Analysis")
        report.extend(self._generate_error_analysis())

        return "\n".join(report)

    def _format_method_name(self, method):
        """Format method name for display"""
        names = {
            "edge_function": "Edge Function",
            "serverless_function": "Serverless Function",
            "socks5_proxy": "SOCKS5 Proxy"
        }
        return names.get(method, method.replace("_", " ").title())

    def _generate_streaming_summary(self):
        """Generate streaming performance summary for executive summary"""
        summary = []
        
        for method, data in self.results.get("deployments", {}).items():
            if method in ["edge_function", "serverless_function"]:
                # ✅ Check both streaming_metrics and summary for TTFB data
                streaming_data = data.get("streaming_metrics", {})
                summary_data = data.get("summary", {})
                
                if streaming_data and streaming_data.get("avg_ttfb"):
                    method_name = self._format_method_name(method)
                    avg_ttfb = streaming_data.get("avg_ttfb", 0)
                    avg_chars_per_sec = streaming_data.get("avg_chars_per_second", 0)
                    summary.append(f"- **{method_name}**: TTFB {avg_ttfb:.3f}s, Rate {avg_chars_per_sec:.1f} chars/sec")
                elif summary_data.get("avg_ttfb"):
                    # Fallback to summary TTFB data
                    method_name = self._format_method_name(method)
                    avg_ttfb = summary_data.get("avg_ttfb", 0)
                    summary.append(f"- **{method_name}**: TTFB {avg_ttfb:.3f}s (from summary)")
        
        return summary if summary else ["- No streaming data available"]

    def _generate_performance_rankings(self):
        """Generate performance rankings"""
        rankings = []
        for method, data in self.results.get("deployments", {}).items():
            summary = data.get("summary", {})
            if summary.get("avg_response_time"):
                rankings.append({
                    "method": method,
                    "avg_time": summary["avg_response_time"],
                    "success_rate": summary.get("success_rate", 0),
                    "score": summary.get("success_rate", 0) / summary["avg_response_time"]
                })

        # Sort by performance score (higher is better)
        rankings.sort(key=lambda x: x["score"], reverse=True)

        ranking_text = []
        for i, rank in enumerate(rankings, 1):
            if rank["avg_time"] < Config.EXCELLENT_THRESHOLD:
                emoji = "🚀"
            elif rank["avg_time"] < Config.GOOD_THRESHOLD:
                emoji = "✅"
            elif rank["avg_time"] < Config.AVERAGE_THRESHOLD:
                emoji = "⚠️"
            else:
                emoji = "🐌"

            ranking_text.append(
                f"{i}. {emoji} **{self._format_method_name(rank['method'])}**: "
                f"{rank['avg_time']:.3f}s avg (Success: {rank['success_rate']:.1%})"
            )

        return ranking_text if ranking_text else ["No successful measurements to rank."]

    def _generate_comparison_table(self):
        """Generate deployment method comparison table with TTFB support"""
        headers = ["Method", "Avg Time (s)", "Min (s)", "Max (s)", "Avg TTFB (s)", "Success Rate", "Measurements", "Status"]
        table_data = []
        
        for method, data in self.results.get("deployments", {}).items():
            summary = data.get("summary", {})
            if summary.get("avg_response_time"):
                # Get TTFB data if available
                avg_ttfb = summary.get("avg_ttfb", "N/A")
                ttfb_str = f"{avg_ttfb:.3f}" if isinstance(avg_ttfb, (int, float)) else "N/A"
                
                # FIX: Calculate actual measurements for SOCKS5
                if method == "socks5_proxy":
                    # Check if we have valid measurements from regional results
                    actual_measurements = 0
                    regional_results = data.get("regional_results", {})
                    for region_data in regional_results.values():
                        if region_data.get("connection_status") == "connected":
                            # MISSING: This line needs to be added
                            region_measurements = len(region_data.get("response_times", []))
                            actual_measurements += region_measurements
                    measurements_count = actual_measurements
                    has_valid_data = summary.get("avg_response_time") is not None and actual_measurements > 0
                else:
                    has_valid_data = summary.get("avg_response_time") is not None
                    measurements_count = summary.get("total_measurements", 0)
                
                table_data.append([
                    self._format_method_name(method),
                    f"{summary['avg_response_time']:.3f}",
                    f"{summary.get('min_response_time', 0):.3f}",
                    f"{summary.get('max_response_time', 0):.3f}",
                    ttfb_str,
                    f"{summary.get('success_rate', 0):.1%}",
                    f"{measurements_count}",  # Use corrected count
                    "✅ Operational"
                ])
            else:
                table_data.append([
                    self._format_method_name(method),
                    "Failed", "N/A", "N/A", "N/A", "0%", "0", "❌ Failed"
                ])
        
        return tabulate(table_data, headers=headers, tablefmt="grid")

    def _generate_scenario_analysis(self):
        """Generate scenario-by-scenario analysis - FIXED VERSION for all deployment methods"""
        headers = ["Scenario", "Category", "Edge Function", "Serverless", "SOCKS5", "Best Method"]
        table_data = []

        # Get all scenarios from any deployment method - INCLUDING SOCKS5 regional data
        all_scenarios = set()
        for method_data in self.results.get("deployments", {}).values():
            # Handle direct scenario structure (Edge/Serverless)
            if method_data.get("scenarios"):
                all_scenarios.update(method_data["scenarios"].keys())
            
            # Handle SOCKS5 regional structure
            if method_data.get("regional_results"):
                for region_data in method_data["regional_results"].values():
                    if region_data.get("scenarios"):
                        all_scenarios.update(region_data["scenarios"].keys())

        from tests.test_scenarios import TestScenarios
        scenario_lookup = {s["name"]: s for s in TestScenarios.get_all_scenarios()}

        for scenario_name in sorted(all_scenarios):
            scenario_info = scenario_lookup.get(scenario_name, {})
            category = scenario_info.get("category", "unknown")
            times = {}

            for method in ["edge_function", "serverless_function", "socks5_proxy"]:
                method_data = self.results.get("deployments", {}).get(method, {})
                
                if method == "socks5_proxy":
                    # Handle SOCKS5's regional structure - aggregate across all regions
                    regional_results = method_data.get("regional_results", {})
                    all_region_times = []
                    
                    for region, region_data in regional_results.items():
                        scenario_data = region_data.get("scenarios", {}).get(scenario_name, {})
                        # Try both 'avg_time' and 'avg' for backward compatibility
                        avg_time = scenario_data.get("avg_time") or scenario_data.get("avg")
                        if avg_time is not None:
                            all_region_times.append(avg_time)

                    # Calculate average across all successful regions
                    if all_region_times:
                        avg_time = statistics.mean(all_region_times)
                        times[method] = f"{avg_time:.3f}s"
                    else:
                        times[method] = "Failed"
                else:
                    # Handle direct scenario structure (Edge/Serverless)
                    scenario_data = method_data.get("scenarios", {}).get(scenario_name, {})
                    avg_time = scenario_data.get("avg_time")
                    times[method] = f"{avg_time:.3f}s" if avg_time else "Failed"

            # Determine best method for this scenario
            valid_times = {k: v for k, v in times.items() if v != "Failed"}
            if valid_times:
                best_method = min(valid_times.items(), key=lambda x: float(x[1].replace("s", "")))[0]
                best_method = self._format_method_name(best_method)
            else:
                best_method = "None"

            table_data.append([
                scenario_name,
                category.title(),
                times.get("edge_function", "N/A"),
                times.get("serverless_function", "N/A"),
                times.get("socks5_proxy", "N/A"),
                best_method
            ])

        return tabulate(table_data, headers=headers, tablefmt="grid")


    def _generate_streaming_analysis(self):
        """Generate detailed streaming and TTFB analysis"""
        analysis = []
        
        for method in ["edge_function", "serverless_function"]:
            method_data = self.results.get("deployments", {}).get(method, {})
            streaming_data = method_data.get("streaming_metrics", {})
            
            if streaming_data:
                method_name = self._format_method_name(method)
                analysis.append(f"### {method_name} Streaming Metrics")
                
                # TTFB Analysis
                avg_ttfb = streaming_data.get("avg_ttfb", 0)
                min_ttfb = streaming_data.get("min_ttfb", 0)
                max_ttfb = streaming_data.get("max_ttfb", 0)
                
                analysis.append(f"- **Average TTFB**: {avg_ttfb:.3f} seconds")
                analysis.append(f"- **TTFB Range**: {min_ttfb:.3f}s - {max_ttfb:.3f}s")
                
                # Streaming Performance
                chars_per_sec = streaming_data.get("avg_chars_per_second", 0)
                analysis.append(f"- **Streaming Rate**: {chars_per_sec:.1f} characters/second")
                
                # Quality Metrics
                consistency = streaming_data.get("streaming_consistency", 0)
                user_experience = streaming_data.get("user_experience_score", 0)
                
                analysis.append(f"- **Streaming Consistency**: {consistency:.2f}")
                analysis.append(f"- **User Experience Score**: {user_experience:.2f}")
                
                # Method-specific insights
                if method == "serverless_function":
                    cold_start_impact = streaming_data.get("cold_start_ttfb_impact", 0)
                    if cold_start_impact > 0:
                        analysis.append(f"- **Cold Start TTFB Impact**: +{cold_start_impact:.3f}s")
                
                analysis.append("")
        
        return analysis if analysis else ["No streaming data available for analysis."]

    def _generate_method_analysis(self):
        """Generate detailed analysis for each method with streaming support"""
        analysis = []

        for method, data in self.results.get("deployments", {}).items():
            analysis.append(f"### {self._format_method_name(method)}")
            summary = data.get("summary", {})

            if summary.get("avg_response_time"):
                analysis.append(f"- **Average Response Time**: {summary['avg_response_time']:.3f} seconds")
                analysis.append(f"- **Performance Range**: {summary.get('min_response_time', 0):.3f}s - {summary.get('max_response_time', 0):.3f}s")
                analysis.append(f"- **Reliability**: {summary.get('success_rate', 0):.1%} success rate")
                analysis.append(f"- **Total Measurements**: {summary.get('total_measurements', 0)}")

                # Add TTFB information if available
                if summary.get("avg_ttfb"):
                    analysis.append(f"- **Average TTFB**: {summary['avg_ttfb']:.3f} seconds")
                    ttfb_percentage = (summary['avg_ttfb'] / summary['avg_response_time']) * 100
                    analysis.append(f"- **TTFB Percentage**: {ttfb_percentage:.1f}% of total time")

                # Performance assessment
                avg_time = summary['avg_response_time']
                if avg_time < Config.EXCELLENT_THRESHOLD:
                    assessment = "🚀 **Excellent** - Recommended for production"
                elif avg_time < Config.GOOD_THRESHOLD:
                    assessment = "✅ **Good** - Suitable for production"
                elif avg_time < Config.AVERAGE_THRESHOLD:
                    assessment = "⚠️ **Average** - Consider as backup"
                else:
                    assessment = "🐌 **Poor** - Not recommended"

                analysis.append(f"- **Assessment**: {assessment}")

                # Method-specific insights
                if method == "serverless_function" and "cold_start_rate" in summary:
                    analysis.append(f"- **Cold Start Rate**: {summary['cold_start_rate']:.1%}")
                elif method == "socks5_proxy" and "regions_tested" in summary:
                    analysis.append(f"- **Regions Tested**: {summary['regions_tested']}")

            else:
                analysis.append("- **Status**: ❌ No successful measurements")

            analysis.append("")

        return analysis

    def _generate_deployment_recommendations(self):
        """Generate deployment recommendations"""
        recommendations = self.results.get("recommendations", {})
        analysis = []

        if recommendations.get("primary_deployment"):
            analysis.append("### Primary Recommendation")
            primary = recommendations["primary_deployment"]
            analysis.append(f"**Deploy using {self._format_method_name(primary['method'])}**")
            analysis.append(f"- Average response time: {primary['avg_time']:.3f} seconds")
            analysis.append(f"- Success rate: {primary['success_rate']:.1%}")
            analysis.append(f"- Reasoning: {primary['reasoning']}")
            analysis.append("")

            # Backup recommendations
            if recommendations.get("fastest_deployment") and recommendations["fastest_deployment"]["method"] != primary["method"]:
                fastest = recommendations["fastest_deployment"]
                analysis.append("### Backup Option")
                analysis.append(f"**{self._format_method_name(fastest['method'])}** for speed-critical applications")
                analysis.append(f"- Response time: {fastest['avg_time']:.3f} seconds")
                analysis.append("")
        else:
            analysis.append("### No Recommendations Available")
            analysis.append("All deployment methods failed or had insufficient data.")
            analysis.append("")

        return analysis

    def _generate_use_case_guidelines(self):
        """Generate use case specific guidelines"""
        recommendations = self.results.get("recommendations", {})
        guidelines = []

        if recommendations.get("use_cases"):
            use_cases = recommendations["use_cases"]

            guidelines.append("### Simple Prompts (< 50 tokens)")
            guidelines.append(f"- **Recommended**: {self._format_method_name(use_cases.get('simple_prompts', 'N/A'))}")
            guidelines.append("- **Use for**: Quick responses, real-time interactions")
            guidelines.append("")

            guidelines.append("### Complex Prompts (> 200 tokens)")
            guidelines.append(f"- **Recommended**: {self._format_method_name(use_cases.get('complex_prompts', 'N/A'))}")
            guidelines.append("- **Use for**: Detailed analysis, content generation")
            guidelines.append("")

            guidelines.append("### Production Workloads")
            guidelines.append(f"- **Recommended**: {self._format_method_name(use_cases.get('production_workload', 'N/A'))}")
            guidelines.append("- **Use for**: High-volume, mission-critical applications")
            guidelines.append("")
        else:
            guidelines.append("Use case guidelines unavailable due to insufficient test data.")
            guidelines.append("")

        return guidelines

    def _generate_performance_insights(self):
        """Generate performance insights and trends"""
        insights = []
        global_stats = self.results.get("global_stats", {})

        if global_stats.get("total_measurements", 0) > 0:
            insights.append(f"- **Total Performance Data**: {global_stats['total_measurements']} measurements across {global_stats.get('methods_tested', 0)} methods")
            insights.append(f"- **Overall Average**: {global_stats.get('global_avg_response_time', 0):.3f} seconds")
            insights.append(f"- **Performance Spread**: {global_stats.get('performance_range', 0):.3f} seconds between fastest and slowest methods")

            # Performance consistency analysis
            std_time = global_stats.get("global_std_response_time", 0)
            avg_time = global_stats.get("global_avg_response_time", 1)
            cv = (std_time / avg_time) * 100 if avg_time > 0 else 0

            if cv < 20:
                consistency = "High consistency across methods"
            elif cv < 40:
                consistency = "Moderate consistency across methods"
            else:
                consistency = "High variability across methods"

            insights.append(f"- **Consistency**: {consistency} (CV: {cv:.1f}%)")
        else:
            insights.append("- **Performance Data**: Insufficient data for insights")

        insights.append("")
        return insights

    def _generate_error_analysis(self):
        """Generate error analysis across all deployment methods"""
        analysis = []
        has_errors = False

        for method, data in self.results.get("deployments", {}).items():
            errors = data.get("errors", {})
            if errors:
                has_errors = True
                error_count = sum(len(error_list) if isinstance(error_list, list) else 1
                                  for error_list in errors.values())
                analysis.append(f"- **{self._format_method_name(method)}**: {error_count} errors across {len(errors)} scenarios")

                # Detail specific error scenarios
                for scenario, error_info in errors.items():
                    if isinstance(error_info, list):
                        analysis.append(f"  - {scenario}: {len(error_info)} failures")
                    else:
                        analysis.append(f"  - {scenario}: {error_info}")

        if not has_errors:
            analysis.append("- **Status**: ✅ No errors detected across all deployment methods")

        analysis.append("")
        return analysis
