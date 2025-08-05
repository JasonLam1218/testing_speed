import requests
import sys

# Your credentials (from the curl command)
username = "2qfCDkqLEw8P3kf4ZAdm5zMu"
password = "7R4LttY9hDK8rHjSmvBPM7q7"
server = "los-angeles.us.socks.nordhold.net"
port = 1080

# Test different server formats
servers_to_test = [
    f"{server}",
    "us.socks.nordhold.net",  # Generic US server
    "nl.socks.nordhold.net",  # Generic Netherlands server
]

for test_server in servers_to_test:
    print(f"\n🧪 Testing: {test_server}")
    
    proxy = {
        'http': f'socks5://{username}:{password}@{test_server}:{port}',
        'https': f'socks5://{username}:{password}@{test_server}:{port}'
    }
    
    try:
        # Test connection
        response = requests.get('https://httpbin.org/ip', 
                              proxies=proxy, 
                              timeout=15)
        
        if response.status_code == 200:
            ip_info = response.json()
            print(f"✅ SUCCESS: {test_server}")
            print(f"   IP via SOCKS5: {ip_info['origin']}")
            break
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            
    except requests.exceptions.ProxyError as e:
        print(f"❌ Proxy Error: {e}")
    except requests.exceptions.Timeout as e:
        print(f"❌ Timeout: {e}")
    except Exception as e:
        print(f"❌ Unknown Error: {e}")

print(f"\n🏠 Your real IP (without proxy):")
try:
    real_ip = requests.get('https://httpbin.org/ip', timeout=5).json()
    print(f"   Real IP: {real_ip['origin']}")
except:
    print("   Could not determine real IP")
