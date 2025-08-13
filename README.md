***

## 📄 README — Multi‑Deployment Gemini API Performance Testing Framework

### 1. Overview

This project is a **comprehensive benchmarking suite** designed to measure **latency**, **reliability**, and **streaming performance** of Google's **Gemini 2.5 Flash** model across multiple deployment types:

- **Vercel Edge Functions** (low‑latency, short‑duration)
- **Vercel Serverless Functions** (longer runtime, more complex workflows)
- **SOCKS5 Proxy via NordVPN** (geographic latency testing)

It allows running:

- **Total Response Time tests**
- **TTFB (Time to First Byte) tests**
- **Streaming throughput tests**
- All three above in combined form (`both` mode)

***

### 2. Directory Structure

```
.
├── config/
│   ├── settings.py           # Global config (URLs, regions, thresholds)
├── src/
│   ├── edge_function_client.py
│   ├── serverless_function_client.py
│   ├── socks5_client.py
│   ├── utils.py
├── tests/
│   ├── test_scenarios.py     # Prompt scenarios
├── main.py                   # CLI entry point
├── requirements.txt
├── results/                  # Raw logs & JSON results
├── reports/                  # Markdown reports
```


***

### 3. **Setup**

#### (1) Install Dependencies

```bash
pip install -r requirements.txt
```


#### (2) Set Environment Variables

Create a `.env` file in the root folder:

```env
# Gemini API
GEMINI_API_KEY=your_google_gemini_api_key

# NordVPN (SOCKS5)
NORDVPN_USERNAME=your_nordvpn_username
NORDVPN_PASSWORD=your_nordvpn_password
NORDVPN_PORT=1080

# Deployment URLs (Vercel deployments)
EDGE_FUNCTION_URL=https://your-vercel-edge-url.vercel.app/api/edge-gemini
SERVERLESS_FUNCTION_URL=https://your-vercel-serverless-url.vercel.app/api/serverless-gemini
```

> **Note:** You must deploy `edge-gemini.js` and `serverless-gemini.js` in your Vercel project and update their URLs in `.env`.

#### (3) Ensure Directories Exist

The tool will auto-create:

- `results/` for raw logs
- `reports/` for Markdown output

***

### 4. **Running Tests**

`main.py` is the **central test runner**.

#### **Basic Command**

```bash
python main.py
```

This:

- Runs **multi-deployment** testing across Edge, Serverless, and SOCKS5
- Benchmarks **all scenarios** (simple, medium, complex)
- Uses **total response time** test mode
- Saves full reports in `reports/`

***

#### **Important CLI Parameters**

| Parameter | Description | Example |
| :-- | :-- | :-- |
| `--deployment` | Which deployment(s) to test: `edge`, `serverless`, `socks5`, `multi` | `--deployment edge` |
| `--scenarios` | Scenario group: `simple`, `medium`, `complex`, `all` | `--scenarios medium` |
| `--iterations` | Iterations per scenario | `--iterations 3` |
| `--delay` | Delay between requests (seconds) | `--delay 5` |
| `--test-mode` | `total`, `ttfb`, `both`, `streaming` | `--test-mode both` |
| `--analysis-mode` | `basic`, `comprehensive`, `streaming` | `--analysis-mode comprehensive` |
| `--verbose` | Verbose logs | `--verbose` |
| `--save-raw` | Save raw request/response payloads | `--save-raw` |


***

### 5. **Example Commands**

#### **1) Run All Deployments (Default)**

```bash
python main.py --deployment multi --scenarios all --iterations 2 --delay 5 --test-mode total --analysis-mode comprehensive
```


#### **2) Edge Function Only, TTFB + Total**

```bash
python main.py --deployment edge --scenarios simple --iterations 3 --test-mode both
```


#### **3) Serverless Function, Complex Prompts, Streaming**

```bash
python main.py --deployment serverless --scenarios complex --iterations 1 --test-mode streaming
```


#### **4) SOCKS5 Proxy Regional Test**

```bash
python main.py --deployment socks5 --scenarios all --iterations 1 --test-mode ttfb --regions los-angeles.us amsterdam.nl
```


#### **5) Debug Mode (Verbose + Raw Output)**

```bash
python main.py --deployment multi --verbose --save-raw
```


***

### 6. **Output Files**

- **JSON results** → `results/multi_deployment_results_YYYYMMDD_HHMMSS.json`
- **Markdown report** → `reports/multi_deployment_analysis_YYYYMMDD_HHMMSS.md`
- **Logs** → `results/multi_deployment_YYYYMMDD_HHMMSS.log`

***

### 7. **Extra Notes**

- **Thinking Mode**: If you want to **disable Gemini's thinking mode**, you must modify `edge-gemini.js` and `serverless-gemini.js` to include:

```javascript
thinkingConfig: {
  thinkingBudget: 0,
  includeThoughts: false
}
```

- The `baseline validation` in `multi_deployment_test_runner.py` prevents unrealistic results (too fast or too slow).
- SOCKS5 testing requires an **active NordVPN account** with SOCKS5 credentials.

***