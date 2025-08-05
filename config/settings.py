import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # NordVPN credentials / proxy
    NORDVPN_USERNAME = os.getenv("NORDVPN_USERNAME")
    NORDVPN_PASSWORD = os.getenv("NORDVPN_PASSWORD")
    NORDVPN_PORT = int(os.getenv("NORDVPN_PORT", "1080"))

    # Gemini API
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    TIMEOUT_SECONDS = int(os.getenv("TIMEOUT_SECONDS", "30"))

    # Test parameters (overridden via CLI)
    TEST_ITERATIONS = 1
    API_DELAY = 8

    # SOCKS5 Regional testing
    NORDVPN_REGIONS = [
        # US City-Specific Servers
        "los-angeles.us",  # Los Angeles, US
        "new-york.us",     # New York, US
        "atlanta.us",      # Atlanta, US
        "chicago.us",      # Chicago, US
        "phoenix.us",      # Phoenix, US
        "san-francisco.us", # San Francisco, US
        # European City-Specific Servers
        "amsterdam.nl",    # Amsterdam, Netherlands
        "stockholm.se",    # Stockholm, Sweden
    ]

    # Multi-deployment URLs (UPDATE THESE AFTER DEPLOYMENT)
    EDGE_FUNCTION_URL = os.getenv("EDGE_FUNCTION_URL", "https://testing-speed-hdi2hod01-jasonlam1218s-projects.vercel.app/api/edge-gemini")
    SERVERLESS_FUNCTION_URL = os.getenv("SERVERLESS_FUNCTION_URL", "https://testing-speed-hdi2hod01-jasonlam1218s-projects.vercel.app/api/serverless-gemini")

    # Deployment configurations
    DEPLOYMENT_METHODS = ["edge_function", "serverless_function", "socks5_proxy"]

    # Performance thresholds
    EXCELLENT_THRESHOLD = 3.0  # seconds
    GOOD_THRESHOLD = 5.0       # seconds
    AVERAGE_THRESHOLD = 7.0    # seconds

    # Directories
    RESULTS_DIR = os.getenv("RESULTS_DIR", "results")
    REPORTS_DIR = os.getenv("REPORTS_DIR", "reports")

    @classmethod
    def validate_config(cls):
        errors = []
        required_vars = ['NORDVPN_USERNAME', 'NORDVPN_PASSWORD', 'GEMINI_API_KEY']
        missing_vars = []
        
        for var in required_vars:
            if not getattr(cls, var):
                missing_vars.append(var)
        
        if missing_vars:
            errors.append(f"Missing env vars: {', '.join(missing_vars)}")

        # Validate deployment URLs
        if cls.EDGE_FUNCTION_URL.startswith("https://your-project"):
            errors.append("EDGE_FUNCTION_URL not configured - update after Vercel deployment")
        
        if cls.SERVERLESS_FUNCTION_URL.startswith("https://your-project"):
            errors.append("SERVERLESS_FUNCTION_URL not configured - update after Vercel deployment")

        if errors:
            raise ValueError('; '.join(errors))

    @classmethod
    def get_deployment_config(cls, method):
        """Get configuration for specific deployment method"""
        configs = {
            "edge_function": {
                "url": cls.EDGE_FUNCTION_URL,
                "name": "Edge Function",
                "expected_latency": "0.1-0.3s",
                "max_timeout": 10
            },
            "serverless_function": {
                "url": cls.SERVERLESS_FUNCTION_URL,
                "name": "Serverless Function", 
                "expected_latency": "0.3-0.8s",
                "max_timeout": 30
            },
            "socks5_proxy": {
                "url": None,
                "name": "SOCKS5 Proxy",
                "expected_latency": "0.8-2.0s", 
                "max_timeout": 30
            }
        }
        return configs.get(method, {})
