# engine/generation/motion_planner.py
from typing import Dict, Any

class MotionPlanner:
    """Plan motion for video generation based on scene."""

    def plan(self, scene: Dict, channel: str) -> Dict:
        """Generate motion plan."""
        scene_name = scene.get("name", "").lower()
        channel_lower = channel.lower()

        if "jazz" in scene_name or "speakeasy" in scene_name or "jazz" in channel_lower:
            return {
                "primary": "Slow smoke drift",
                "secondary": "Gentle candle flicker",
                "camera": "Static tripod, subtle pan",
                "duration": "4s loop",
                "style": "Cinematic noir",
                "shutter": "1/60",
                "lens": "50mm f/1.8"
            }
        elif "bamboo" in scene_name or "zen" in scene_name or "bambu" in channel_lower:
            return {
                "primary": "Mist drifting",
                "secondary": "Bamboo sway",
                "camera": "Static, wide angle",
                "duration": "5s loop",
                "style": "Meditative",
                "shutter": "1/120",
                "lens": "24mm f/2.8"
            }
        elif "study" in scene_name or "lofi" in scene_name or "aurelia" in channel_lower:
            return {
                "primary": "Slow head nod",
                "secondary": "Pen writing motion",
                "camera": "Static, medium close-up",
                "duration": "3s loop",
                "style": "Cozy, focused",
                "shutter": "1/100",
                "lens": "50mm f/1.4"
            }
        else:
            return {
                "primary": "Gentle movement",
                "secondary": "Subtle motion",
                "camera": "Static",
                "duration": "4s loop",
                "style": "Ambient",
                "shutter": "1/120",
                "lens": "35mm f/2.8"
            }