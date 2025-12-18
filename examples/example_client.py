"""
Example MCP Client for HiAnime Server

This script demonstrates how to connect to the HiAnime MCP server
programmatically from any Python application.

Requirements:
    pip install mcp

Usage:
    python example_client.py
"""

import asyncio
import sys
import os

# Add parent directory to path if running from examples folder
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    """Demonstrate how to use the HiAnime MCP server programmatically."""
    
    # Get the path to the server script
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    server_script = os.path.join(script_dir, "hianime_mcp_server.py")
    
    # Configure server parameters
    server_params = StdioServerParameters(
        command="python",
        args=[server_script],
    )
    
    print("🚀 Connecting to HiAnime MCP Server...")
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()
            print("✅ Connected successfully!\n")
            
            # List available tools
            tools_response = await session.list_tools()
            tools = tools_response.tools
            
            print(f"📦 Available Tools ({len(tools)}):")
            print("-" * 50)
            for tool in tools:
                print(f"  • {tool.name}: {tool.description[:60]}...")
            print()
            
            # Example 1: Check API health
            print("🏥 Checking API Health...")
            health_result = await session.call_tool("check_api_health", arguments={})
            print(f"   {health_result.content[0].text}\n")
            
            # Example 2: Search for anime
            print("🔍 Searching for 'naruto'...")
            search_result = await session.call_tool(
                "search_anime",
                arguments={"keyword": "naruto", "page": 1}
            )
            # Print first 500 characters of result
            result_text = search_result.content[0].text
            print(result_text[:500] + "..." if len(result_text) > 500 else result_text)
            print()
            
            # Example 3: Get popular anime
            print("🌟 Getting Popular Anime...")
            popular_result = await session.call_tool(
                "get_popular_anime",
                arguments={"page": 1}
            )
            result_text = popular_result.content[0].text
            print(result_text[:500] + "..." if len(result_text) > 500 else result_text)
            print()
            
            # Example 4: Filter anime
            print("🎯 Filtering Action Anime with Score >= 8...")
            filter_result = await session.call_tool(
                "filter_anime",
                arguments={
                    "genres": "action",
                    "score": 8,
                    "status": "finished",
                    "page": 1
                }
            )
            result_text = filter_result.content[0].text
            print(result_text[:500] + "..." if len(result_text) > 500 else result_text)
            
            print("\n✨ Demo completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())
