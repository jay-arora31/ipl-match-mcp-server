import asyncio
import json
from typing import Any, Dict, List, Optional

from mcp.server import Server, InitializationOptions
from mcp import stdio_server
from mcp.types import Resource, Tool, TextContent

from ..database.database import get_db_session
from ..database.models import *
from .query_engine import QueryEngine

class IPLMCPServer:
    def __init__(self):
        self.server = Server("ipl-cricket-server")
        self.query_engine = QueryEngine()
        self.setup_handlers()
    
    def setup_handlers(self):
        """Setup MCP server handlers"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            """List available tools for querying IPL data"""
            return [
                Tool(
                    name="query_ipl_data",
                    description="""Query IPL cricket data using natural language. 
                    Examples:
                    - 'Show me all matches in the dataset'
                    - 'Which team won the most matches?'
                    - 'Who scored the most runs across all matches?'
                    - 'What was the highest total score?'
                    - 'Show matches played in Mumbai'
                    - 'Who has the best bowling figures?'
                    - 'Show me Virat Kohli batting stats'
                    - 'What's the average first innings score?'
                    - 'Show me all centuries scored'
                    - 'Which venue has the highest scoring matches?'
                    """,
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Natural language query about IPL cricket data"
                            }
                        },
                        "required": ["query"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Handle tool calls"""
            if name == "query_ipl_data":
                query = arguments.get("query", "")
                if not query:
                    return [TextContent(type="text", text="Please provide a query.")]
                
                try:
                    result = self.query_engine.process_query(query)
                    return [TextContent(type="text", text=result)]
                except Exception as e:
                    return [TextContent(type="text", text=f"Error processing query: {str(e)}")]
            
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

    async def run(self):
        """Run the MCP server"""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="ipl-cricket-server",
                    server_version="1.0.0",
                    capabilities={
                        "tools": {}
                    }
                )
            ) 