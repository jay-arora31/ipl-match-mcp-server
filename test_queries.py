#!/usr/bin/env python3
"""
Test script to demonstrate IPL MCP Server query capabilities
"""

import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.mcp_server.query_engine import QueryEngine

def main():
    print("🏏 IPL MCP Server - Query Demo")
    print("=" * 50)
    
    qe = QueryEngine()
    
    # Test queries from the requirements
    test_queries = [
        "Show me all matches in the dataset",
        "Which team won the most matches?",
        "Who scored the most runs across all matches?",
        "What was the highest total score?",
        "Show matches played in Mumbai",
        "Who took the most wickets?",
        "Show me Virat Kohli batting stats",
        "What's the average first innings score?",
        "Show me all centuries scored",
        "Which venue has the highest scoring matches?",
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📊 Query {i}: {query}")
        print("-" * 60)
        try:
            result = qe.process_query(query)
            # Truncate long results for readability
            if len(result) > 800:
                result = result[:800] + "...\n[Results truncated for display]"
            print(result)
        except Exception as e:
            print(f"Error: {e}")
        
        if i < len(test_queries):
            input("\n⏸️  Press Enter to continue to next query...")
    
    print(f"\n✅ Demo completed! Tested {len(test_queries)} different query types.")
    print("\n💡 Try your own queries by running:")
    print("   python -c \"from src.mcp_server.query_engine import QueryEngine; qe = QueryEngine(); print(qe.process_query('your query here'))\"")

if __name__ == "__main__":
    main() 