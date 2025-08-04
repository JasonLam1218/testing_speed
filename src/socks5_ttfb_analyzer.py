from tabulate import tabulate
from datetime import datetime
from config.settings import Config
import json

class SOCKS5TTFBAnalyzer:
    """
    Advanced analyzer for TTFB test results with comprehensive reporting.
    """
    
    def __init__(self, results):
        self.results = results
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def generate_comprehensive_report(self):
        """Generate detailed markdown report with statistical analysis"""
        test_info = self.results.get("test_info", {})
        global_stats = self.results.get("global_stats", {})
        
        report = []
        
        # Header and Executive Summary
        report.append("# Gemini API Time To First Byte (TTFB) Analysis Report")
        report.append(f"**Generated**: {self.timestamp}")
        report.append("")
        report.append("## Executive Summary")
        report.append("")
        
        if global_stats.get("fastest_region"):
            fastest = global_stats["fastest_region"]
            slowest = global_stats["slowest_region"]
            performance_gap = global_stats.get("performance_range_seconds", 0)
            
            report.append(f"- **Best Performing Region**: {fastest}")
            report.append(f"- **Worst Performing Region**: {slowest}")
            report.append(f"- **Performance Gap**: {performance_gap:.3f} seconds")
            report.append(f"- **Global Average TTFB**: {global_stats.get('global_avg_ttfb', 0):.3f} seconds")
            report.append(f"- **Total Measurements**: {global_stats.get('total_successful_measurements', 0)}")
            report.append(f"- **Regions Successfully Tested**: {global_stats.get('regions_tested', 0)}")
        else:
            report.append("- **Status**: No successful measurements obtained")
        
        report.append("")
        
        # Test Configuration
        report.append("## Test Configuration")
        report.append(f"- **Test Start**: {test_info.get('start_time', 'N/A')}")
        report.append(f"- **Test Duration**: {global_stats.get('test_duration_seconds', 0):.1f} seconds")
        report.append(f"- **Iterations per Scenario**: {test_info.get('iterations', 'N/A')}")
        report.append(f"- **Scenarios Tested**: {test_info.get('scenarios_count', 'N/A')}")
        report.append(f"- **Measurement Focus**: Time To First Byte (TTFB)")
        report.append("")
        report.append("**Important Note**: For Gemini API, TTFB represents the time until response generation is complete, as the API generates full responses before sending any data.")
        report.append("")

        # Performance Rankings
        report.append("## 🏆 Regional Performance Rankings")
        report.append("")
        rankings = self._generate_performance_rankings()
        report.append(rankings)
        report.append("")

        # Detailed Statistics Table
        report.append("## 📊 Detailed Performance Statistics")
        report.append("")
        stats_table = self._generate_detailed_statistics_table()
        report.append("```")
        report.append(stats_table)
        report.append("```")
        report.append("")

        # Scenario Analysis
        report.append("## 📋 Scenario Performance Analysis")
        report.append("")
        scenario_table = self._generate_scenario_analysis_table()
        report.append("```")
        report.append(scenario_table)
        report.append("```")
        report.append("")

        # Regional Deep Dive
        report.append("## 🔍 Regional Analysis")
        for region, data in self.results["regions"].items():
            if data.get("connection_status") == "connected":
                report.extend(self._generate_regional_deep_dive(region, data))

        # Quality Assessment
        report.append("## 📈 Quality Assessment")
        report.extend(self._generate_quality_assessment())

        # Recommendations
        report.append("## 💡 Production Recommendations")
        report.extend(self._generate_production_recommendations())

        # Error Analysis
        report.append("## ⚠️ Error Analysis")
        report.extend(self._generate_error_analysis())

        return "\n".join(report)

    def _generate_performance_rankings(self):
        """Generate performance rankings table"""
        rankings = []
        
        for region, data in self.results["regions"].items():
            if data.get("connection_status") == "connected":
                summary = data.get("region_summary", {})
                if summary.get("avg_ttfb") is not None:
                    rankings.append({
                        "region": region,
                        "avg_ttfb": summary["avg_ttfb"],
                        "success_rate": summary["success_rate"],
                        "quality_score": summary["quality_score"]
                    })
        
        # Sort by average TTFB (ascending - faster is better)
        rankings.sort(key=lambda x: x["avg_ttfb"])
        
        ranking_text = []
        for i, rank in enumerate(rankings, 1):
            if rank["avg_ttfb"] < 3.0:
                emoji = "🚀"
            elif rank["avg_ttfb"] < 5.0:
                emoji = "✅"
            elif rank["avg_ttfb"] < 7.0:
                emoji = "⚠️"
            else:
                emoji = "🐌"
                
            ranking_text.append(f"{i}. {emoji} **{rank['region']}**: {rank['avg_ttfb']:.3f}s "
                              f"(Success: {rank['success_rate']:.1%}, Quality: {rank['quality_score']:.2f})")
        
        return "\n".join(ranking_text) if ranking_text else "No successful measurements to rank."

    def _generate_detailed_statistics_table(self):
        """Generate comprehensive statistics table"""
        headers = ["Region", "Avg TTFB (s)", "Min (s)", "Max (s)", "Std Dev", "Success Rate", "Quality", "Status"]
        table_data = []
        
        for region, data in self.results["regions"].items():
            if data.get("connection_status") == "connected":
                summary = data.get("region_summary", {})
                if summary.get("avg_ttfb") is not None:
                    table_data.append([
                        region,
                        f"{summary['avg_ttfb']:.3f}",
                        f"{summary['min_ttfb']:.3f}",
                        f"{summary['max_ttfb']:.3f}",
                        f"{summary['std_ttfb']:.3f}",
                        f"{summary['success_rate']:.1%}",
                        f"{summary['quality_score']:.2f}",
                        "✅ Operational"
                    ])
                else:
                    table_data.append([
                        region, "Failed", "Failed", "Failed", "N/A", "0%", "0.00", "❌ Failed"
                    ])
            else:
                table_data.append([
                    region, "No Connection", "N/A", "N/A", "N/A", "0%", "0.00", "❌ Connection Failed"
                ])
        
        return tabulate(table_data, headers=headers, tablefmt="grid")

    def _generate_scenario_analysis_table(self):
        """Generate scenario performance analysis"""
        from tests.test_scenarios import TestScenarios
        
        headers = ["Region", "Scenario", "Category", "Avg TTFB (s)", "Success Rate", "Consistency"]
        table_data = []
        
        for region, data in self.results["regions"].items():
            if data.get("connection_status") != "connected":
                continue
                
            for scenario_name, stats in data.get("scenarios", {}).items():
                scenario = next((s for s in TestScenarios.get_all_scenarios() 
                               if s["name"] == scenario_name), {})
                category = scenario.get("category", "unknown")
                
                if stats.get("success_rate", 0) > 0:
                    table_data.append([
                        region,
                        scenario_name,
                        category,
                        f"{stats['avg_ttfb']:.3f}",
                        f"{stats['success_rate']:.1%}",
                        f"{stats['consistency_score']:.2f}"
                    ])
        
        return tabulate(table_data, headers=headers, tablefmt="grid")

    def _generate_regional_deep_dive(self, region, data):
        """Generate detailed analysis for specific region"""
        summary = data.get("region_summary", {})
        report = []
        
        report.append(f"### {region}")
        
        if summary.get("avg_ttfb") is not None:
            report.append(f"- **Average TTFB**: {summary['avg_ttfb']:.3f} seconds")
            report.append(f"- **Performance Range**: {summary['min_ttfb']:.3f}s - {summary['max_ttfb']:.3f}s")
            report.append(f"- **Consistency (Lower = Better)**: σ = {summary['std_ttfb']:.3f}s")
            report.append(f"- **Reliability**: {summary['success_rate']:.1%} success rate")
            report.append(f"- **Total Measurements**: {summary['total_measurements']}")
            report.append(f"- **Quality Score**: {summary['quality_score']:.2f}/1.00")
            
            # Performance categorization
            avg_ttfb = summary['avg_ttfb']
            if avg_ttfb < 3.0:
                assessment = "🚀 **Excellent** - Recommended for production"
            elif avg_ttfb < 5.0:
                assessment = "✅ **Good** - Suitable for production"
            elif avg_ttfb < 7.0:
                assessment = "⚠️ **Average** - Consider as backup"
            else:
                assessment = "🐌 **Poor** - Not recommended"
                
            report.append(f"- **Assessment**: {assessment}")
        else:
            report.append("- **Status**: ❌ No successful measurements")
        
        report.append("")
        return report

    def _generate_quality_assessment(self):
        """Generate overall quality assessment"""
        global_stats = self.results.get("global_stats", {})
        report = []
        
        if global_stats.get("total_successful_measurements", 0) > 0:
            total_measurements = global_stats["total_successful_measurements"]
            avg_ttfb = global_stats.get("global_avg_ttfb", 0)
            std_ttfb = global_stats.get("global_std_ttfb", 0)
            
            report.append(f"- **Data Quality**: {total_measurements} successful measurements")
            report.append(f"- **Global Consistency**: σ = {std_ttfb:.3f}s across all regions")
            report.append(f"- **Performance Spread**: {global_stats.get('performance_range_seconds', 0):.3f}s between fastest and slowest")
            
            # Calculate coefficient of variation for consistency assessment
            cv = (std_ttfb / avg_ttfb) * 100 if avg_ttfb > 0 else 0
            if cv < 20:
                consistency = "High consistency across regions"
            elif cv < 40:
                consistency = "Moderate consistency across regions"
            else:
                consistency = "High variability across regions"
                
            report.append(f"- **Regional Consistency**: {consistency} (CV: {cv:.1f}%)")
        else:
            report.append("- **Data Quality**: Insufficient data for quality assessment")
        
        report.append("")
        return report

    def _generate_production_recommendations(self):
        """Generate production deployment recommendations"""
        report = []
        global_stats = self.results.get("global_stats", {})
        
        if global_stats.get("fastest_region"):
            # Get top 3 performing regions
            rankings = []
            for region, data in self.results["regions"].items():
                if data.get("connection_status") == "connected":
                    summary = data.get("region_summary", {})
                    if summary.get("avg_ttfb") is not None:
                        rankings.append((region, summary["avg_ttfb"], summary["quality_score"]))
            
            rankings.sort(key=lambda x: x[1])  # Sort by TTFB
            
            if len(rankings) >= 3:
                report.append("### Tier 1 (Primary Production)")
                for i, (region, ttfb, quality) in enumerate(rankings[:3], 1):
                    report.append(f"{i}. **{region}**: {ttfb:.3f}s avg TTFB (Quality: {quality:.2f})")
                
                report.append("")
                report.append("### Load Balancing Strategy")
                report.append(f"- **Primary**: {rankings[0][0]} ({rankings[0][1]:.3f}s)")
                report.append(f"- **Secondary**: {rankings[1][0]} ({rankings[1][1]:.3f}s)")
                report.append(f"- **Tertiary**: {rankings[2][0]} ({rankings[2][1]:.3f}s)")
                
                if len(rankings) > 3:
                    report.append("")
                    report.append("### Backup Regions")
                    for region, ttfb, quality in rankings[3:]:
                        report.append(f"- {region}: {ttfb:.3f}s")
            else:
                report.append("### Available Regions")
                for region, ttfb, quality in rankings:
                    report.append(f"- **{region}**: {ttfb:.3f}s")
        else:
            report.append("- **No performance data available for recommendations**")
        
        report.append("")
        return report

    def _generate_error_analysis(self):
        """Generate error analysis"""
        report = []
        has_errors = False
        
        for region, data in self.results["regions"].items():
            errors = data.get("errors", {})
            if errors:
                has_errors = True
                error_count = sum(len(error_list) if isinstance(error_list, list) else 1 for error_list in errors.values())
                report.append(f"- **{region}**: {error_count} errors across {len(errors)} scenarios")
                
                # Detail specific error scenarios
                for scenario, error_info in errors.items():
                    if isinstance(error_info, list):
                        report.append(f"  - {scenario}: {len(error_info)} failures")
                    else:
                        report.append(f"  - {scenario}: {error_info} failures")
        
        if not has_errors:
            report.append("- **Status**: ✅ No errors detected across all regions and scenarios")
        
        report.append("")
        return report

    def save_report(self):
        """Save comprehensive report to file"""
        content = self.generate_comprehensive_report()
        filename = f"{Config.REPORTS_DIR}/ttfb_analysis_report_{datetime.now():%Y%m%d_%H%M%S}.md"
        
        with open(filename, "w") as f:
            f.write(content)
        
        return filename
