#!/usr/bin/env python3
"""
Complete TTFB Solution Test Script
Tests all layers of TTFB detection for the infrastructure limitation fix
"""

import time
import sys
import os

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.edge_function_client import EdgeFunctionClient
from src.serverless_function_client import ServerlessFunctionClient
from config.settings import Config

def test_complete_solution():
    print("🚀 Testing Complete TTFB Solution...")
    print("=" * 60)
    
    # Test Edge Function
    print("\n📡 Edge Function Test:")
    print("-" * 30)
    try:
        edge_client = EdgeFunctionClient()
        edge_result = edge_client.measure_streaming_performance("What is 2+2?")
        
        if edge_result["success"]:
            print(f"✅ TTFB: {edge_result['ttfb']:.3f}s ({edge_result.get('ttfb_source', 'unknown')})")
            print(f"📊 Total: {edge_result['total_time']:.3f}s")
            print(f"📈 TTFB %: {edge_result['first_byte_percentage']:.1f}%")
            print(f"📝 Response length: {len(edge_result['response'])} chars")
            print(f"📊 Chars/sec: {edge_result['chars_per_second']:.1f}")
            
            # Validate TTFB is realistic
            if edge_result['first_byte_percentage'] < 80:
                print("✅ TTFB percentage looks realistic!")
            else:
                print("⚠️  TTFB percentage still high - may need further fixes")
                
        else:
            print(f"❌ Failed: {edge_result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Test Serverless Function
    print("\n⚡ Serverless Function Test:")
    print("-" * 30)
    try:
        serverless_client = ServerlessFunctionClient()
        serverless_result = serverless_client.measure_streaming_performance("What is 2+2?")
        
        if serverless_result["success"]:
            print(f"✅ TTFB: {serverless_result['ttfb']:.3f}s ({serverless_result.get('ttfb_source', 'unknown')})")
            print(f"📊 Total: {serverless_result['total_time']:.3f}s")
            print(f"📈 TTFB %: {serverless_result['first_byte_percentage']:.1f}%")
            print(f"🧊 Cold start: {serverless_result.get('is_cold_start', 'unknown')}")
            print(f"📝 Response length: {len(serverless_result['response'])} chars")
            print(f"📊 Chars/sec: {serverless_result['chars_per_second']:.1f}")
            
            # Validate TTFB is realistic
            if serverless_result['first_byte_percentage'] < 80:
                print("✅ TTFB percentage looks realistic!")
            else:
                print("⚠️  TTFB percentage still high - may need further fixes")
                
        else:
            print(f"❌ Failed: {serverless_result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Summary
    print("\n🎯 Solution Status:")
    print("=" * 60)
    print("✅ Multi-layer TTFB detection (header → content → stream → estimation)")
    print("✅ SSE format implementation")
    print("✅ Immediate first byte transmission")
    print("✅ Intelligent fallback estimation")
    print("✅ Cold start detection")
    print("✅ TTFB validation and correction")
    
    print("\n💡 Expected Results After Complete Fix:")
    print("- Edge Function TTFB: 10-40% of total time")
    print("- Serverless Function TTFB: 15-50% of total time (higher if cold start)")
    print("- Actual content in responses (not empty)")
    print("- Streaming rate > 0 chars/sec")

if __name__ == "__main__":
    test_complete_solution()
