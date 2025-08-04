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
    # 
    # NORDVPN_REGIONS = [
    #     "los-angeles.us",     # West Coast America
    #     "new-york.us",        # East Coast America  
    #     "amsterdam.nl",       # Europe (Netherlands)
    #     "stockholm.se"        # Europe (Sweden)
    # ]

    NORDVPN_REGIONS = [
        # US City-Specific Servers
        "los-angeles.us",      # Los Angeles, US
        "new-york.us",         # New York, US  
        "atlanta.us",          # Atlanta, US
        "chicago.us",          # Chicago, US
        "phoenix.us",          # Phoenix, US
        "san-francisco.us",    # San Francisco, US
        
        # European City-Specific Servers
        "amsterdam.nl",        # Amsterdam, Netherlands
        "stockholm.se",        # Stockholm, Sweden
    ]

        
    # Directories
    RESULTS_DIR = os.getenv("RESULTS_DIR", "results")
    REPORTS_DIR = os.getenv("REPORTS_DIR", "reports")

    @classmethod
    def validate_config(cls):
        missing = []
        for var in ("NORDVPN_USERNAME","NORDVPN_PASSWORD","GEMINI_API_KEY"):
            if not getattr(cls,var):
                missing.append(var)
        if missing:
            raise ValueError(f"Missing env vars: {', '.join(missing)}")
