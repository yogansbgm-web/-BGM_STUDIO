# engine/vpos_selector.py
TIME_MAP = {
    "🌅 Pagi": "Morning",
    "☀️ Siang": "Day",
    "🌇 Sore": "Evening",
    "🌙 Malam": "Night"
}

MOOD_MAP = {
    "🏛️ Luxury": {"density": "Open", "weather": "Sunny", "dna": "Elegant", "mode": "auto"},
    "🌿 Nature": {"density": "Low", "weather": "Fog", "dna": "Natural", "mode": "auto"},
    "🏠 Room": {"density": "Medium", "weather": "Rain", "dna": "Cozy", "mode": "auto"},
    "📚 Riset": {"density": "Dense", "weather": "Rain", "dna": "Focused", "mode": "reference"}
}

STYLE_MAP = {
    "📸 Standard 50mm": {"lens": "50mm f/1.8", "camera": "Full-frame"},
    "📸 Wide 24mm": {"lens": "24mm f/2.8", "camera": "APS-C"},
    "📸 Tele 85mm": {"lens": "85mm f/1.4", "camera": "Full-frame"},
    "📸 Macro 100mm": {"lens": "100mm f/2.8", "camera": "Full-frame"},
    "🎞️ Vintage": {"lens": "50mm f/1.4", "camera": "Film", "filter": "Grain + Warm"},
    "🎨 Cinematic": {"lens": "35mm f/1.4", "camera": "Arri Alexa", "filter": "Teal & Orange"}
}

def get_user_mode(mood: str) -> str:
    return MOOD_MAP.get(mood, {}).get("mode", "auto")

def get_vpos_filters(time: str, mood: str, style: str) -> dict:
    time_val = TIME_MAP.get(time, "Night")
    mood_data = MOOD_MAP.get(mood, MOOD_MAP["📚 Riset"])
    style_data = STYLE_MAP.get(style, STYLE_MAP["📸 Standard 50mm"])
    return {
        "time": time_val,
        "density": mood_data["density"],
        "weather": mood_data["weather"],
        "dna": mood_data["dna"],
        "lens": style_data["lens"],
        "camera": style_data["camera"],
        "filter": style_data.get("filter", "Natural"),
    }

def filter_vpos_by_user(vpos_data: dict, user_filters: dict) -> dict:
    filtered = {"world": [], "hero": [], "lighting": [], "material": []}
    time = user_filters.get("time", "Night")
    density = user_filters.get("density", "Medium")
    dna = user_filters.get("dna", "Focused")
    
    for w in vpos_data.get("worlds", []):
        if w.get("time") == time and w.get("density") == density:
            filtered["world"].append(w)
    for h in vpos_data.get("heroes", []):
        if dna.lower() in h.get("emotion", "").lower():
            filtered["hero"].append(h)
    for l in vpos_data.get("lightings", []):
        if dna.lower() in l.get("mood", "").lower():
            filtered["lighting"].append(l)
    for m in vpos_data.get("materials", []):
        if dna.lower() in m.get("style", "").lower():
            filtered["material"].append(m)
    return filtered