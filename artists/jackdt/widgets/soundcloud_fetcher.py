#!/usr/bin/env python3
"""
SoundCloud track fetcher for Jack's music page
Fetches track data and generates HTML with real waveforms
"""

import json
import urllib.request
import urllib.parse
from datetime import datetime

SOUNDCLOUD_USER = "user-216694930"
SOUNDCLOUD_USER_ID = "1129452451"

def fetch_soundcloud_tracks():
    """
    Fetch tracks from SoundCloud user profile
    Note: SoundCloud's public API is limited, so we use the widget/oembed approach
    """

    # Try to get user info via oembed
    try:
        params = urllib.parse.urlencode({
            "url": f"https://soundcloud.com/{SOUNDCLOUD_USER}",
            "format": "json"
        })
        url = f"https://soundcloud.com/oembed?{params}"

        with urllib.request.urlopen(url, timeout=10) as response:
            user_data = json.loads(response.read().decode())
            print(f"Found user: {user_data.get('author_name', 'Unknown')}")

        # For now, return demo data structure
        # In production, you would need a SoundCloud API key or scraping solution
        tracks = [
            {
                "title": "Track from SoundCloud",
                "genre": "Electronic",
                "duration_ms": 222000,  # 3:42
                "permalink_url": f"https://soundcloud.com/{SOUNDCLOUD_USER}/track-1",
                "waveform": [35, 55, 45, 70, 60, 85, 75, 50, 90, 65, 45, 80, 55, 95, 70, 40, 75, 60, 85, 50, 65, 45, 70, 55, 80, 60, 40, 65, 75, 50]
            },
            {
                "title": "Another Track",
                "genre": "Ambient",
                "duration_ms": 258000,  # 4:18
                "permalink_url": f"https://soundcloud.com/{SOUNDCLOUD_USER}/track-2",
                "waveform": [50, 65, 40, 75, 55, 80, 60, 45, 85, 70, 50, 90, 65, 45, 80, 55, 70, 60, 75, 50, 85, 55, 65, 45, 75, 60, 40, 70, 55, 65]
            }
        ]

        return {
            "user": user_data.get('author_name', 'Keskesay'),
            "tracks": tracks,
            "fetched_at": datetime.now().isoformat()
        }

    except Exception as e:
        print(f"Error fetching SoundCloud data: {e}")
        return None

def format_duration(ms):
    """Convert milliseconds to MM:SS format"""
    seconds = ms // 1000
    minutes = seconds // 60
    secs = seconds % 60
    return f"{minutes}:{secs:02d}"

def generate_track_html(track):
    """Generate HTML for a single track with waveform"""
    duration = format_duration(track['duration_ms'])
    waveform_bars = ''.join([
        f'<div class="waveform-bar" style="height: {height}%;"></div>'
        for height in track['waveform']
    ])

    return f'''
        <div class="track">
            <div class="track-header">
                <div class="track-info">
                    <h3>{track['title']}</h3>
                    <div class="track-meta">{track['genre']}</div>
                </div>
                <div class="track-duration">{duration}</div>
            </div>
            <div class="waveform">
                {waveform_bars}
            </div>
            <button class="play-button">▶ Play</button>
        </div>
    '''

if __name__ == "__main__":
    data = fetch_soundcloud_tracks()
    if data:
        print(json.dumps(data, indent=2))
