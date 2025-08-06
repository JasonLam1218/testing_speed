# Multi-Deployment Gemini API Performance Analysis
**Generated**: 2025-08-06 00:22:17

## Executive Summary

- **Recommended Deployment**: Serverless Function
- **Average Response Time**: 9.411 seconds
- **Success Rate**: 100.0%
- **Reasoning**: Best balance of speed and reliability

## Test Configuration
- **Test Start**: 2025-08-06T00:09:56.254698
- **Test Duration**: 740.8 seconds
- **Deployment Methods**: Edge Function, Serverless Function, SOCKS5 Proxy
- **Scenarios Tested**: 6
- **Iterations per Scenario**: 1
- **Test Mode**: both

## 🏆 Performance Rankings

1. 🐌 **Serverless Function**: 9.411s avg (Success: 100.0%)
2. 🐌 **Edge Function**: 10.108s avg (Success: 100.0%)
3. 🐌 **SOCKS5 Proxy**: 11.524s avg (Success: 64.6%)

## 📊 Deployment Method Comparison

```
+---------------------+----------------+-----------+-----------+----------------+----------------+---------------+
| Method              |   Avg Time (s) |   Min (s) |   Max (s) | Success Rate   |   Measurements | Status        |
+=====================+================+===========+===========+================+================+===============+
| Edge Function       |         10.108 |     1.063 |    15.507 | 100.0%         |              6 | ✅ Operational |
+---------------------+----------------+-----------+-----------+----------------+----------------+---------------+
| Serverless Function |          9.411 |     0.867 |    13.009 | 100.0%         |              6 | ✅ Operational |
+---------------------+----------------+-----------+-----------+----------------+----------------+---------------+
| SOCKS5 Proxy        |         11.524 |     4.633 |    17.137 | 64.6%          |              0 | ✅ Operational |
+---------------------+----------------+-----------+-----------+----------------+----------------+---------------+
```

## 📋 Scenario Performance Analysis

```
+---------------------+------------+-----------------+--------------+----------+---------------------+
| Scenario            | Category   | Edge Function   | Serverless   | SOCKS5   | Best Method         |
+=====================+============+=================+==============+==========+=====================+
| Code Generation     | Medium     | 11.686s         | 10.898s      | 14.358s  | Serverless Function |
+---------------------+------------+-----------------+--------------+----------+---------------------+
| Long Essay          | Complex    | 12.975s         | 12.741s      | 13.123s  | Serverless Function |
+---------------------+------------+-----------------+--------------+----------+---------------------+
| Medium Analysis     | Medium     | 13.865s         | 13.009s      | 14.331s  | Serverless Function |
+---------------------+------------+-----------------+--------------+----------+---------------------+
| Quick Math          | Simple     | 1.063s          | 0.867s       | 5.584s   | Serverless Function |
+---------------------+------------+-----------------+--------------+----------+---------------------+
| Short Explanation   | Simple     | 5.549s          | 7.249s       | 7.142s   | Edge Function       |
+---------------------+------------+-----------------+--------------+----------+---------------------+
| Technical Deep Dive | Complex    | 15.507s         | 11.702s      | 16.151s  | Serverless Function |
+---------------------+------------+-----------------+--------------+----------+---------------------+
```

## 🔍 Method Analysis
### Edge Function
- **Average Response Time**: 10.108 seconds
- **Performance Range**: 1.063s - 15.507s
- **Reliability**: 100.0% success rate
- **Total Measurements**: 6
- **Assessment**: 🐌 **Poor** - Not recommended

### Serverless Function
- **Average Response Time**: 9.411 seconds
- **Performance Range**: 0.867s - 13.009s
- **Reliability**: 100.0% success rate
- **Total Measurements**: 6
- **Assessment**: 🐌 **Poor** - Not recommended
- **Cold Start Rate**: 66.7%

### SOCKS5 Proxy
- **Average Response Time**: 11.524 seconds
- **Performance Range**: 4.633s - 17.137s
- **Reliability**: 64.6% success rate
- **Total Measurements**: 0
- **Assessment**: 🐌 **Poor** - Not recommended
- **Regions Tested**: 6

## 💡 Deployment Recommendations
### Primary Recommendation
**Deploy using Serverless Function**
- Average response time: 9.411 seconds
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
- **Total Performance Data**: 43 measurements across 3 methods
- **Overall Average**: 11.031 seconds
- **Performance Spread**: 2.113 seconds between fastest and slowest methods
- **Consistency**: Moderate consistency across methods (CV: 39.9%)

## ⚠️ Error Analysis
- **Status**: ✅ No errors detected across all deployment methods
