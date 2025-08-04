# Gemini API Time To First Byte (TTFB) Analysis Report
**Generated**: 2025-08-04 18:12:07

## Executive Summary

- **Best Performing Region**: atlanta.us
- **Worst Performing Region**: phoenix.us
- **Performance Gap**: 0.333 seconds
- **Global Average TTFB**: 13.222 seconds
- **Total Measurements**: 48
- **Regions Successfully Tested**: 4

## Test Configuration
- **Test Start**: 2025-08-04T17:56:01.726856
- **Test Duration**: 965.3 seconds
- **Iterations per Scenario**: 2
- **Scenarios Tested**: 6
- **Measurement Focus**: Time To First Byte (TTFB)

**Important Note**: For Gemini API, TTFB represents the time until response generation is complete, as the API generates full responses before sending any data.

## 🏆 Regional Performance Rankings

1. 🐌 **atlanta.us**: 13.048s (Success: 100.0%, Quality: 0.15)
2. 🐌 **new-york.us**: 13.100s (Success: 100.0%, Quality: 0.17)
3. 🐌 **los-angeles.us**: 13.358s (Success: 100.0%, Quality: 0.16)
4. 🐌 **phoenix.us**: 13.381s (Success: 100.0%, Quality: 0.16)

## 📊 Detailed Performance Statistics

```
+------------------+----------------+-----------+-----------+-----------+----------------+-----------+---------------------+
| Region           | Avg TTFB (s)   | Min (s)   | Max (s)   | Std Dev   | Success Rate   |   Quality | Status              |
+==================+================+===========+===========+===========+================+===========+=====================+
| los-angeles.us   | 13.358         | 5.255     | 21.847    | 5.312     | 100.0%         |      0.16 | ✅ Operational       |
+------------------+----------------+-----------+-----------+-----------+----------------+-----------+---------------------+
| new-york.us      | 13.100         | 4.751     | 19.530    | 5.013     | 100.0%         |      0.17 | ✅ Operational       |
+------------------+----------------+-----------+-----------+-----------+----------------+-----------+---------------------+
| atlanta.us       | 13.048         | 5.068     | 20.172    | 5.483     | 100.0%         |      0.15 | ✅ Operational       |
+------------------+----------------+-----------+-----------+-----------+----------------+-----------+---------------------+
| chicago.us       | No Connection  | N/A       | N/A       | N/A       | 0%             |      0    | ❌ Connection Failed |
+------------------+----------------+-----------+-----------+-----------+----------------+-----------+---------------------+
| phoenix.us       | 13.381         | 3.881     | 19.118    | 5.334     | 100.0%         |      0.16 | ✅ Operational       |
+------------------+----------------+-----------+-----------+-----------+----------------+-----------+---------------------+
| san-francisco.us | No Connection  | N/A       | N/A       | N/A       | 0%             |      0    | ❌ Connection Failed |
+------------------+----------------+-----------+-----------+-----------+----------------+-----------+---------------------+
| amsterdam.nl     | No Connection  | N/A       | N/A       | N/A       | 0%             |      0    | ❌ Connection Failed |
+------------------+----------------+-----------+-----------+-----------+----------------+-----------+---------------------+
| stockholm.se     | No Connection  | N/A       | N/A       | N/A       | 0%             |      0    | ❌ Connection Failed |
+------------------+----------------+-----------+-----------+-----------+----------------+-----------+---------------------+
```

## 📋 Scenario Performance Analysis

```
+----------------+---------------------+------------+----------------+----------------+---------------+
| Region         | Scenario            | Category   |   Avg TTFB (s) | Success Rate   |   Consistency |
+================+=====================+============+================+================+===============+
| los-angeles.us | Quick Math          | simple     |          5.655 | 100.0%         |          0.75 |
+----------------+---------------------+------------+----------------+----------------+---------------+
| los-angeles.us | Short Explanation   | simple     |          9.562 | 100.0%         |          0.14 |
+----------------+---------------------+------------+----------------+----------------+---------------+
| los-angeles.us | Medium Analysis     | medium     |         15.265 | 100.0%         |          0.32 |
+----------------+---------------------+------------+----------------+----------------+---------------+
| los-angeles.us | Code Generation     | medium     |         15.195 | 100.0%         |          0.25 |
+----------------+---------------------+------------+----------------+----------------+---------------+
| los-angeles.us | Long Essay          | complex    |         14.928 | 100.0%         |          0.28 |
+----------------+---------------------+------------+----------------+----------------+---------------+
| los-angeles.us | Technical Deep Dive | complex    |         19.545 | 100.0%         |          0.24 |
+----------------+---------------------+------------+----------------+----------------+---------------+
| new-york.us    | Quick Math          | simple     |          4.911 | 100.0%         |          0.81 |
+----------------+---------------------+------------+----------------+----------------+---------------+
| new-york.us    | Short Explanation   | simple     |          9.492 | 100.0%         |          0.35 |
+----------------+---------------------+------------+----------------+----------------+---------------+
| new-york.us    | Medium Analysis     | medium     |         16.084 | 100.0%         |          0.34 |
+----------------+---------------------+------------+----------------+----------------+---------------+
| new-york.us    | Code Generation     | medium     |         15.582 | 100.0%         |          0.24 |
+----------------+---------------------+------------+----------------+----------------+---------------+
| new-york.us    | Long Essay          | complex    |         14.635 | 100.0%         |          0.22 |
+----------------+---------------------+------------+----------------+----------------+---------------+
| new-york.us    | Technical Deep Dive | complex    |         17.897 | 100.0%         |          0.3  |
+----------------+---------------------+------------+----------------+----------------+---------------+
| atlanta.us     | Quick Math          | simple     |          5.155 | 100.0%         |          0.89 |
+----------------+---------------------+------------+----------------+----------------+---------------+
| atlanta.us     | Short Explanation   | simple     |          7.575 | 100.0%         |          0.27 |
+----------------+---------------------+------------+----------------+----------------+---------------+
| atlanta.us     | Medium Analysis     | medium     |         15.66  | 100.0%         |          0.22 |
+----------------+---------------------+------------+----------------+----------------+---------------+
| atlanta.us     | Code Generation     | medium     |         15.089 | 100.0%         |          0.38 |
+----------------+---------------------+------------+----------------+----------------+---------------+
| atlanta.us     | Long Essay          | complex    |         16.925 | 100.0%         |          0.18 |
+----------------+---------------------+------------+----------------+----------------+---------------+
| atlanta.us     | Technical Deep Dive | complex    |         17.883 | 100.0%         |          0.35 |
+----------------+---------------------+------------+----------------+----------------+---------------+
| phoenix.us     | Quick Math          | simple     |          6.779 | 100.0%         |          0.51 |
+----------------+---------------------+------------+----------------+----------------+---------------+
| phoenix.us     | Short Explanation   | simple     |          7.305 | 100.0%         |          0.17 |
+----------------+---------------------+------------+----------------+----------------+---------------+
| phoenix.us     | Medium Analysis     | medium     |         16.471 | 100.0%         |          0.35 |
+----------------+---------------------+------------+----------------+----------------+---------------+
| phoenix.us     | Code Generation     | medium     |         15.825 | 100.0%         |          0.2  |
+----------------+---------------------+------------+----------------+----------------+---------------+
| phoenix.us     | Long Essay          | complex    |         15.443 | 100.0%         |          0.2  |
+----------------+---------------------+------------+----------------+----------------+---------------+
| phoenix.us     | Technical Deep Dive | complex    |         18.463 | 100.0%         |          0.52 |
+----------------+---------------------+------------+----------------+----------------+---------------+
```

## 🔍 Regional Analysis
### los-angeles.us
- **Average TTFB**: 13.358 seconds
- **Performance Range**: 5.255s - 21.847s
- **Consistency (Lower = Better)**: σ = 5.312s
- **Reliability**: 100.0% success rate
- **Total Measurements**: 12
- **Quality Score**: 0.16/1.00
- **Assessment**: 🐌 **Poor** - Not recommended

### new-york.us
- **Average TTFB**: 13.100 seconds
- **Performance Range**: 4.751s - 19.530s
- **Consistency (Lower = Better)**: σ = 5.013s
- **Reliability**: 100.0% success rate
- **Total Measurements**: 12
- **Quality Score**: 0.17/1.00
- **Assessment**: 🐌 **Poor** - Not recommended

### atlanta.us
- **Average TTFB**: 13.048 seconds
- **Performance Range**: 5.068s - 20.172s
- **Consistency (Lower = Better)**: σ = 5.483s
- **Reliability**: 100.0% success rate
- **Total Measurements**: 12
- **Quality Score**: 0.15/1.00
- **Assessment**: 🐌 **Poor** - Not recommended

### phoenix.us
- **Average TTFB**: 13.381 seconds
- **Performance Range**: 3.881s - 19.118s
- **Consistency (Lower = Better)**: σ = 5.334s
- **Reliability**: 100.0% success rate
- **Total Measurements**: 12
- **Quality Score**: 0.16/1.00
- **Assessment**: 🐌 **Poor** - Not recommended

## 📈 Quality Assessment
- **Data Quality**: 48 successful measurements
- **Global Consistency**: σ = 5.119s across all regions
- **Performance Spread**: 0.333s between fastest and slowest
- **Regional Consistency**: Moderate consistency across regions (CV: 38.7%)

## 💡 Production Recommendations
### Tier 1 (Primary Production)
1. **atlanta.us**: 13.048s avg TTFB (Quality: 0.15)
2. **new-york.us**: 13.100s avg TTFB (Quality: 0.17)
3. **los-angeles.us**: 13.358s avg TTFB (Quality: 0.16)

### Load Balancing Strategy
- **Primary**: atlanta.us (13.048s)
- **Secondary**: new-york.us (13.100s)
- **Tertiary**: los-angeles.us (13.358s)

### Backup Regions
- phoenix.us: 13.381s

## ⚠️ Error Analysis
- **Status**: ✅ No errors detected across all regions and scenarios
