# engine/vpos_mapper.py
VPOS_CHANNEL_MATCH = {
    "W001": {"name": "Japanese Alley", "dna": "Neo Tokyo vibe", "channels": ["AURELIA", "JAZZ"]},
    "W002": {"name": "Paris Cafe", "dna": "Romantic", "channels": ["BOSSA"]},
    "W003": {"name": "Kyoto Temple", "dna": "Zen", "channels": ["BAMBU"]},
    "W004": {"name": "London Pub", "dna": "Moody", "channels": ["JAZZ"]},
    "W005": {"name": "Desert Outpost", "dna": "Lonely", "channels": ["FOREST"]},
    "W006": {"name": "Cyberpunk Street", "dna": "High Tech", "channels": ["AURELIA"]},
    "W007": {"name": "Mountain Village", "dna": "Peaceful", "channels": ["BAMBU", "FOREST"]},
    "W008": {"name": "Harbor Dock", "dna": "Cold", "channels": ["JAZZ"]},
}

VPOS_HERO_MATCH = {
    "H001": {"role": "Jazz Pianist", "channels": ["JAZZ"]},
    "H002": {"role": "Monk", "channels": ["BAMBU", "FOREST"]},
    "H003": {"role": "Detective", "channels": ["JAZZ", "AURELIA"]},
    "H004": {"role": "Singer", "channels": ["BOSSA", "JAZZ"]},
    "H005": {"role": "Bartender", "channels": ["JAZZ", "BOSSA"]},
}

VPOS_LIGHTING_MATCH = {
    "L001": {"name": "Tungsten", "channels": ["JAZZ", "AURELIA"]},
    "L002": {"name": "Moonlight", "channels": ["FOREST", "BAMBU"]},
    "L003": {"name": "Neon", "channels": ["AURELIA"]},
    "L004": {"name": "Golden Hour", "channels": ["BOSSA", "ECOLIFE"]},
    "L005": {"name": "Candle Light", "channels": ["BAMBU", "AURELIA"]},
}

VPOS_MATERIAL_MATCH = {
    "M001": {"name": "Old Oak", "channels": ["JAZZ", "BAMBU"]},
    "M002": {"name": "Marble", "channels": ["BOSSA", "AURELIA"]},
    "M003": {"name": "Copper", "channels": ["JAZZ"]},
    "M004": {"name": "Leather", "channels": ["JAZZ", "AURELIA"]},
    "M005": {"name": "Concrete", "channels": ["FOREST", "ECOLIFE"]},
}

def map_vpos_to_dna(vpos_id: str, category: str) -> str:
    if category == "world":
        return VPOS_CHANNEL_MATCH.get(vpos_id, {}).get("dna", "")
    elif category == "hero":
        return VPOS_HERO_MATCH.get(vpos_id, {}).get("role", "")
    elif category == "lighting":
        return VPOS_LIGHTING_MATCH.get(vpos_id, {}).get("name", "")
    elif category == "material":
        return VPOS_MATERIAL_MATCH.get(vpos_id, {}).get("name", "")
    return ""

def get_channel_match(vpos_id: str, category: str) -> list:
    if category == "world":
        return VPOS_CHANNEL_MATCH.get(vpos_id, {}).get("channels", [])
    elif category == "hero":
        return VPOS_HERO_MATCH.get(vpos_id, {}).get("channels", [])
    elif category == "lighting":
        return VPOS_LIGHTING_MATCH.get(vpos_id, {}).get("channels", [])
    elif category == "material":
        return VPOS_MATERIAL_MATCH.get(vpos_id, {}).get("channels", [])
    return []