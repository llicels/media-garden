import requests
import os
import json
import time
from dotenv import load_dotenv
import isodate


load_dotenv()

TMDB_TOKEN = os.getenv("TMDB_TOKEN")
YOUTUBE_API_KEY= os.getenv("YOUTUBE_API_KEY")
PROVIDER = os.getenv("PROVIDER")

# =====================
# CONFIG
# =====================

YOUTUBE_CHANNELS = {
    "entertainment": [
        "UC-NW3bCGpuJm6fz-9DyXMjg",
        "UCMpWpGXG8tlWA6Xban2m6oA",
        "UCjIgdaem1mo7Ozi3Ppb8a7Q",
        "UCLuYADJ6hESLHX87JnsGbjA",
        "UCMdzKbGx5e4xtnKejh9aJVg",
        "UCw8_yg1camlWnYfX_0tfECw",
        "UCr3dtVIm3nL7I-Yjn2PxxIQ",
        "UCtrjFP7i92_30uv6IehwE5Q",
        "UChmOR1T5ZNnbRUba3lHRTOg",
        "UC3TYvpGVVD9DrqRQAMUqK1A",
        "UCS9K27KW782vvAwTHJpVePQ",
        "UCn9Erjy00mpnWeLnRqhsA1g",
    ],
    "productivity": [
        "UC9N7LoUG8eYNWDTAzUWWQ5A",
        "UCNMUIjeu84SPmii-Z-M1l0w",
        "UCBnHZUkOqg73h7gWiIu0ITA",
        "UCh5wgwwsHnW4038EORUiuXw",
        "UCq8GIvVUKcsTTYUIkH6Q-bw",
        "UCFU6Qn5FWHEjm1ZDzQ4HsNQ",
        "UCeGUqJFEuNCiECPrHMup3tg",
        "UCnq4hLbdnUDFZBUAGQGufkw",
        "UCJ2rcz01WV9kfLCZ7koy4kQ",
    ]
}

CACHE_FILE = "instance/youtube_cache.json"
CACHE_TTL = 3600  # 10 minutes


VIDEO_CACHE = []
LAST_FETCH = 0

# =====================
# MOVIES
# =====================

def popularMovies(page):
    url = f"https://api.themoviedb.org/3/discover/movie?include_adult=false&language=en-US&page={page}&sort_by=popularity.desc"

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {TMDB_TOKEN}"
    }

    response = requests.get(url, headers=headers).json()

    movies = []

    for item in response["results"]:
        if not item["poster_path"]:
            continue

        movies.append({
            "type": "movie",
            "title": item["title"],
            "image": f"https://image.tmdb.org/t/p/w500/{item['poster_path']}",
            "link": f"https://{PROVIDER}/?video_id={item['id']}&tmdb=1", 
            "id": item["id"]
        })

    return movies


# =====================
# SERIES
# =====================

def popularSeries(page):
    url = f"https://api.themoviedb.org/3/discover/tv?include_adult=false&language=en-US&page={page}&sort_by=popularity.desc"

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {TMDB_TOKEN}"
    }

    response = requests.get(url, headers=headers).json()

    series = []

    for item in response["results"]:
        if not item["poster_path"]:
            continue

        series.append({
            "type": "tv",
            "title": item["name"],
            "image": f"https://image.tmdb.org/t/p/w500/{item['poster_path']}",
            "link": f"https://{PROVIDER}/?video_id={item['id']}&tmdb=1&s=1&e=1",
            "id": item["id"]
        })

    return series


# =====================
# YOUTUBE
# =====================

def load_cache():
    if not os.path.exists(CACHE_FILE):
        return None

    with open(CACHE_FILE, "r") as f:
        data = json.load(f)

    if time.time() - data["timestamp"] > CACHE_TTL:
        return None

    return data["videos"]

def save_cache(videos):
    with open(CACHE_FILE, "w") as f:
        json.dump({
            "timestamp": time.time(),
            "videos": videos
        }, f)

def get_uploads_playlist(channel_id):
    url = "https://www.googleapis.com/youtube/v3/channels"
    params = {
        "part": "contentDetails",
        "id": channel_id,
        "key": YOUTUBE_API_KEY
    }

    res = requests.get(url, params=params).json()
    return res["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

def parse_duration(duration):
    # PT1H2M3S → segundos
    return isodate.parse_duration(duration).total_seconds()

def youtubeVideosByCategory(force_refresh=False):
    if not force_refresh:
        cached = load_cache()
        if cached:
            print("Using cache")
            return cached

    result = []

    for category, channels in YOUTUBE_CHANNELS.items():
        videos = []

        # 🔥 TEM QUE ESTAR DENTRO DA CATEGORIA
        for channel in channels:
            playlist_id = get_uploads_playlist(channel)

            url = "https://www.googleapis.com/youtube/v3/playlistItems"
            params = {
                "part": "snippet",
                "playlistId": playlist_id,
                "maxResults": 50,
                "key": YOUTUBE_API_KEY
            }

            response = requests.get(url, params=params).json()
            items = response.get("items")

            if not items:
                print("❌ YouTube API error:", response)
                continue

            video_map = []
            videos_data = []

            # 🔥 PASSO 1
            for item in items:
                snippet = item.get("snippet", {})
                resource = snippet.get("resourceId", {})

                video_id = resource.get("videoId")
                if not video_id:
                    continue

                title = snippet.get("title", "")

                videos_data.append({
                    "id": video_id,
                    "title": title,
                    "image": snippet["thumbnails"]["high"]["url"],
                    "publishedAt": snippet.get("publishedAt", "")
                })

                video_map.append(video_id)

            # 🔥 PASSO 2
            video_info = {}

            if video_map:
                video_url = "https://www.googleapis.com/youtube/v3/videos"
                video_params = {
                    "part": "contentDetails",
                    "id": ",".join(video_map),
                    "key": YOUTUBE_API_KEY
                }

                video_response = requests.get(video_url, params=video_params).json()

                for v in video_response.get("items", []):
                    vid = v["id"]
                    duration = v["contentDetails"]["duration"]
                    video_info[vid] = parse_duration(duration)

            # 🔥 PASSO 3
            for v in videos_data:
                vid = v["id"]

                duration = video_info.get(vid)

                # filtra shorts
                if duration is not None and duration <= 60:
                    continue

                videos.append({
                    "type": "youtube",
                    "title": v["title"],
                    "image": v["image"],
                    "link": f"https://www.youtube.com/embed/{vid}",
                    "id": vid,
                    "publishedAt": v["publishedAt"]
                })

        # ordenar categoria inteira (depois de todos canais)
        videos.sort(key=lambda x: x["publishedAt"], reverse=True)

        result.append({
            "category": category,
            "videos": videos
        })

    save_cache(result)
    return result


# =====================
# SEARCH
# =====================

def search(name):
    url = f"https://api.themoviedb.org/3/search/multi?query={name}&include_adult=false&language=en-US&page=1"

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {TMDB_TOKEN}"
    }

    response = requests.get(url, headers=headers).json()

    content = []

    for item in response["results"]:
        if not item.get("poster_path"):
            continue

        if item["media_type"] == "movie":
            content.append({
                "type": "movie",
                "title": item["title"],
                "image": f"https://image.tmdb.org/t/p/w500/{item['poster_path']}",
                "link": f"https://{PROVIDER}/?video_id={item['id']}&tmdb=1",
                "id": item["id"]
            })

        elif item["media_type"] == "tv":
            content.append({
                "type": "tv",
                "title": item["name"],
                "image": f"https://image.tmdb.org/t/p/w500/{item['poster_path']}",
                "link": f"https://{PROVIDER}/?video_id={item['id']}&tmdb=1&s=1&e=1",
                "id": item["id"]
            })

    return content

def searchYoutube(query):
    url = "https://www.googleapis.com/youtube/v3/search"

    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "maxResults": 12,
        "key": YOUTUBE_API_KEY
    }

    response = requests.get(url, params=params).json()

    videos = []

    for item in response["items"]:
        snippet = item["snippet"]

        title = snippet["title"]

        if "shorts" in title.lower():
            continue

        video_id = item["id"]["videoId"]

        videos.append({
            "type": "youtube",
            "title": title,
            "image": snippet["thumbnails"]["high"]["url"],
            "link": f"https://www.youtube.com/embed/{video_id}",
            "id": video_id
        })

    return [{
        "category": "search",
        "videos": videos
    }]


# =====================
# SERIES INFO
# =====================

def seriesInfo(id):
    url = f"https://api.themoviedb.org/3/tv/{id}"

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {TMDB_TOKEN}"
    }

    response = requests.get(url, headers=headers).json()

    info = []

    for season in response["seasons"]:
        info.append([season["season_number"], season["episode_count"]])

    return info