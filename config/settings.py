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
    TIMEOUT_SECONDS = int(os.getenv("TIMEOUT_SECONDS", "45"))
    
    # Test parameters (overridden via CLI)
    TEST_ITERATIONS = 1
    API_DELAY = 8
    
    # SOCKS5 Regional testing
    NORDVPN_REGIONS = [
        "los-angeles.us",
        "new-york.us", 
        "atlanta.us",
        "chicago.us",
        "phoenix.us",
        "san-francisco.us",
        "amsterdam.nl",
        "stockholm.se",
    ]
    
    # Multi-deployment URLs
    EDGE_FUNCTION_URL = os.getenv("EDGE_FUNCTION_URL", "https://testing-speed-iota.vercel.app/api/edge-gemini")
    SERVERLESS_FUNCTION_URL = os.getenv("SERVERLESS_FUNCTION_URL", "https://testing-speed-iota.vercel.app/api/serverless-gemini")
    
    # Deployment configurations
    DEPLOYMENT_METHODS = ["edge_function", "serverless_function", "socks5_proxy"]
    
    # ✅ FIXED: Performance thresholds for VPN + Hong Kong setup
    EXCELLENT_THRESHOLD = 5.0   # Account for VPN overhead
    GOOD_THRESHOLD = 8.0        # More realistic with VPN
    AVERAGE_THRESHOLD = 12.0    # Reasonable with network latency
    POOR_THRESHOLD = 20.0       # Clear poor performance marker
    
    # ✅ FIXED: Realistic baseline validation thresholds
    BASELINE_MIN_RESPONSE_TIME = 0.3   # Minimum realistic with VPN
    BASELINE_MAX_RESPONSE_TIME = 45.0  # More generous maximum
    BASELINE_WARNING_THRESHOLD = 20.0  # Earlier warning
    
    # ✅ NEW: TTFB-specific thresholds (MISSING FROM YOUR CONFIG)
    BASELINE_MIN_TTFB = 0.2     # Minimum realistic TTFB with VPN
    BASELINE_MAX_TTFB = 3.0     # Maximum acceptable TTFB
    TTFB_WARNING_THRESHOLD = 2.0 # TTFB investigation threshold
    
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
                "expected_latency": "0.8-1.5s",  # Adjusted for VPN
                "max_timeout": 25
            },
            "serverless_function": {
                "url": cls.SERVERLESS_FUNCTION_URL,
                "name": "Serverless Function", 
                "expected_latency": "1.0-2.0s",  # Adjusted for VPN
                "max_timeout": 30
            },
            "socks5_proxy": {
                "url": None,
                "name": "SOCKS5 Proxy",
                "expected_latency": "1.5-3.0s",  # Adjusted for double proxy
                "max_timeout": 30
            }
        }
        return configs.get(method, {})
