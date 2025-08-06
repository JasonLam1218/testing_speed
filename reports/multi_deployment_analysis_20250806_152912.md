# Multi-Deployment Gemini API Performance Analysis
**Generated**: 2025-08-06 15:29:12

## Executive Summary

- **Recommended Deployment**: Serverless Function
- **Average Response Time**: 9.464 seconds
- **Success Rate**: 100.0%
- **Reasoning**: Best balance of speed and reliability

### Streaming Performance Highlights
- No streaming data available

## Test Configuration
- **Test Start**: 2025-08-06T15:11:02.439392
- **Test Duration**: 1089.6 seconds
- **Deployment Methods**: Edge Function, Serverless Function, SOCKS5 Proxy
- **Scenarios Tested**: 6
- **Iterations per Scenario**: 1
- **Test Mode**: both

## 🏆 Performance Rankings

1. ✅ **Serverless Function**: 9.464s avg (Success: 100.0%)
2. ✅ **Edge Function**: 11.522s avg (Success: 100.0%)
3. ✅ **SOCKS5 Proxy**: 11.563s avg (Success: 100.0%)

## 📊 Deployment Method Comparison

```
+---------------------+----------------+-----------+-----------+----------------+----------------+----------------+---------------+
| Method              |   Avg Time (s) |   Min (s) |   Max (s) | Avg TTFB (s)   | Success Rate   |   Measurements | Status        |
+=====================+================+===========+===========+================+================+================+===============+
| Edge Function       |         11.522 |     1.785 |    16.36  | 11.614         | 100.0%         |              6 | ✅ Operational |
+---------------------+----------------+-----------+-----------+----------------+----------------+----------------+---------------+
| Serverless Function |          9.464 |     1.281 |    12.46  | 9.123          | 100.0%         |              6 | ✅ Operational |
+---------------------+----------------+-----------+-----------+----------------+----------------+----------------+---------------+
| SOCKS5 Proxy        |         11.563 |     2.57  |    18.947 | N/A            | 100.0%         |             48 | ✅ Operational |
+---------------------+----------------+-----------+-----------+----------------+----------------+----------------+---------------+
```

## 📋 Scenario Performance Analysis

```
+---------------------+------------+-----------------+--------------+----------+---------------------+
| Scenario            | Category   | Edge Function   | Serverless   | SOCKS5   | Best Method         |
+=====================+============+=================+==============+==========+=====================+
| Code Generation     | Medium     | 13.516s         | 10.439s      | 15.077s  | Serverless Function |
+---------------------+------------+-----------------+--------------+----------+---------------------+
| Long Essay          | Complex    | 14.296s         | 12.211s      | 13.626s  | Serverless Function |
+---------------------+------------+-----------------+--------------+----------+---------------------+
| Medium Analysis     | Medium     | 14.103s         | 12.396s      | 13.849s  | Serverless Function |
+---------------------+------------+-----------------+--------------+----------+---------------------+
| Quick Math          | Simple     | 1.785s          | 1.281s       | 3.278s   | Serverless Function |
+---------------------+------------+-----------------+--------------+----------+---------------------+
| Short Explanation   | Simple     | 9.074s          | 7.996s       | 6.776s   | SOCKS5 Proxy        |
+---------------------+------------+-----------------+--------------+----------+---------------------+
| Technical Deep Dive | Complex    | 16.360s         | 12.460s      | 16.772s  | Serverless Function |
+---------------------+------------+-----------------+--------------+----------+---------------------+
```

## ⚡ Streaming & TTFB Analysis

No streaming data available for analysis.

## 🔍 Method Analysis
### Edge Function
- **Average Response Time**: 11.522 seconds
- **Performance Range**: 1.785s - 16.360s
- **Reliability**: 100.0% success rate
- **Total Measurements**: 6
- **Average TTFB**: 11.614 seconds
- **TTFB Percentage**: 100.8% of total time
- **Assessment**: ✅ **Good** - Suitable for production

### Serverless Function
- **Average Response Time**: 9.464 seconds
- **Performance Range**: 1.281s - 12.460s
- **Reliability**: 100.0% success rate
- **Total Measurements**: 6
- **Average TTFB**: 9.123 seconds
- **TTFB Percentage**: 96.4% of total time
- **Assessment**: ✅ **Good** - Suitable for production
- **Cold Start Rate**: 0.0%

### SOCKS5 Proxy
- **Average Response Time**: 11.563 seconds
- **Performance Range**: 2.570s - 18.947s
- **Reliability**: 100.0% success rate
- **Total Measurements**: 0
- **Assessment**: ✅ **Good** - Suitable for production
- **Regions Tested**: 8

## 💡 Deployment Recommendations
### Primary Recommendation
**Deploy using Serverless Function**
- Average response time: 9.464 seconds
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
- **Total Performance Data**: 60 measurements across 3 methods
- **Overall Average**: 11.349 seconds
- **Performance Spread**: 2.099 seconds between fastest and slowest methods
- **Consistency**: High variability across methods (CV: 43.6%)

## ⚠️ Error Analysis
- **Status**: ✅ No errors detected across all deployment methods
