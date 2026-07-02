# engine/vpos_reference.py
REFERENCE_CHANNELS = {
    "📚 Riset": [
        {"name": "Lofi Girl", "subs": "15.1M", "style": "Anime girl studying, cozy room, lo-fi", "vibe": "Focus, nostalgic, cozy", "url": "youtube.com/@lofigirl"},
        {"name": "Midnight Rain Sounds", "subs": "~15k+ views/video", "style": "Jazz + rain, cozy cafe vibes", "vibe": "Intimate, warm, melancholy", "url": "youtube.com/@midnightrainsounds"},
        {"name": "Calmed By Nature", "subs": "765K", "style": "Nature ambience, animations", "vibe": "Healing, peaceful, wild", "url": "youtube.com/@calmedbynature"},
        {"name": "Chiffon Cake", "subs": "~3.5K avg/video", "style": "Bossa nova + beach", "vibe": "Relaxed, warm, coastal", "url": "youtube.com/@chiffoncake"},
        {"name": "Bamboo Zen Flow", "subs": "7.81K", "style": "Zen + bamboo + mist", "vibe": "Calm, meditative, serene", "url": "youtube.com/@bamboovenflow"}
    ]
}

def get_reference(mood: str) -> list:
    return REFERENCE_CHANNELS.get(mood, [])