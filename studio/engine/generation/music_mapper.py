# engine/generation/music_mapper.py
from typing import Dict, Any

class MusicMapper:
    """Map scene to music recommendations."""

    def map(self, scene: Dict, channel: str) -> Dict:
        """Generate music suggestion based on scene."""
        scene_name = scene.get("name", "").lower()
        channel_lower = channel.lower()

        if "jazz" in scene_name or "speakeasy" in scene_name or "jazz" in channel_lower:
            return {
                "genre": "Smooth Jazz",
                "tempo": "60-70 BPM",
                "instruments": ["Piano", "Saxophone", "Double Bass"],
                "mood": "Intimate, Warm, Melancholic",
                "recommended": "Smooth jazz with rain ambience",
                "suno_prompt": "Smooth jazz, intimate, warm, melancholic, soft rain ambience, 65 BPM"
            }
        elif "bamboo" in scene_name or "zen" in scene_name or "bambu" in channel_lower:
            return {
                "genre": "Ambient / Zen",
                "tempo": "40-50 BPM",
                "instruments": ["Koto", "Shakuhachi", "Singing Bowls"],
                "mood": "Calm, Meditative, Serene",
                "recommended": "Traditional Japanese zen music",
                "suno_prompt": "Zen meditation, koto, shakuhachi, serene, calm, 45 BPM"
            }
        elif "study" in scene_name or "lofi" in scene_name or "aurelia" in channel_lower:
            return {
                "genre": "Lo-fi Hip Hop",
                "tempo": "70-80 BPM",
                "instruments": ["Piano", "Drums", "Bass"],
                "mood": "Focused, Nostalgic, Cozy",
                "recommended": "Lo-fi chillhop with vinyl crackle",
                "suno_prompt": "Lo-fi hip hop, piano, nostalgic, cozy, vinyl crackle, 75 BPM"
            }
        else:
            return {
                "genre": "Ambient",
                "tempo": "70-80 BPM",
                "instruments": ["Piano", "Strings"],
                "mood": "Calm, Focused",
                "recommended": "Ambient instrumental",
                "suno_prompt": "Ambient, calm, focused, piano, strings, 75 BPM"
            }