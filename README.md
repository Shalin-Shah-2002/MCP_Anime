# HiAnime MCP Server 🎬

A **Model Context Protocol (MCP)** server for browsing and searching anime from HiAnime. This server can be used with **any MCP-compatible client**, not just Claude Desktop!

## 🌟 Features

This MCP server provides 15 powerful tools for anime discovery:

| Tool | Description |
|------|-------------|
| `search_anime` | Search for anime by keyword |
| `get_popular_anime` | Get most popular anime |
| `get_top_airing_anime` | Get currently airing anime |
| `get_recently_updated_anime` | Get recently updated anime |
| `get_completed_anime` | Get completed anime |
| `get_subbed_anime` | Get anime with subtitles |
| `get_dubbed_anime` | Get dubbed anime |
| `get_anime_by_genre` | Browse anime by genre (40+ genres) |
| `get_anime_by_type` | Browse anime by type (TV, Movie, OVA, etc.) |
| `get_anime_details` | Get detailed info about specific anime |
| `get_anime_episodes` | Get episode list for an anime |
| `get_anime_az_list` | Browse anime alphabetically |
| `get_anime_by_producer` | Browse anime by studio/producer |
| `filter_anime` | Advanced multi-criteria filtering |
| `get_available_filters` | List all available filter options |
| `check_api_health` | Check if the API is responding |

## 📋 Prerequisites

- **Python 3.10+**
- **uv** (recommended) or **pip**

## 🚀 Quick Start

### Option 1: Using uv (Recommended)

```bash
# Clone or navigate to the project directory
cd MCP_Anime

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv pip install -e .

# Or install from requirements.txt
uv pip install -r requirements.txt
```

### Option 2: Using pip

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Run the Server

```bash
# Using uv
uv run hianime_mcp_server.py

# Or directly with Python
python hianime_mcp_server.py
```

## 🔧 Configuration for MCP Clients

### Claude Desktop

Edit your Claude Desktop config file:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "hianime": {
      "command": "uv",
      "args": [
        "--directory",
        "/ABSOLUTE/PATH/TO/MCP_Anime",
        "run",
        "hianime_mcp_server.py"
      ]
    }
  }
}
```

**Alternative using Python directly:**

```json
{
  "mcpServers": {
    "hianime": {
      "command": "/ABSOLUTE/PATH/TO/MCP_Anime/.venv/bin/python",
      "args": [
        "/ABSOLUTE/PATH/TO/MCP_Anime/hianime_mcp_server.py"
      ]
    }
  }
}
```

### Cursor IDE

Add to your Cursor MCP settings (`.cursor/mcp.json` in your project or global settings):

```json
{
  "mcpServers": {
    "hianime": {
      "command": "uv",
      "args": [
        "--directory",
        "/ABSOLUTE/PATH/TO/MCP_Anime",
        "run",
        "hianime_mcp_server.py"
      ]
    }
  }
}
```

### VS Code with Continue Extension

Add to your Continue config (`~/.continue/config.json`):

```json
{
  "mcpServers": [
    {
      "name": "hianime",
      "command": "python",
      "args": ["/ABSOLUTE/PATH/TO/MCP_Anime/hianime_mcp_server.py"]
    }
  ]
}
```

### Generic MCP Client

For any MCP client that supports STDIO transport:

```bash
# Command to run the server
uv --directory /path/to/MCP_Anime run hianime_mcp_server.py

# Or with Python
/path/to/MCP_Anime/.venv/bin/python /path/to/MCP_Anime/hianime_mcp_server.py
```

### Programmatic Usage (Custom MCP Client)

```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    server_params = StdioServerParameters(
        command="python",
        args=["/path/to/MCP_Anime/hianime_mcp_server.py"],
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()
            
            # List available tools
            tools = await session.list_tools()
            print("Available tools:", [t.name for t in tools.tools])
            
            # Call a tool
            result = await session.call_tool(
                "search_anime",
                arguments={"keyword": "naruto", "page": 1}
            )
            print(result)

asyncio.run(main())
```

## 📖 Usage Examples

Once connected to an MCP client, you can ask questions like:

- "Search for anime about demons"
- "What are the most popular anime right now?"
- "Show me currently airing anime"
- "Get details about One Piece"
- "Find action anime with a score above 8"
- "List all anime from Studio MAPPA"
- "What anime start with the letter A?"
- "Show me completed isekai anime"
- "Get the episode list for Naruto"

## 🛠 Available Tools Reference

### Search & Discovery

```
search_anime(keyword: str, page: int = 1)
```
Search for anime by name or keyword.

### Browse Categories

```
get_popular_anime(page: int = 1)
get_top_airing_anime(page: int = 1)
get_recently_updated_anime(page: int = 1)
get_completed_anime(page: int = 1)
get_subbed_anime(page: int = 1)
get_dubbed_anime(page: int = 1)
```

### Filter by Attributes

```
get_anime_by_genre(genre: str, page: int = 1)
get_anime_by_type(anime_type: str, page: int = 1)
get_anime_by_producer(producer_slug: str, page: int = 1)
get_anime_az_list(letter: str, page: int = 1)
```

### Detailed Information

```
get_anime_details(slug: str)
get_anime_episodes(slug: str)
```

### Advanced Filtering

```
filter_anime(
    anime_type: str = None,      # movie, tv, ova, ona, special, music
    status: str = None,          # finished, airing, upcoming
    rated: str = None,           # g, pg, pg-13, r, r+, rx
    score: int = None,           # 1-10
    season: str = None,          # spring, summer, fall, winter
    language: str = None,        # sub, dub
    genres: str = None,          # comma-separated: "action,fantasy"
    sort: str = None,            # default, recently_added, score, etc.
    page: int = 1
)
```

### Utility

```
get_available_filters()          # List all filter options
check_api_health()               # Check API status
```

## 🎭 Available Genres

action, adventure, cars, comedy, dementia, demons, drama, ecchi, fantasy, game, harem, historical, horror, isekai, josei, kids, magic, martial-arts, mecha, military, music, mystery, parody, police, psychological, romance, samurai, school, sci-fi, seinen, shoujo, shoujo-ai, shounen, shounen-ai, slice-of-life, space, sports, super-power, supernatural, thriller, vampire

## 📁 Available Types

movie, tv, ova, ona, special, music

## 🔧 Troubleshooting

### Server not showing in Claude Desktop

1. Make sure you've restarted Claude Desktop after editing the config
2. Check that the path in the config is absolute (starts with `/` on macOS/Linux or `C:\` on Windows)
3. Verify the Python environment has all dependencies installed

### Connection timeout

The HiAnime API might be slow to respond. The server has a 30-second timeout configured.

### Logging

The server logs to stderr. Check your MCP client's logs for debugging information.

### Testing the server manually

```bash
# Test with MCP inspector
npx @modelcontextprotocol/inspector python hianime_mcp_server.py
```

## 📄 License

MIT License - feel free to use and modify!

## 🤝 Contributing

Contributions are welcome! Feel free to submit issues and pull requests.

## 🙏 Credits

- [HiAnime API](https://hianime-api-b6ix.onrender.com) for the anime data
- [Model Context Protocol](https://modelcontextprotocol.io) by Anthropic
