# HiAnime MCP Server 🎬

A **Model Context Protocol (MCP)** server for browsing and searching anime from HiAnime and MyAnimeList (MAL). This server can be used with **any MCP-compatible client**, not just Claude Desktop!

## 🌟 Features

This MCP server provides **26 powerful tools** for anime discovery:

### 📺 HiAnime Tools

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
| `get_episode_info` | Get specific episode details |
| `get_anime_az_list` | Browse anime alphabetically |
| `get_anime_by_producer` | Browse anime by studio/producer |
| `filter_anime` | Advanced multi-criteria filtering |
| `get_available_filters` | List all available filter options |
| `check_api_health` | Check if the API is responding |

### 📊 MyAnimeList (MAL) Tools

| Tool | Description |
|------|-------------|
| `mal_search` | Search anime on MAL with official API |
| `mal_anime_details` | Get detailed anime info by MAL ID |
| `mal_ranking` | Get anime rankings (top, airing, upcoming, etc.) |
| `mal_seasonal` | Get seasonal anime by year and season |

### 🔐 MAL User Authentication Tools

| Tool | Description |
|------|-------------|
| `mal_get_auth_url` | Get OAuth2 authorization URL for MAL login |
| `mal_exchange_token` | Exchange auth code for access token |
| `mal_user_animelist` | Get user's anime list with status filters |
| `mal_user_profile` | Get user's MAL profile information |

### 🔗 Combined Tools

| Tool | Description |
|------|-------------|
| `combined_search` | Search both HiAnime and MAL simultaneously |

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
- "What are the top ranked anime on MAL?"
- "Show me anime from Winter 2024 season"
- "Search both HiAnime and MAL for Attack on Titan"
- "Get my MAL anime list" (requires authentication)

## 🛠 Available Tools Reference

### HiAnime - Search & Discovery

```
search_anime(keyword: str, page: int = 1)
```
Search for anime by name or keyword.

### HiAnime - Browse Categories

```
get_popular_anime(page: int = 1)
get_top_airing_anime(page: int = 1)
get_recently_updated_anime(page: int = 1)
get_completed_anime(page: int = 1)
get_subbed_anime(page: int = 1)
get_dubbed_anime(page: int = 1)
```

### HiAnime - Filter by Attributes

```
get_anime_by_genre(genre: str, page: int = 1)
get_anime_by_type(anime_type: str, page: int = 1)
get_anime_by_producer(producer_slug: str, page: int = 1)
get_anime_az_list(letter: str, page: int = 1)
```

### HiAnime - Detailed Information

```
get_anime_details(slug: str)
get_anime_episodes(slug: str)
get_episode_info(slug: str, episode_number: int)
```

### HiAnime - Advanced Filtering

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

### MyAnimeList (MAL) - Search & Browse

```
mal_search(query: str, limit: int = 10)
```
Search anime on MAL with official API.

```
mal_anime_details(mal_id: int)
```
Get detailed anime info by MAL ID.

```
mal_ranking(ranking_type: str = "all", limit: int = 10)
```
Get anime rankings. Types: all, airing, upcoming, tv, movie, bypopularity, favorite

```
mal_seasonal(year: int, season: str, limit: int = 10)
```
Get seasonal anime. Seasons: winter, spring, summer, fall

### MyAnimeList - User Authentication

```
mal_get_auth_url(client_id: str, redirect_uri: str, client_secret: str = None)
```
Get OAuth2 authorization URL for MAL login.

```
mal_exchange_token(client_id: str, code: str, code_verifier: str, redirect_uri: str, client_secret: str = None)
```
Exchange authorization code for access token.

```
mal_user_animelist(client_id: str, access_token: str, status: str = None, limit: int = 100)
```
Get user's anime list. Status options: watching, completed, on_hold, dropped, plan_to_watch

```
mal_user_profile(client_id: str, access_token: str)
```
Get user's MAL profile information.

### Combined Tools

```
combined_search(query: str, limit: int = 5)
```
Search both HiAnime and MAL simultaneously for comparison.

### Utility

```
get_available_filters()          # List all filter options
check_api_health()               # Check API status
```

## 🎭 Available Genres

action, adventure, cars, comedy, dementia, demons, drama, ecchi, fantasy, game, harem, historical, horror, isekai, josei, kids, magic, martial-arts, mecha, military, music, mystery, parody, police, psychological, romance, samurai, school, sci-fi, seinen, shoujo, shoujo-ai, shounen, shounen-ai, slice-of-life, space, sports, super-power, supernatural, thriller, vampire

## 📁 Available Types

movie, tv, ova, ona, special, music

## 🏆 MAL Ranking Types

- `all` - Top Anime Series
- `airing` - Top Airing Anime
- `upcoming` - Top Upcoming Anime
- `tv` - Top TV Series
- `movie` - Top Movies
- `bypopularity` - Most Popular
- `favorite` - Most Favorited

## 🍂 Available Seasons

- `winter` - January to March
- `spring` - April to June
- `summer` - July to September
- `fall` - October to December

## 🔐 MAL Authentication Setup

To use MAL user features (anime list, profile), you need to:

1. **Create a MAL API Application:**
   - Go to https://myanimelist.net/apiconfig
   - Create a new application
   - Copy your Client ID (and optionally Client Secret)

2. **Get Authorization:**
   ```
   # Use mal_get_auth_url to get the authorization URL
   # Open the URL in your browser and authorize
   # Copy the 'code' from the callback URL
   ```

3. **Exchange for Token:**
   ```
   # Use mal_exchange_token with the code and code_verifier
   # Save the access_token securely
   ```

4. **Use Authenticated Endpoints:**
   ```
   # Use mal_user_animelist and mal_user_profile with your access_token
   ```

⚠️ **Privacy:** Your credentials and tokens are NOT stored by this server.

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
- [MyAnimeList API](https://myanimelist.net/apiconfig/references/api/v2) for MAL integration
- [Model Context Protocol](https://modelcontextprotocol.io) by Anthropic
