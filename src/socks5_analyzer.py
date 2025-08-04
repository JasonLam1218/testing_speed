from tabulate import tabulate
from datetime import datetime
from config.settings import Config

class SOCKS5RegionalAnalyzer:
    def __init__(self, results):
        self.r = results
        self.ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def generate_analysis(self):
        info = self.r.get("info", {})
        
        md = []
        md.append("# Gemini API Speed Test Report")
        md.append(f"Generated on: {self.ts}")
        md.append("")
        md.append("")
        md.append("## Test Configuration")
        md.append(f"- **Start Time**: {info.get('start', 'N/A')}")
        md.append(f"- **End Time**: {info.get('end', 'N/A')}")
        md.append(f"- **Total Duration**: {info.get('duration', 0):.2f} seconds")
        md.append(f"- **Iterations per Test**: {info.get('iterations', 'N/A')}")
        md.append("")
        md.append("")

        # Find best performing region
        best_region = None
        best_avg = float('inf')
        for region, data in self.r["regions"].items():
            if data.get("connected") and data["summary"]["avg_response"]:
                if data["summary"]["avg_response"] < best_avg:
                    best_avg = data["summary"]["avg_response"]
                    best_region = region

        md.append("## 🏆 Key Results")
        md.append(f"- **Best Overall Method**: socks5_{best_region}" if best_region else "- **Best Overall Method**: None (all failed)")
        md.append(f"- **Best SOCKS5 Region**: {best_region}" if best_region else "- **Best SOCKS5 Region**: None")
        md.append("")
        md.append("")
        md.append("## 📋 Recommendations")
        if best_region:
            md.append(f"- Use SOCKS5 proxy ({best_region}) - Vercel endpoint failed")
        else:
            md.append("- All SOCKS5 proxies failed - consider checking credentials and network connectivity")
        md.append("")
        md.append("")

        # Detailed Performance Comparison Table
        md.append("## 📊 Detailed Performance Comparison")
        
        # Build table data
        table_data = []
        for region, data in self.r["regions"].items():
            for scenario_name, stats in data.get("scenarios", {}).items():
                from tests.test_scenarios import TestScenarios
                scenario = next((s for s in TestScenarios.get_all_scenarios() if s["name"] == scenario_name), {})
                category = scenario.get("category", "unknown")
                
                if stats["success_rate"] > 0:
                    table_data.append([
                        "SOCKS5",
                        region,
                        scenario_name,
                        category,
                        f"{stats['avg']:.3f}",
                        f"{stats['success_rate']:.1%}",
                        f"{stats['min']:.3f}",
                        f"{stats['max']:.3f}"
                    ])
                else:
                    table_data.append([
                        "SOCKS5",
                        region,
                        scenario_name,
                        category,
                        "Failed",
                        "0%",
                        "N/A",
                        "N/A"
                    ])

        headers = ["Method", "Region", "Scenario", "Category", "Avg Time (s)", "Success Rate", "Min Time (s)", "Max Time (s)"]
        table = tabulate(table_data, headers=headers, tablefmt="grid")
        
        md.append("```")
        md.append(table)
        md.append("```")
        md.append("")
        md.append("")

        # SOCKS5 Regional Performance
        md.append("## 🔄 SOCKS5 Regional Performance")
        for region, data in self.r["regions"].items():
            if data.get("connected"):
                summary = data["summary"]
                md.append(f"### {region}")
                if summary["avg_response"]:
                    md.append(f"- **Average Response Time**: {summary['avg_response']:.3f} seconds")
                    md.append(f"- **Average Success Rate**: {summary['success_rate']:.1%}")
                else:
                    md.append("- **Average Response Time**: Failed")
                    md.append("- **Average Success Rate**: 0.0%")
                md.append(f"- **Scenarios Tested**: {summary['successful_scenarios']}")
                md.append("")

        # Error Analysis
        md.append("")
        md.append("## ⚠️ Error Analysis")
        md.append("### SOCKS5 Errors")
        
        for region, data in self.r["regions"].items():
            errors = data.get("errors", {})
            if errors:
                error_details = []
                for scenario, count in errors.items():
                    error_details.append(f"{scenario}: {count}")
                md.append(f"- **{region}**: {', '.join(error_details)}")

        return "\n".join(md)

    def save(self):
        content = self.generate_analysis()
        fn = f"{Config.REPORTS_DIR}/gemini_speed_test_report_{datetime.now():%Y%m%d_%H%M%S}.md"
        with open(fn, "w") as f:
            f.write(content)
        return fn
