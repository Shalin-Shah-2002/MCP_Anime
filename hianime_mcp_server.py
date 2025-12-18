"""
HiAnime MCP Server - A Model Context Protocol server for anime data.

This MCP server provides tools to search, browse, and get detailed information
about anime from the HiAnime API. It can be used with any MCP-compatible client
including Claude Desktop, custom MCP clients, and more.

Author: Senior Developer
Version: 1.0.0
"""

import logging
import os
from typing import Any, Optional

import httpx
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# Load environment variables from .env file
load_dotenv()

# Configure logging to stderr (important for STDIO-based MCP servers)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("hianime-mcp")

# Initialize FastMCP server
mcp = FastMCP("hianime")

# Constants - Load from environment variables with defaults
HIANIME_API_BASE = os.getenv("HIANIME_API_BASE", "https://hianime-api-b6ix.onrender.com")
USER_AGENT = os.getenv("USER_AGENT", "HiAnime-MCP-Server/1.0")
REQUEST_TIMEOUT = float(os.getenv("REQUEST_TIMEOUT", "30.0"))

logger.info(f"Using API base: {HIANIME_API_BASE}")

# Available genres for reference
AVAILABLE_GENRES = [
    "action", "adventure", "cars", "comedy", "dementia", "demons", "drama",
    "ecchi", "fantasy", "game", "harem", "historical", "horror", "isekai",
    "josei", "kids", "magic", "martial-arts", "mecha", "military", "music",
    "mystery", "parody", "police", "psychological", "romance", "samurai",
    "school", "sci-fi", "seinen", "shoujo", "shoujo-ai", "shounen",
    "shounen-ai", "slice-of-life", "space", "sports", "super-power",
    "supernatural", "thriller", "vampire"
]

# Available types
AVAILABLE_TYPES = ["movie", "tv", "ova", "ona", "special", "music"]

# Available statuses
AVAILABLE_STATUSES = ["finished", "airing", "upcoming"]

# Available ratings
AVAILABLE_RATINGS = ["g", "pg", "pg-13", "r", "r+", "rx"]

# Available seasons
AVAILABLE_SEASONS = ["spring", "summer", "fall", "winter"]

# Available sort options
AVAILABLE_SORT_OPTIONS = [
    "default", "recently_added", "recently_updated", "score",
    "name_az", "released_date", "most_watched"
]


async def make_api_request(endpoint: str, params: Optional[dict] = None) -> dict[str, Any] | None:
    """Make a request to the HiAnime API with proper error handling."""
    url = f"{HIANIME_API_BASE}{endpoint}"
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                url,
                headers=headers,
                params=params,
                timeout=REQUEST_TIMEOUT
            )
            response.raise_for_status()
            return response.json()
        except httpx.TimeoutException:
            logger.error(f"Request timeout for {url}")
            return None
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code} for {url}")
            return None
        except Exception as e:
            logger.error(f"Request failed for {url}: {str(e)}")
            return None


def format_anime_item(item: dict) -> str:
    """Format a single anime item into a readable string."""
    # Extract slug properly - prefer 'slug' field, fallback to constructing from id
    slug = item.get('slug', '')
    url = item.get('url', '')
    if not slug and item.get('id'):
        # Try to extract from URL if available
        if url:
            # URL format: https://hianime.to/anime-name-123?ref=search
            path = url.split('?')[0].split('/')[-1]
            slug = path
        else:
            slug = item.get('id', 'N/A')
    
    # Clean URL (remove ref param)
    if url:
        url = url.split('?')[0]
    
    # Get episode counts
    eps_sub = item.get('episodes_sub', item.get('episodes', {}).get('sub', 'N/A'))
    eps_dub = item.get('episodes_dub', item.get('episodes', {}).get('dub', 'N/A'))
    eps_display = f"Sub: {eps_sub}"
    if eps_dub:
        eps_display += f", Dub: {eps_dub}"
    
    result = f"""
📺 **{item.get('title', 'Unknown Title')}**
   ▸ Slug: `{slug}` ← Use this for episode lookup
   ▸ Type: {item.get('type', 'N/A')}
   ▸ Episodes: {eps_display}
   ▸ Duration: {item.get('duration', 'N/A')}"""
    
    if url:
        result += f"\n   ▸ Page: {url}"
    
    return result


def format_anime_list(data: list[dict]) -> str:
    """Format a list of anime items."""
    if not data:
        return "No anime found."
    return "\n".join(format_anime_item(item) for item in data)


def format_anime_details(data: dict) -> str:
    """Format detailed anime information."""
    info = data.get('data', data)
    
    # Handle nested structure
    anime_info = info.get('anime', info)
    
    details = f"""
🎬 **{anime_info.get('title', 'Unknown Title')}**

📝 **Basic Information:**
   - Japanese Title: {anime_info.get('japanese_title', anime_info.get('japaneseTitle', 'N/A'))}
   - Type: {anime_info.get('type', 'N/A')}
   - Status: {anime_info.get('status', 'N/A')}
   - Episodes: {anime_info.get('episodes', anime_info.get('totalEpisodes', 'N/A'))}
   - Duration: {anime_info.get('duration', 'N/A')}
   - Aired: {anime_info.get('aired', 'N/A')}
   - Season: {anime_info.get('season', 'N/A')}
   - Rating: {anime_info.get('rating', anime_info.get('malscore', 'N/A'))}

📖 **Synopsis:**
{anime_info.get('synopsis', anime_info.get('description', 'No synopsis available.'))}

🏷️ **Genres:** {', '.join(anime_info.get('genres', [])) if anime_info.get('genres') else 'N/A'}

🎭 **Studios:** {', '.join(anime_info.get('studios', [])) if anime_info.get('studios') else 'N/A'}

�icing **Producers:** {', '.join(anime_info.get('producers', [])) if anime_info.get('producers') else 'N/A'}
"""
    return details


def format_episode_list(data: list[dict], include_urls: bool = True) -> str:
    """Format episode list with reference links."""
    if not data:
        return "No episodes found."
    
    episodes = []
    for ep in data[:20]:  # Limit to first 20 episodes for readability
        ep_num = ep.get('number', ep.get('episodeNum', 'N/A'))
        title = ep.get('title', ep.get('name', 'N/A'))
        japanese_title = ep.get('japanese_title', '')
        ep_id = ep.get('id', '')
        url = ep.get('url', '')
        is_filler = " 🔸 Filler" if ep.get('is_filler', ep.get('isFiller', False)) else ""
        
        ep_line = f"   Episode {ep_num}: {title}"
        if japanese_title:
            ep_line += f" ({japanese_title})"
        ep_line += is_filler
        if include_urls and url:
            ep_line += f"\n      📎 Reference: {url}"
        if ep_id:
            ep_line += f"\n      🆔 ID: {ep_id}"
        
        episodes.append(ep_line)
    
    result = "\n\n".join(episodes)
    if len(data) > 20:
        result += f"\n\n... and {len(data) - 20} more episodes."
    return result


# ============================================================================
# MCP TOOLS
# ============================================================================

@mcp.tool()
async def search_anime(keyword: str, page: int = 1) -> str:
    """
    Search for anime by keyword.
    
    Args:
        keyword: The search term to find anime (e.g., "naruto", "one piece", "attack on titan")
        page: Page number for pagination (default: 1)
    
    Returns:
        A formatted list of anime matching the search query
    """
    logger.info(f"Searching anime with keyword: {keyword}, page: {page}")
    
    data = await make_api_request("/api/search", {"keyword": keyword, "page": page})
    
    if not data or not data.get("success"):
        return f"Unable to search for '{keyword}'. Please try again later."
    
    anime_list = data.get("data", [])
    count = data.get("count", len(anime_list))
    current_page = data.get("page", page)
    
    if not anime_list:
        return f"No anime found for '{keyword}'."
    
    result = f"🔍 **Search Results for '{keyword}'** (Page {current_page}, {count} results)\n"
    result += "=" * 50 + "\n"
    result += format_anime_list(anime_list)
    
    return result


@mcp.tool()
async def get_popular_anime(page: int = 1) -> str:
    """
    Get the most popular anime.
    
    Args:
        page: Page number for pagination (default: 1)
    
    Returns:
        A formatted list of popular anime
    """
    logger.info(f"Fetching popular anime, page: {page}")
    
    data = await make_api_request("/api/popular", {"page": page})
    
    if not data or not data.get("success"):
        return "Unable to fetch popular anime. Please try again later."
    
    anime_list = data.get("data", [])
    count = data.get("count", len(anime_list))
    
    result = f"🌟 **Most Popular Anime** (Page {page}, {count} results)\n"
    result += "=" * 50 + "\n"
    result += format_anime_list(anime_list)
    
    return result


@mcp.tool()
async def get_top_airing_anime(page: int = 1) -> str:
    """
    Get currently airing anime (top airing).
    
    Args:
        page: Page number for pagination (default: 1)
    
    Returns:
        A formatted list of currently airing anime
    """
    logger.info(f"Fetching top airing anime, page: {page}")
    
    data = await make_api_request("/api/top-airing", {"page": page})
    
    if not data or not data.get("success"):
        return "Unable to fetch top airing anime. Please try again later."
    
    anime_list = data.get("data", [])
    count = data.get("count", len(anime_list))
    
    result = f"📡 **Currently Airing Anime** (Page {page}, {count} results)\n"
    result += "=" * 50 + "\n"
    result += format_anime_list(anime_list)
    
    return result


@mcp.tool()
async def get_recently_updated_anime(page: int = 1) -> str:
    """
    Get recently updated anime (latest episodes released).
    
    Args:
        page: Page number for pagination (default: 1)
    
    Returns:
        A formatted list of recently updated anime
    """
    logger.info(f"Fetching recently updated anime, page: {page}")
    
    data = await make_api_request("/api/recently-updated", {"page": page})
    
    if not data or not data.get("success"):
        return "Unable to fetch recently updated anime. Please try again later."
    
    anime_list = data.get("data", [])
    count = data.get("count", len(anime_list))
    
    result = f"🆕 **Recently Updated Anime** (Page {page}, {count} results)\n"
    result += "=" * 50 + "\n"
    result += format_anime_list(anime_list)
    
    return result


@mcp.tool()
async def get_completed_anime(page: int = 1) -> str:
    """
    Get completed anime (finished airing).
    
    Args:
        page: Page number for pagination (default: 1)
    
    Returns:
        A formatted list of completed anime
    """
    logger.info(f"Fetching completed anime, page: {page}")
    
    data = await make_api_request("/api/completed", {"page": page})
    
    if not data or not data.get("success"):
        return "Unable to fetch completed anime. Please try again later."
    
    anime_list = data.get("data", [])
    count = data.get("count", len(anime_list))
    
    result = f"✅ **Completed Anime** (Page {page}, {count} results)\n"
    result += "=" * 50 + "\n"
    result += format_anime_list(anime_list)
    
    return result


@mcp.tool()
async def get_subbed_anime(page: int = 1) -> str:
    """
    Get anime with subtitles (subbed anime).
    
    Args:
        page: Page number for pagination (default: 1)
    
    Returns:
        A formatted list of subbed anime
    """
    logger.info(f"Fetching subbed anime, page: {page}")
    
    data = await make_api_request("/api/subbed", {"page": page})
    
    if not data or not data.get("success"):
        return "Unable to fetch subbed anime. Please try again later."
    
    anime_list = data.get("data", [])
    count = data.get("count", len(anime_list))
    
    result = f"📝 **Subbed Anime** (Page {page}, {count} results)\n"
    result += "=" * 50 + "\n"
    result += format_anime_list(anime_list)
    
    return result


@mcp.tool()
async def get_dubbed_anime(page: int = 1) -> str:
    """
    Get dubbed anime (English dub).
    
    Args:
        page: Page number for pagination (default: 1)
    
    Returns:
        A formatted list of dubbed anime
    """
    logger.info(f"Fetching dubbed anime, page: {page}")
    
    data = await make_api_request("/api/dubbed", {"page": page})
    
    if not data or not data.get("success"):
        return "Unable to fetch dubbed anime. Please try again later."
    
    anime_list = data.get("data", [])
    count = data.get("count", len(anime_list))
    
    result = f"🎙️ **Dubbed Anime** (Page {page}, {count} results)\n"
    result += "=" * 50 + "\n"
    result += format_anime_list(anime_list)
    
    return result


@mcp.tool()
async def get_anime_by_genre(genre: str, page: int = 1) -> str:
    """
    Get anime by genre.
    
    Args:
        genre: The genre to filter by. Available genres: action, adventure, cars, comedy,
               dementia, demons, drama, ecchi, fantasy, game, harem, historical, horror,
               isekai, josei, kids, magic, martial-arts, mecha, military, music, mystery,
               parody, police, psychological, romance, samurai, school, sci-fi, seinen,
               shoujo, shoujo-ai, shounen, shounen-ai, slice-of-life, space, sports,
               super-power, supernatural, thriller, vampire
        page: Page number for pagination (default: 1)
    
    Returns:
        A formatted list of anime in the specified genre
    """
    genre_lower = genre.lower().strip()
    
    if genre_lower not in AVAILABLE_GENRES:
        return f"Invalid genre '{genre}'. Available genres: {', '.join(AVAILABLE_GENRES)}"
    
    logger.info(f"Fetching anime by genre: {genre_lower}, page: {page}")
    
    data = await make_api_request(f"/api/genre/{genre_lower}", {"page": page})
    
    if not data or not data.get("success"):
        return f"Unable to fetch anime for genre '{genre}'. Please try again later."
    
    anime_list = data.get("data", [])
    count = data.get("count", len(anime_list))
    
    result = f"🏷️ **{genre.title()} Anime** (Page {page}, {count} results)\n"
    result += "=" * 50 + "\n"
    result += format_anime_list(anime_list)
    
    return result


@mcp.tool()
async def get_anime_by_type(anime_type: str, page: int = 1) -> str:
    """
    Get anime by type.
    
    Args:
        anime_type: The type of anime. Available types: movie, tv, ova, ona, special, music
        page: Page number for pagination (default: 1)
    
    Returns:
        A formatted list of anime of the specified type
    """
    type_lower = anime_type.lower().strip()
    
    if type_lower not in AVAILABLE_TYPES:
        return f"Invalid type '{anime_type}'. Available types: {', '.join(AVAILABLE_TYPES)}"
    
    logger.info(f"Fetching anime by type: {type_lower}, page: {page}")
    
    data = await make_api_request(f"/api/type/{type_lower}", {"page": page})
    
    if not data or not data.get("success"):
        return f"Unable to fetch anime for type '{anime_type}'. Please try again later."
    
    anime_list = data.get("data", [])
    count = data.get("count", len(anime_list))
    
    result = f"📁 **{anime_type.upper()} Anime** (Page {page}, {count} results)\n"
    result += "=" * 50 + "\n"
    result += format_anime_list(anime_list)
    
    return result


@mcp.tool()
async def get_anime_details(slug: str) -> str:
    """
    Get detailed information about a specific anime.
    
    Args:
        slug: The anime slug/ID (e.g., "naruto-677", "one-piece-100", "attack-on-titan-112").
              You can get the slug from search results or browse listings.
    
    Returns:
        Detailed information about the anime including synopsis, genres, status, etc.
    """
    logger.info(f"Fetching anime details for slug: {slug}")
    
    data = await make_api_request(f"/api/anime/{slug}")
    
    if not data or not data.get("success"):
        return f"Unable to fetch details for anime '{slug}'. Please check the slug and try again."
    
    return format_anime_details(data)


@mcp.tool()
async def get_anime_episodes(slug: str) -> str:
    """
    Get the episode list for a specific anime.
    
    Args:
        slug: The anime slug/ID (e.g., "naruto-677", "one-piece-100").
              You can get the slug from search results or browse listings.
    
    Returns:
        A list of episodes for the anime
    """
    logger.info(f"Fetching episodes for anime: {slug}")
    
    data = await make_api_request(f"/api/episodes/{slug}")
    
    if not data or not data.get("success"):
        return f"Unable to fetch episodes for anime '{slug}'. Please check the slug and try again."
    
    episodes = data.get("data", [])
    count = data.get("count", len(episodes))
    
    result = f"📺 **Episodes for {slug}** ({count} total episodes)\n"
    result += "=" * 50 + "\n"
    result += format_episode_list(episodes)
    
    return result


@mcp.tool()
async def get_episode_info(slug: str, episode_number: int) -> str:
    """
    Get detailed information and reference page for a specific episode.
    
    Args:
        slug: The anime slug/ID (e.g., "naruto-677", "one-piece-100")
        episode_number: The episode number to get info for
    
    Returns:
        Episode details including title, ID, and reference page
    """
    logger.info(f"Getting info for {slug} episode {episode_number}")
    
    data = await make_api_request(f"/api/episodes/{slug}")
    
    if not data or not data.get("success"):
        return f"Unable to fetch episodes for anime '{slug}'. Please check the slug and try again."
    
    episodes = data.get("data", [])
    
    # Find the specific episode
    episode = None
    for ep in episodes:
        if ep.get('number') == episode_number:
            episode = ep
            break
    
    if not episode:
        return f"Episode {episode_number} not found for '{slug}'. This anime has {len(episodes)} episodes (1-{len(episodes)})."
    
    title = episode.get('title', 'N/A')
    japanese_title = episode.get('japanese_title', '')
    url = episode.get('url', 'N/A')
    ep_id = episode.get('id', 'N/A')
    is_filler = "Yes 🔸" if episode.get('is_filler', False) else "No"
    
    result = f"""
🎬 **{slug} - Episode {episode_number}**

📺 **Title:** {title}
🇯🇵 **Japanese Title:** {japanese_title if japanese_title else 'N/A'}
📎 **Page:** {url}
🆔 **ID:** {ep_id}
🔸 **Is Filler:** {is_filler}
"""
    return result


@mcp.tool()
async def get_anime_az_list(letter: str, page: int = 1) -> str:
    """
    Get anime alphabetically by first letter.
    
    Args:
        letter: Single letter A-Z, or "other" for non-alphabetic titles
        page: Page number for pagination (default: 1)
    
    Returns:
        A formatted list of anime starting with the specified letter
    """
    letter_upper = letter.upper().strip()
    
    # Validate letter
    if letter_upper != "OTHER" and (len(letter_upper) != 1 or not letter_upper.isalpha()):
        return "Invalid letter. Please provide a single letter A-Z or 'other' for non-alphabetic titles."
    
    letter_param = letter.lower() if letter_upper == "OTHER" else letter_upper
    
    logger.info(f"Fetching A-Z list for letter: {letter_param}, page: {page}")
    
    data = await make_api_request(f"/api/az/{letter_param}", {"page": page})
    
    if not data or not data.get("success"):
        return f"Unable to fetch anime for letter '{letter}'. Please try again later."
    
    anime_list = data.get("data", [])
    count = data.get("count", len(anime_list))
    
    result = f"🔤 **Anime Starting with '{letter_upper}'** (Page {page}, {count} results)\n"
    result += "=" * 50 + "\n"
    result += format_anime_list(anime_list)
    
    return result


@mcp.tool()
async def get_anime_by_producer(producer_slug: str, page: int = 1) -> str:
    """
    Get anime by producer/studio.
    
    Args:
        producer_slug: The producer/studio slug (e.g., "studio-pierrot", "mappa", 
                      "toei-animation", "bones", "madhouse", "a-1-pictures", "ufotable")
        page: Page number for pagination (default: 1)
    
    Returns:
        A formatted list of anime from the specified producer/studio
    """
    logger.info(f"Fetching anime by producer: {producer_slug}, page: {page}")
    
    data = await make_api_request(f"/api/producer/{producer_slug}", {"page": page})
    
    if not data or not data.get("success"):
        return f"Unable to fetch anime for producer '{producer_slug}'. Please check the producer slug and try again."
    
    anime_list = data.get("data", [])
    count = data.get("count", len(anime_list))
    
    result = f"🏢 **Anime by {producer_slug.replace('-', ' ').title()}** (Page {page}, {count} results)\n"
    result += "=" * 50 + "\n"
    result += format_anime_list(anime_list)
    
    return result


@mcp.tool()
async def filter_anime(
    anime_type: Optional[str] = None,
    status: Optional[str] = None,
    rated: Optional[str] = None,
    score: Optional[int] = None,
    season: Optional[str] = None,
    language: Optional[str] = None,
    genres: Optional[str] = None,
    sort: Optional[str] = None,
    page: int = 1
) -> str:
    """
    Advanced filter for anime with multiple criteria.
    
    Args:
        anime_type: Type filter - movie, tv, ova, ona, special, music (optional)
        status: Status filter - finished, airing, upcoming (optional)
        rated: Rating filter - g, pg, pg-13, r, r+, rx (optional)
        score: Minimum score filter 1-10 (optional)
        season: Season filter - spring, summer, fall, winter (optional)
        language: Language filter - sub, dub (optional)
        genres: Comma-separated genres like "action,adventure,fantasy" (optional)
        sort: Sort order - default, recently_added, recently_updated, score, 
              name_az, released_date, most_watched (optional)
        page: Page number for pagination (default: 1)
    
    Returns:
        A formatted list of anime matching the filter criteria
    """
    params = {"page": page}
    filters_applied = []
    
    if anime_type:
        if anime_type.lower() not in AVAILABLE_TYPES:
            return f"Invalid type '{anime_type}'. Available: {', '.join(AVAILABLE_TYPES)}"
        params["type"] = anime_type.lower()
        filters_applied.append(f"Type: {anime_type}")
    
    if status:
        if status.lower() not in AVAILABLE_STATUSES:
            return f"Invalid status '{status}'. Available: {', '.join(AVAILABLE_STATUSES)}"
        params["status"] = status.lower()
        filters_applied.append(f"Status: {status}")
    
    if rated:
        if rated.lower() not in AVAILABLE_RATINGS:
            return f"Invalid rating '{rated}'. Available: {', '.join(AVAILABLE_RATINGS)}"
        params["rated"] = rated.lower()
        filters_applied.append(f"Rated: {rated}")
    
    if score is not None:
        if not 1 <= score <= 10:
            return "Score must be between 1 and 10."
        params["score"] = score
        filters_applied.append(f"Min Score: {score}")
    
    if season:
        if season.lower() not in AVAILABLE_SEASONS:
            return f"Invalid season '{season}'. Available: {', '.join(AVAILABLE_SEASONS)}"
        params["season"] = season.lower()
        filters_applied.append(f"Season: {season}")
    
    if language:
        if language.lower() not in ["sub", "dub"]:
            return "Invalid language. Available: sub, dub"
        params["language"] = language.lower()
        filters_applied.append(f"Language: {language}")
    
    if genres:
        params["genres"] = genres.lower()
        filters_applied.append(f"Genres: {genres}")
    
    if sort:
        if sort.lower() not in AVAILABLE_SORT_OPTIONS:
            return f"Invalid sort '{sort}'. Available: {', '.join(AVAILABLE_SORT_OPTIONS)}"
        params["sort"] = sort.lower()
        filters_applied.append(f"Sort: {sort}")
    
    logger.info(f"Filtering anime with params: {params}")
    
    data = await make_api_request("/api/filter", params)
    
    if not data or not data.get("success"):
        return "Unable to filter anime. Please try again later."
    
    anime_list = data.get("data", [])
    count = data.get("count", len(anime_list))
    
    filter_summary = ", ".join(filters_applied) if filters_applied else "No filters"
    result = f"🔍 **Filtered Anime** ({filter_summary})\n"
    result += f"Page {page}, {count} results\n"
    result += "=" * 50 + "\n"
    result += format_anime_list(anime_list)
    
    return result


@mcp.tool()
async def check_api_health() -> str:
    """
    Check if the HiAnime API is healthy and responding.
    
    Returns:
        API health status
    """
    logger.info("Checking API health")
    
    data = await make_api_request("/")
    
    if data is not None:
        return "✅ HiAnime API is healthy and responding!"
    else:
        return "❌ HiAnime API is not responding. Please try again later."


@mcp.tool()
async def get_available_filters() -> str:
    """
    Get all available filter options for the anime search.
    
    Returns:
        A list of all available filter options including genres, types, statuses, etc.
    """
    return f"""
📚 **Available Filter Options for HiAnime MCP Server**

🎭 **Genres:**
{', '.join(AVAILABLE_GENRES)}

📁 **Types:**
{', '.join(AVAILABLE_TYPES)}

📊 **Statuses:**
{', '.join(AVAILABLE_STATUSES)}

⭐ **Ratings:**
{', '.join(AVAILABLE_RATINGS)}

🍂 **Seasons:**
{', '.join(AVAILABLE_SEASONS)}

🔤 **Sort Options:**
{', '.join(AVAILABLE_SORT_OPTIONS)}

🌐 **Languages:**
sub, dub

💡 **Tips:**
- Use 'search_anime' to find anime by name
- Use 'get_anime_details' with the slug from search results to get full details
- Use 'filter_anime' to combine multiple filters
- Use 'get_anime_episodes' to see all episodes of an anime
- Use 'mal_search' for MyAnimeList search with scores and rankings
- Use 'combined_search' to search both HiAnime and MAL simultaneously
"""


# ============================================================================
# MYANIMELIST (MAL) TOOLS
# ============================================================================

# Available MAL ranking types
MAL_RANKING_TYPES = ["all", "airing", "upcoming", "tv", "movie", "bypopularity", "favorite"]

# Available MAL anime list statuses
MAL_LIST_STATUSES = ["watching", "completed", "on_hold", "dropped", "plan_to_watch"]


def format_mal_anime_item(item: dict) -> str:
    """Format a single MAL anime item into a readable string."""
    node = item.get('node', item)
    
    title = node.get('title', 'Unknown Title')
    mal_id = node.get('id', 'N/A')
    main_picture = node.get('main_picture', {})
    picture_url = main_picture.get('medium', main_picture.get('large', ''))
    
    # Get ranking info if available
    ranking = item.get('ranking', {})
    rank = ranking.get('rank', '')
    
    result = f"""
📺 **{title}**
   ▸ MAL ID: `{mal_id}` ← Use this for MAL details lookup
   ▸ MAL URL: https://myanimelist.net/anime/{mal_id}"""
    
    if rank:
        result += f"\n   ▸ Rank: #{rank}"
    
    return result


def format_mal_anime_list(data: list[dict]) -> str:
    """Format a list of MAL anime items."""
    if not data:
        return "No anime found."
    return "\n".join(format_mal_anime_item(item) for item in data)


def format_mal_anime_details(data: dict) -> str:
    """Format detailed MAL anime information."""
    if not data:
        return "No details available."
    
    title = data.get('title', 'Unknown Title')
    mal_id = data.get('id', 'N/A')
    
    # Basic info
    media_type = data.get('media_type', 'N/A')
    status = data.get('status', 'N/A')
    num_episodes = data.get('num_episodes', 'N/A')
    
    # Dates
    start_date = data.get('start_date', 'N/A')
    end_date = data.get('end_date', 'N/A')
    
    # Scores and popularity
    mean_score = data.get('mean', 'N/A')
    rank = data.get('rank', 'N/A')
    popularity = data.get('popularity', 'N/A')
    num_scoring_users = data.get('num_scoring_users', 'N/A')
    num_list_users = data.get('num_list_users', 'N/A')
    
    # Synopsis
    synopsis = data.get('synopsis', 'No synopsis available.')
    
    # Genres
    genres = data.get('genres', [])
    genre_names = [g.get('name', '') for g in genres] if genres else []
    
    # Studios
    studios = data.get('studios', [])
    studio_names = [s.get('name', '') for s in studios] if studios else []
    
    # Alternative titles
    alt_titles = data.get('alternative_titles', {})
    japanese_title = alt_titles.get('ja', 'N/A')
    english_title = alt_titles.get('en', 'N/A')
    
    # Season and year
    start_season = data.get('start_season', {})
    season = start_season.get('season', '')
    year = start_season.get('year', '')
    season_display = f"{season.title()} {year}" if season and year else 'N/A'
    
    # Rating
    rating = data.get('rating', 'N/A')
    
    # Source
    source = data.get('source', 'N/A')
    
    result = f"""
🎬 **{title}** (MAL)

📝 **Basic Information:**
   - MAL ID: {mal_id}
   - English Title: {english_title}
   - Japanese Title: {japanese_title}
   - Type: {media_type}
   - Status: {status}
   - Episodes: {num_episodes}
   - Season: {season_display}
   - Aired: {start_date} to {end_date}
   - Rating: {rating}
   - Source: {source}

⭐ **Scores & Rankings:**
   - Mean Score: {mean_score}/10
   - Rank: #{rank}
   - Popularity: #{popularity}
   - Scoring Users: {num_scoring_users:,}
   - List Users: {num_list_users:,}

📖 **Synopsis:**
{synopsis}

🏷️ **Genres:** {', '.join(genre_names) if genre_names else 'N/A'}

🎭 **Studios:** {', '.join(studio_names) if studio_names else 'N/A'}

🔗 **MAL URL:** https://myanimelist.net/anime/{mal_id}
"""
    return result


def format_mal_user_animelist(data: list[dict]) -> str:
    """Format user's MAL anime list."""
    if not data:
        return "No anime in list."
    
    results = []
    for item in data[:25]:  # Limit to first 25 for readability
        node = item.get('node', {})
        list_status = item.get('list_status', {})
        
        title = node.get('title', 'Unknown Title')
        mal_id = node.get('id', 'N/A')
        status = list_status.get('status', 'N/A')
        score = list_status.get('score', 0)
        watched_eps = list_status.get('num_episodes_watched', 0)
        
        score_display = f"⭐ {score}/10" if score > 0 else "Not rated"
        
        results.append(f"""
📺 **{title}**
   ▸ MAL ID: {mal_id}
   ▸ Status: {status.replace('_', ' ').title()}
   ▸ Score: {score_display}
   ▸ Episodes Watched: {watched_eps}""")
    
    result = "\n".join(results)
    if len(data) > 25:
        result += f"\n\n... and {len(data) - 25} more anime."
    return result


@mcp.tool()
async def mal_search(query: str, limit: int = 10) -> str:
    """
    Search for anime on MyAnimeList (official MAL API).
    
    Args:
        query: The search term to find anime (e.g., "naruto", "one piece")
        limit: Maximum number of results to return (1-100, default: 10)
    
    Returns:
        A formatted list of anime from MyAnimeList with MAL IDs and scores
    """
    logger.info(f"MAL search for: {query}, limit: {limit}")
    
    # Clamp limit to valid range
    limit = max(1, min(100, limit))
    
    data = await make_api_request("/api/mal/search", {"query": query, "limit": limit})
    
    if not data or not data.get("success"):
        return f"Unable to search MAL for '{query}'. Please try again later."
    
    anime_list = data.get("data", [])
    
    if not anime_list:
        return f"No anime found on MAL for '{query}'."
    
    result = f"🔍 **MAL Search Results for '{query}'** ({len(anime_list)} results)\n"
    result += "=" * 50 + "\n"
    result += format_mal_anime_list(anime_list)
    
    return result


@mcp.tool()
async def mal_anime_details(mal_id: int) -> str:
    """
    Get detailed anime information from MyAnimeList by MAL ID.
    
    Args:
        mal_id: The MyAnimeList anime ID (e.g., 20, 1735, 21)
    
    Returns:
        Detailed information about the anime including scores, rankings, synopsis, etc.
    """
    logger.info(f"Fetching MAL anime details for ID: {mal_id}")
    
    data = await make_api_request(f"/api/mal/anime/{mal_id}")
    
    if not data or not data.get("success"):
        return f"Unable to fetch MAL details for anime ID '{mal_id}'. Please check the ID and try again."
    
    anime_data = data.get("data", {})
    return format_mal_anime_details(anime_data)


@mcp.tool()
async def mal_ranking(ranking_type: str = "all", limit: int = 10) -> str:
    """
    Get anime rankings from MyAnimeList.
    
    Args:
        ranking_type: Type of ranking to get. Options:
                     - all: Top Anime Series (default)
                     - airing: Top Airing Anime
                     - upcoming: Top Upcoming Anime
                     - tv: Top Anime TV Series
                     - movie: Top Anime Movies
                     - bypopularity: Most Popular Anime
                     - favorite: Most Favorited Anime
        limit: Maximum number of results to return (1-100, default: 10)
    
    Returns:
        A formatted list of top ranked anime from MAL
    """
    ranking_lower = ranking_type.lower().strip()
    
    if ranking_lower not in MAL_RANKING_TYPES:
        return f"Invalid ranking type '{ranking_type}'. Available types: {', '.join(MAL_RANKING_TYPES)}"
    
    # Clamp limit to valid range
    limit = max(1, min(100, limit))
    
    logger.info(f"Fetching MAL rankings: type={ranking_lower}, limit={limit}")
    
    data = await make_api_request("/api/mal/ranking", {"type": ranking_lower, "limit": limit})
    
    if not data or not data.get("success"):
        return f"Unable to fetch MAL rankings. Please try again later."
    
    anime_list = data.get("data", [])
    
    if not anime_list:
        return "No rankings available."
    
    # Format ranking titles
    ranking_titles = {
        "all": "Top Anime Series",
        "airing": "Top Airing Anime",
        "upcoming": "Top Upcoming Anime",
        "tv": "Top TV Series",
        "movie": "Top Movies",
        "bypopularity": "Most Popular",
        "favorite": "Most Favorited"
    }
    
    title = ranking_titles.get(ranking_lower, "Rankings")
    result = f"🏆 **MAL {title}** (Top {len(anime_list)})\n"
    result += "=" * 50 + "\n"
    result += format_mal_anime_list(anime_list)
    
    return result


@mcp.tool()
async def mal_seasonal(year: int, season: str, limit: int = 10) -> str:
    """
    Get seasonal anime from MyAnimeList.
    
    Args:
        year: The year (e.g., 2024, 2025)
        season: The season. Options:
               - winter: January - March
               - spring: April - June
               - summer: July - September
               - fall: October - December
        limit: Maximum number of results to return (1-100, default: 10)
    
    Returns:
        A formatted list of anime from the specified season
    """
    season_lower = season.lower().strip()
    
    if season_lower not in AVAILABLE_SEASONS:
        return f"Invalid season '{season}'. Available seasons: {', '.join(AVAILABLE_SEASONS)}"
    
    # Clamp limit to valid range
    limit = max(1, min(100, limit))
    
    logger.info(f"Fetching MAL seasonal anime: {season_lower} {year}, limit={limit}")
    
    data = await make_api_request("/api/mal/seasonal", {
        "year": year,
        "season": season_lower,
        "limit": limit
    })
    
    if not data or not data.get("success"):
        return f"Unable to fetch MAL seasonal anime. Please try again later."
    
    anime_list = data.get("data", [])
    
    if not anime_list:
        return f"No anime found for {season.title()} {year}."
    
    result = f"🍂 **MAL {season.title()} {year} Anime** ({len(anime_list)} results)\n"
    result += "=" * 50 + "\n"
    result += format_mal_anime_list(anime_list)
    
    return result


# ============================================================================
# COMBINED TOOLS
# ============================================================================

@mcp.tool()
async def combined_search(query: str, limit: int = 5) -> str:
    """
    Search both HiAnime and MyAnimeList simultaneously.
    
    This is useful for comparing results from both sources:
    - HiAnime: Streaming info, episodes, direct links
    - MAL: Scores, rankings, detailed metadata
    
    Args:
        query: The search term to find anime
        limit: Maximum results per source (1-20, default: 5)
    
    Returns:
        Combined results from both HiAnime and MAL
    """
    # Clamp limit to valid range
    limit = max(1, min(20, limit))
    
    logger.info(f"Combined search for: {query}, limit: {limit}")
    
    data = await make_api_request("/api/combined/search", {"query": query, "limit": limit})
    
    if not data or not data.get("success"):
        return f"Unable to perform combined search for '{query}'. Please try again later."
    
    result_data = data.get("data", {})
    hianime_results = result_data.get("hianime", [])
    mal_results = result_data.get("mal", [])
    
    result = f"🔍 **Combined Search Results for '{query}'**\n"
    result += "=" * 50 + "\n"
    
    # HiAnime results
    result += "\n📺 **HiAnime Results:**\n"
    if hianime_results:
        result += format_anime_list(hianime_results)
    else:
        result += "   No results from HiAnime.\n"
    
    # MAL results
    result += "\n\n📊 **MyAnimeList Results:**\n"
    if mal_results:
        result += format_mal_anime_list(mal_results)
    else:
        result += "   No results from MAL.\n"
    
    return result


# ============================================================================
# MYANIMELIST USER AUTHENTICATION TOOLS
# ============================================================================

@mcp.tool()
async def mal_get_auth_url(client_id: str, redirect_uri: str, client_secret: Optional[str] = None) -> str:
    """
    Get OAuth2 authorization URL for MAL user login.
    
    ⚠️ PRIVACY NOTICE: Your credentials are NOT stored. They are only used for this request.
    
    How to get your credentials:
    1. Go to https://myanimelist.net/apiconfig
    2. Create a new API application
    3. Copy your Client ID (and optionally Client Secret)
    
    Args:
        client_id: Your MAL API Client ID
        redirect_uri: Your redirect URI (must match your MAL app settings)
        client_secret: Your MAL API Client Secret (optional)
    
    Returns:
        Authorization URL to open in browser, and code_verifier to save for token exchange
    """
    logger.info("Getting MAL OAuth2 authorization URL")
    
    payload = {
        "client_id": client_id,
        "redirect_uri": redirect_uri
    }
    if client_secret:
        payload["client_secret"] = client_secret
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{HIANIME_API_BASE}/api/mal/user/auth",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=REQUEST_TIMEOUT
            )
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            logger.error(f"Failed to get auth URL: {str(e)}")
            return f"Unable to get authorization URL. Error: {str(e)}"
    
    if not data or not data.get("success"):
        return "Unable to get authorization URL. Please check your credentials and try again."
    
    auth_data = data.get("data", {})
    auth_url = auth_data.get("auth_url", "")
    code_verifier = auth_data.get("code_verifier", "")
    state = auth_data.get("state", "")
    
    return f"""
🔐 **MAL OAuth2 Authorization**

📎 **Authorization URL:**
{auth_url}

⚠️ **IMPORTANT - Save these values:**
   - Code Verifier: `{code_verifier}`
   - State: `{state}`

📝 **Next Steps:**
1. Open the authorization URL in your browser
2. Login to MyAnimeList and authorize the app
3. After redirect, copy the 'code' parameter from the URL
4. Use 'mal_exchange_token' with the code and code_verifier to get your access token
"""


@mcp.tool()
async def mal_exchange_token(
    client_id: str,
    code: str,
    code_verifier: str,
    redirect_uri: str,
    client_secret: Optional[str] = None
) -> str:
    """
    Exchange authorization code for MAL access token.
    
    ⚠️ PRIVACY NOTICE: Your tokens are NOT stored. Save them securely on your end.
    
    Args:
        client_id: Your MAL API Client ID
        code: The authorization code from the callback URL
        code_verifier: The code_verifier from the previous auth step
        redirect_uri: Your redirect URI (must match your MAL app settings)
        client_secret: Your MAL API Client Secret (optional)
    
    Returns:
        Access token and refresh token for MAL API access
    """
    logger.info("Exchanging MAL authorization code for token")
    
    payload = {
        "client_id": client_id,
        "code": code,
        "code_verifier": code_verifier,
        "redirect_uri": redirect_uri
    }
    if client_secret:
        payload["client_secret"] = client_secret
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{HIANIME_API_BASE}/api/mal/user/token",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=REQUEST_TIMEOUT
            )
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            logger.error(f"Failed to exchange token: {str(e)}")
            return f"Unable to exchange token. Error: {str(e)}"
    
    if not data or not data.get("success"):
        return "Unable to exchange token. Please check your credentials and try again."
    
    token_data = data.get("data", {})
    access_token = token_data.get("access_token", "")
    refresh_token = token_data.get("refresh_token", "")
    expires_in = token_data.get("expires_in", "")
    token_type = token_data.get("token_type", "Bearer")
    
    return f"""
✅ **MAL Token Exchange Successful!**

🔑 **Access Token:**
`{access_token}`

🔄 **Refresh Token:**
`{refresh_token}`

⏰ **Expires In:** {expires_in} seconds
🏷️ **Token Type:** {token_type}

⚠️ **IMPORTANT:**
- Save these tokens securely!
- Use the access_token with 'mal_user_animelist' and 'mal_user_profile'
- Use the refresh_token to get a new access_token when it expires
"""


@mcp.tool()
async def mal_user_animelist(
    client_id: str,
    access_token: str,
    status: Optional[str] = None,
    limit: int = 100
) -> str:
    """
    Get authenticated user's anime list from MyAnimeList.
    
    ⚠️ PRIVACY NOTICE: Your access token is NOT stored.
    
    Args:
        client_id: Your MAL API Client ID
        access_token: Your MAL access token (from mal_exchange_token)
        status: Filter by status (optional). Options:
               - watching
               - completed
               - on_hold
               - dropped
               - plan_to_watch
               - (leave empty for all)
        limit: Maximum number of results (default: 100)
    
    Returns:
        User's anime list with watch status, scores, and progress
    """
    logger.info(f"Fetching MAL user animelist, status={status}, limit={limit}")
    
    if status and status.lower() not in MAL_LIST_STATUSES:
        return f"Invalid status '{status}'. Available statuses: {', '.join(MAL_LIST_STATUSES)}"
    
    payload = {
        "client_id": client_id,
        "access_token": access_token,
        "limit": limit
    }
    if status:
        payload["status"] = status.lower()
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{HIANIME_API_BASE}/api/mal/user/animelist",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=REQUEST_TIMEOUT
            )
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            logger.error(f"Failed to fetch animelist: {str(e)}")
            return f"Unable to fetch anime list. Error: {str(e)}"
    
    if not data or not data.get("success"):
        return "Unable to fetch anime list. Please check your credentials and try again."
    
    anime_list = data.get("data", [])
    
    if not anime_list:
        status_msg = f" with status '{status}'" if status else ""
        return f"No anime found in your list{status_msg}."
    
    status_title = status.replace('_', ' ').title() if status else "All"
    result = f"📚 **Your MAL Anime List** ({status_title}, {len(anime_list)} entries)\n"
    result += "=" * 50 + "\n"
    result += format_mal_user_animelist(anime_list)
    
    return result


@mcp.tool()
async def mal_user_profile(client_id: str, access_token: str) -> str:
    """
    Get authenticated user's MAL profile information.
    
    ⚠️ PRIVACY NOTICE: Your access token and profile data are NOT stored.
    
    Args:
        client_id: Your MAL API Client ID
        access_token: Your MAL access token (from mal_exchange_token)
    
    Returns:
        User's MAL profile information
    """
    logger.info("Fetching MAL user profile")
    
    payload = {
        "client_id": client_id,
        "access_token": access_token
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{HIANIME_API_BASE}/api/mal/user/profile",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=REQUEST_TIMEOUT
            )
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            logger.error(f"Failed to fetch profile: {str(e)}")
            return f"Unable to fetch profile. Error: {str(e)}"
    
    if not data or not data.get("success"):
        return "Unable to fetch profile. Please check your credentials and try again."
    
    profile = data.get("data", {})
    
    username = profile.get("name", "Unknown")
    user_id = profile.get("id", "N/A")
    location = profile.get("location", "N/A")
    joined = profile.get("joined_at", "N/A")
    birthday = profile.get("birthday", "N/A")
    
    # Anime statistics
    anime_stats = profile.get("anime_statistics", {})
    num_watching = anime_stats.get("num_items_watching", 0)
    num_completed = anime_stats.get("num_items_completed", 0)
    num_on_hold = anime_stats.get("num_items_on_hold", 0)
    num_dropped = anime_stats.get("num_items_dropped", 0)
    num_plan_to_watch = anime_stats.get("num_items_plan_to_watch", 0)
    total_entries = anime_stats.get("num_items", 0)
    episodes_watched = anime_stats.get("num_episodes", 0)
    mean_score = anime_stats.get("mean_score", 0)
    days_watched = anime_stats.get("num_days_watched", 0)
    
    return f"""
👤 **MAL User Profile**

📝 **Basic Information:**
   - Username: {username}
   - User ID: {user_id}
   - Location: {location}
   - Birthday: {birthday}
   - Joined: {joined}

📊 **Anime Statistics:**
   - Total Entries: {total_entries}
   - Episodes Watched: {episodes_watched:,}
   - Days Watched: {days_watched:.1f}
   - Mean Score: {mean_score}/10

📈 **Status Breakdown:**
   - 📺 Watching: {num_watching}
   - ✅ Completed: {num_completed}
   - ⏸️ On Hold: {num_on_hold}
   - ❌ Dropped: {num_dropped}
   - 📋 Plan to Watch: {num_plan_to_watch}

🔗 **Profile URL:** https://myanimelist.net/profile/{username}
"""


def main():
    """Initialize and run the MCP server."""
    logger.info("Starting HiAnime MCP Server...")
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
