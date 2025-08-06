#!/usr/bin/env python3
"""
IPL MCP Server - Main Application Entry Point

This application processes IPL cricket data from Cricsheet and provides
an MCP server interface for querying the data using natural language.
"""

import asyncio
import argparse
import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.database.database import create_tables, reset_database, check_database
from src.data_processing.json_parser import IPLDataProcessor
from src.mcp_server.server import IPLMCPServer

def setup_database():
    """Setup database tables"""
    print("Setting up database...")
    create_tables()

def load_data(data_dir="data", reset=False):
    """Load IPL data from JSON files into database"""
    if reset:
        print("Resetting database...")
        reset_database()
    
    if not check_database():
        setup_database()
    
    print("Loading IPL data...")
    processor = IPLDataProcessor()
    
    try:
        count = processor.process_all_matches(data_dir)
        print(f"Successfully loaded {count} matches!")
        
        print("Calculating statistics...")
        processor.calculate_statistics()
        print("Statistics calculation complete!")
        
    except Exception as e:
        print(f"Error loading data: {e}")
        return False
    
    return True

async def run_server():
    """Run the MCP server"""
    print("Starting IPL MCP Server...")
    print("The server is ready to accept connections from Claude Desktop.")
    print("Press Ctrl+C to stop the server.")
    
    server = IPLMCPServer()
    try:
        await server.run()
    except KeyboardInterrupt:
        print("\nServer stopped by user.")
    except Exception as e:
        print(f"Server error: {e}")

def main():
    """Main application entry point"""
    parser = argparse.ArgumentParser(description="IPL MCP Server")
    parser.add_argument("--setup", action="store_true", 
                       help="Setup database and load data")
    parser.add_argument("--reset", action="store_true",
                       help="Reset database before loading data")
    parser.add_argument("--data-dir", default="data",
                       help="Directory containing IPL JSON data files")
    parser.add_argument("--server", action="store_true",
                       help="Start MCP server (default if no other options)")
    
    args = parser.parse_args()
    
    # If no specific action is requested, default to server mode
    if not args.setup and not args.reset:
        args.server = True
    
    try:
        if args.setup or args.reset:
            # Setup/reset database and load data
            success = load_data(args.data_dir, args.reset)
            if not success:
                sys.exit(1)
        
        if args.server:
            # Check if database is ready
            if not check_database():
                print("Database not found or empty. Please run with --setup first.")
                print("Example: python main.py --setup")
                sys.exit(1)
            
            # Run the MCP server
            asyncio.run(run_server())
    
    except KeyboardInterrupt:
        print("\nApplication stopped by user.")
    except Exception as e:
        print(f"Application error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 