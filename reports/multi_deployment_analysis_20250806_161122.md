# Multi-Deployment Gemini API Performance Analysis
**Generated**: 2025-08-06 16:11:22

## Executive Summary

- **Recommended Deployment**: Serverless Function
- **Average Response Time**: 9.115 seconds
- **Success Rate**: 100.0%
- **Reasoning**: Best balance of speed and reliability

### Streaming Performance Highlights
- No streaming data available

## Test Configuration
- **Test Start**: 2025-08-06T16:06:08.196204
- **Test Duration**: 313.8 seconds
- **Deployment Methods**: Edge Function, Serverless Function, SOCKS5 Proxy
- **Scenarios Tested**: 6
- **Iterations per Scenario**: 1
- **Test Mode**: both

## 🏆 Performance Rankings

1. ✅ **Serverless Function**: 9.115s avg (Success: 100.0%)
2. ✅ **Edge Function**: 10.962s avg (Success: 100.0%)

## 📊 Deployment Method Comparison

```
+---------------------+----------------+-----------+-----------+----------------+----------------+----------------+---------------+
| Method              | Avg Time (s)   | Min (s)   | Max (s)   | Avg TTFB (s)   | Success Rate   |   Measurements | Status        |
+=====================+================+===========+===========+================+================+================+===============+
| Edge Function       | 10.962         | 1.657     | 16.349    | 11.533         | 100.0%         |              6 | ✅ Operational |
+---------------------+----------------+-----------+-----------+----------------+----------------+----------------+---------------+
| Serverless Function | 9.115          | 0.832     | 13.412    | 9.371          | 100.0%         |              6 | ✅ Operational |
+---------------------+----------------+-----------+-----------+----------------+----------------+----------------+---------------+
| SOCKS5 Proxy        | Failed         | N/A       | N/A       | N/A            | 0%             |              0 | ❌ Failed      |
+---------------------+----------------+-----------+-----------+----------------+----------------+----------------+---------------+
```

## 📋 Scenario Performance Analysis

```
+---------------------+------------+-----------------+--------------+----------+---------------------+
| Scenario            | Category   | Edge Function   | Serverless   | SOCKS5   | Best Method         |
+=====================+============+=================+==============+==========+=====================+
| Code Generation     | Medium     | 13.728s         | 10.656s      | Failed   | Serverless Function |
+---------------------+------------+-----------------+--------------+----------+---------------------+
| Long Essay          | Complex    | 14.448s         | 12.184s      | Failed   | Serverless Function |
+---------------------+------------+-----------------+--------------+----------+---------------------+
| Medium Analysis     | Medium     | 13.409s         | 13.412s      | Failed   | Edge Function       |
+---------------------+------------+-----------------+--------------+----------+---------------------+
| Quick Math          | Simple     | 1.657s          | 0.832s       | Failed   | Serverless Function |
+---------------------+------------+-----------------+--------------+----------+---------------------+
| Short Explanation   | Simple     | 6.182s          | 5.740s       | Failed   | Serverless Function |
+---------------------+------------+-----------------+--------------+----------+---------------------+
| Technical Deep Dive | Complex    | 16.349s         | 11.866s      | Failed   | Serverless Function |
+---------------------+------------+-----------------+--------------+----------+---------------------+
```

## ⚡ Streaming & TTFB Analysis

No streaming data available for analysis.

## 🔍 Method Analysis
### Edge Function
- **Total Response Time**: 10.962 seconds
- **Performance Range**: 1.657s - 16.349s
- **Reliability**: 100.0% success rate
- **Total Measurements**: 6
- **Time to First Byte (TTFB)**: 11.533 seconds
- **Processing Time**: -0.570 seconds
- **TTFB Ratio**: 105.2% of total time
- **Processing Ratio**: -5.2% of total time
- **Assessment**: ✅ **Good** - Suitable for production

### Serverless Function
- **Total Response Time**: 9.115 seconds
- **Performance Range**: 0.832s - 13.412s
- **Reliability**: 100.0% success rate
- **Total Measurements**: 6
- **Time to First Byte (TTFB)**: 9.371 seconds
- **Processing Time**: -0.256 seconds
- **TTFB Ratio**: 102.8% of total time
- **Processing Ratio**: -2.8% of total time
- **Assessment**: ✅ **Good** - Suitable for production
- **Cold Start Rate**: 0.0%

### SOCKS5 Proxy
- **Status**: ❌ No successful measurements

## 💡 Deployment Recommendations
### Primary Recommendation
**Deploy using Serverless Function**
- Average response time: 9.115 seconds
- Success rate: 100.0%
- Reasoning: Best balance of speed and reliability

## 🎯 Use Case Guidelines
### Simple Prompts (< 50 tokens)
- **Recommended**: Serverless Function
- **Use for**: Quick responses, real-time interactions

### Complex Prompts (> 200 tokens)
- **Recommended**: Edge Function
- **Use for**: Detailed analysis, content generation

### Production Workloads
- **Recommended**: Serverless Function
- **Use for**: High-volume, mission-critical applications

## 📈 Performance Insights
- **Total Performance Data**: 12 measurements across 2 methods
- **Overall Average**: 10.039 seconds
- **Performance Spread**: 1.847 seconds between fastest and slowest methods
- **Consistency**: High variability across methods (CV: 51.4%)

## ⚠️ Error Analysis
- **Status**: ✅ No errors detected across all deployment methods
