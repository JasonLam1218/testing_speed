# Multi-Deployment Gemini API Performance Analysis
**Generated**: 2025-08-05 23:22:23

## Executive Summary

- **Recommended Deployment**: Serverless Function
- **Average Response Time**: 9.010 seconds
- **Success Rate**: 100.0%
- **Reasoning**: Best balance of speed and reliability

## Test Configuration
- **Test Start**: 2025-08-05T23:10:27.282885
- **Test Duration**: 716.7 seconds
- **Deployment Methods**: Edge Function, Serverless Function, SOCKS5 Proxy
- **Scenarios Tested**: 6
- **Iterations per Scenario**: 1
- **Test Mode**: both

## 🏆 Performance Rankings

1. 🐌 **Serverless Function**: 9.010s avg (Success: 100.0%)
2. 🐌 **Edge Function**: 10.260s avg (Success: 100.0%)
3. 🐌 **SOCKS5 Proxy**: 11.285s avg (Success: 62.5%)

## 📊 Deployment Method Comparison

```
+---------------------+----------------+-----------+-----------+----------------+----------------+---------------+
| Method              |   Avg Time (s) |   Min (s) |   Max (s) | Success Rate   |   Measurements | Status        |
+=====================+================+===========+===========+================+================+===============+
| Edge Function       |         10.26  |     0.851 |    15.801 | 100.0%         |              6 | ✅ Operational |
+---------------------+----------------+-----------+-----------+----------------+----------------+---------------+
| Serverless Function |          9.01  |     1.206 |    11.738 | 100.0%         |              6 | ✅ Operational |
+---------------------+----------------+-----------+-----------+----------------+----------------+---------------+
| SOCKS5 Proxy        |         11.285 |     3.471 |    16.977 | 62.5%          |              0 | ✅ Operational |
+---------------------+----------------+-----------+-----------+----------------+----------------+---------------+
```

## 📋 Scenario Performance Analysis

```
+---------------------+------------+-----------------+--------------+----------+---------------------+
| Scenario            | Category   | Edge Function   | Serverless   | SOCKS5   | Best Method         |
+=====================+============+=================+==============+==========+=====================+
| Code Generation     | Medium     | 12.560s         | 10.449s      | Failed   | Serverless Function |
+---------------------+------------+-----------------+--------------+----------+---------------------+
| Long Essay          | Complex    | 15.801s         | 11.377s      | Failed   | Serverless Function |
+---------------------+------------+-----------------+--------------+----------+---------------------+
| Medium Analysis     | Medium     | 13.088s         | 11.738s      | Failed   | Serverless Function |
+---------------------+------------+-----------------+--------------+----------+---------------------+
| Quick Math          | Simple     | 0.851s          | 1.206s       | Failed   | Edge Function       |
+---------------------+------------+-----------------+--------------+----------+---------------------+
| Short Explanation   | Simple     | 4.642s          | 7.601s       | Failed   | Edge Function       |
+---------------------+------------+-----------------+--------------+----------+---------------------+
| Technical Deep Dive | Complex    | 14.615s         | 11.691s      | Failed   | Serverless Function |
+---------------------+------------+-----------------+--------------+----------+---------------------+
```

## 🔍 Method Analysis
### Edge Function
- **Average Response Time**: 10.260 seconds
- **Performance Range**: 0.851s - 15.801s
- **Reliability**: 100.0% success rate
- **Total Measurements**: 6
- **Assessment**: 🐌 **Poor** - Not recommended

### Serverless Function
- **Average Response Time**: 9.010 seconds
- **Performance Range**: 1.206s - 11.738s
- **Reliability**: 100.0% success rate
- **Total Measurements**: 6
- **Assessment**: 🐌 **Poor** - Not recommended
- **Cold Start Rate**: 66.7%

### SOCKS5 Proxy
- **Average Response Time**: 11.285 seconds
- **Performance Range**: 3.471s - 16.977s
- **Reliability**: 62.5% success rate
- **Total Measurements**: 0
- **Assessment**: 🐌 **Poor** - Not recommended
- **Regions Tested**: 5

## 💡 Deployment Recommendations
### Primary Recommendation
**Deploy using Serverless Function**
- Average response time: 9.010 seconds
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
- **Total Performance Data**: 42 measurements across 3 methods
- **Overall Average**: 10.813 seconds
- **Performance Spread**: 2.275 seconds between fastest and slowest methods
- **Consistency**: High variability across methods (CV: 43.5%)

## ⚠️ Error Analysis
- **Status**: ✅ No errors detected across all deployment methods
