from tabulate import tabulate
from datetime import datetime
from config.settings import Config

class SOCKS5TTFBAnalyzer:
    def __init__(self, results):
        self.r = results
        self.ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def generate_analysis(self):
        info = self.r.get("info", {})
        md = []
        
        md.append("# Gemini API TTFB (First Byte) Speed Test Report")
        md.append(f"Generated on: {self.ts}")
        md.append("")
        md.append("")
        
        md.append("## Test Configuration")
        md.append(f"- **Start Time**: {info.get('start', 'N/A')}")
        md.append(f"- **End Time**: {info.get('end', 'N/A')}")
        md.append(f"- **Total Duration**: {info.get('duration', 0):.2f} seconds")
        md.append(f"- **Iterations per Test**: {info.get('iterations', 'N/A')}")
        md.append(f"- **Measurement Type**: Time To First Byte (TTFB) + Total Response Time")
        md.append("")
        md.append("")

        # Find best performing region for TTFB
        best_region = None
        best_ttfb = float('inf')
        
        for region, data in self.r["regions"].items():
            if data.get("connected") and data["summary"]["avg_ttfb"]:
                if data["summary"]["avg_ttfb"] < best_ttfb:
                    best_ttfb = data["summary"]["avg_ttfb"]
                    best_region = region

        md.append("## 🏆 Key Results")
        md.append(f"- **Best TTFB Region**: {best_region} ({best_ttfb:.3f}s)" if best_region else "- **Best TTFB Region**: None")
        md.append("")
        md.append("")
        
        md.append("## 📋 TTFB Analysis")
        if best_region:
            md.append(f"- Fastest first byte response from **{best_region}** region")
            md.append(f"- TTFB measures time until first byte is received, indicating network latency + initial processing")
            md.append(f"- Total response time includes complete content generation and transfer")
        md.append("")
        md.append("")

        # TTFB Performance Comparison Table
        md.append("## 📊 TTFB vs Total Time Comparison")
        
        table_data = []
        for region, data in self.r["regions"].items():
            for scenario_name, stats in data.get("scenarios", {}).items():
                from tests.test_scenarios import TestScenarios
                scenario = next((s for s in TestScenarios.get_all_scenarios() if s["name"] == scenario_name), {})
                category = scenario.get("category", "unknown")
                
                if stats["success_rate"] > 0:
                    processing_time = stats.get('avg_processing', stats['avg_total'] - stats['avg_ttfb'])
                    table_data.append([
                        "SOCKS5",
                        region,
                        scenario_name,
                        category,
                        f"{stats['avg_ttfb']:.3f}",
                        f"{stats['avg_total']:.3f}",
                        f"{processing_time:.3f}",  # ✅ Use calculated processing time
                        f"{stats['success_rate']:.1%}"
                    ])
                else:
                    table_data.append([
                        "SOCKS5",
                        region,
                        scenario_name,
                        category,
                        "Failed",
                        "Failed",
                        "N/A",
                        "0%"
                    ])

        headers = ["Method", "Region", "Scenario", "Category", "TTFB (s)", "Total (s)", "Processing (s)", "Success Rate"]
        table = tabulate(table_data, headers=headers, tablefmt="grid")
        md.append("```")
        md.append(table)
        md.append("```")
        md.append("")
        md.append("")

        # Regional TTFB Performance
        md.append("## 🔄 Regional TTFB Performance")
        for region, data in self.r["regions"].items():
            if data.get("connected"):
                summary = data["summary"]
                md.append(f"### {region}")
                
                if summary["avg_ttfb"]:
                    md.append(f"- **Average TTFB**: {summary['avg_ttfb']:.3f} seconds")
                    md.append(f"- **Average Total Time**: {summary['avg_total']:.3f} seconds")
                    md.append(f"- **Average Processing Time**: {(summary['avg_total'] - summary['avg_ttfb']):.3f} seconds")
                    md.append(f"- **Min TTFB**: {summary['min_ttfb']:.3f} seconds")
                    md.append(f"- **Max TTFB**: {summary['max_ttfb']:.3f} seconds")
                    md.append(f"- **Success Rate**: {summary['success_rate']:.1%}")
                else:
                    md.append("- **Status**: All requests failed")
                    
                md.append(f"- **Scenarios Tested**: {summary['successful_scenarios']}/{summary['total_scenarios']}")
                md.append("")

        # Error Analysis
        md.append("## ⚠️ Error Analysis")
        md.append("### TTFB Test Errors")
        
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
        fn = f"{Config.REPORTS_DIR}/gemini_ttfb_report_{datetime.now():%Y%m%d_%H%M%S}.md"
        with open(fn, "w") as f:
            f.write(content)
        return fn
