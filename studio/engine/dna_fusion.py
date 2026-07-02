# engine/dna_fusion.py
"""
DNA Fusion Engine — Gabungkeun atribut gambar jeung DNA Channel
"""

from typing import Dict, Any, List
from utils.logger import logger

class DNAFusion:
    """
    Fuse original scene attributes with channel DNA.
    Preserves original scene identity, enriches with channel flavor.
    """
    
    def __init__(self):
        # Mapping channel → flavor keywords
        self.channel_flavors = {
            "JAZZ": {
                "mood": ["Warm", "Intimate", "Noir"],
                "fx": ["Rain", "Smoke", "Condensation"],
                "material": ["Weathered Walnut", "Vintage Brass", "Leather"],
                "lighting": "Low-key",
                "architecture": "Speakeasy",
                "camera": "85mm f/1.4"
            },
            "BOSSA": {
                "mood": ["Relaxed", "Warm", "Productive"],
                "fx": ["Sun Flare", "Gentle Breeze"],
                "material": ["Terracotta", "Wood", "Linen"],
                "lighting": "Golden Hour",
                "architecture": "Beach House",
                "camera": "24mm f/5.6"
            },
            "BAMBU": {
                "mood": ["Calm", "Meditative", "Sacred"],
                "fx": ["Mist", "Dew Drops", "Steam"],
                "material": ["Bamboo", "Rice Paper", "Stone"],
                "lighting": "Overcast",
                "architecture": "Japanese Teahouse",
                "camera": "50mm f/2.8"
            },
            "FOREST": {
                "mood": ["Healing", "Wild", "Immersive"],
                "fx": ["Fog", "Rain", "Volumetric Light"],
                "material": ["Moss", "River Stone", "Pine"],
                "lighting": "Volumetric",
                "architecture": "Cabin",
                "camera": "24mm f/4"
            },
            "AURELIA": {
                "mood": ["Focused", "Nostalgic", "Cozy"],
                "fx": ["Dust Motes", "Warm Glow"],
                "material": ["Wood", "Paper", "Leather"],
                "lighting": "Soft",
                "architecture": "Study Room",
                "camera": "50mm f/1.8"
            },
            "ECOLIFE": {
                "mood": ["Calm", "Mindful", "Organic"],
                "fx": ["Sun Rays", "Dew"],
                "material": ["Ceramic", "Cotton", "Clay"],
                "lighting": "Morning Sun",
                "architecture": "Greenhouse",
                "camera": "50mm f/2.8 Macro"
            }
        }
    
    def fuse(self, attributes: Dict[str, Any], channel: str) -> Dict[str, Any]:
        """
        Fuse original attributes with channel DNA.
        Returns enriched attributes.
        """
        # 1. Get channel flavor
        flavor = self.channel_flavors.get(channel, self.channel_flavors.get("JAZZ"))
        
        # 2. Preserve original scene
        base = attributes.get("base", {})
        fused = {
            "scene": attributes.get("scene", "Scene"),
            "original_attributes": attributes,
            "channel": channel,
            "fused_attributes": {
                "architecture": self._merge_attributes(
                    base.get("architecture", ""),
                    flavor.get("architecture", "")
                ),
                "lighting": self._merge_attributes(
                    base.get("lighting", ""),
                    flavor.get("lighting", "")
                ),
                "material": self._merge_list_attributes(
                    attributes.get("materials", []),
                    flavor.get("material", [])
                ),
                "mood": self._merge_list_attributes(
                    attributes.get("mood", []),
                    flavor.get("mood", [])
                ),
                "fx": self._merge_list_attributes(
                    attributes.get("fx", []),
                    flavor.get("fx", [])
                ),
                "camera": self._merge_attributes(
                    base.get("camera", ""),
                    flavor.get("camera", "")
                ),
                "channel_flavor": channel,
                "fusion_name": f"{attributes.get('scene', 'Scene')} × {channel}",
                "confidence": attributes.get("confidence", 70)
            }
        }
        
        # 3. Log hasil fusi
        logger.info(f"🧬 DNA Fusion: {fused['fused_attributes']['fusion_name']}")
        
        return fused
    
    def _merge_attributes(self, original: str, channel_val: str) -> str:
        """Gabungkeun dua atribut (string)."""
        if not original:
            return channel_val
        if not channel_val:
            return original
        if original.lower() == channel_val.lower():
            return original
        return f"{original} × {channel_val}"
    
    def _merge_list_attributes(self, original: List[str], channel_list: List[str]) -> List[str]:
        """Gabungkeun dua atribut (list)."""
        result = original.copy() if original else []
        for item in channel_list:
            if item not in result:
                result.append(item)
        return result
    
    def get_fusion_description(self, fused: Dict) -> str:
        """Generate deskripsi fusi pikeun UI."""
        attrs = fused.get("fused_attributes", {})
        return f"""
**Scene:** {fused.get('scene')}
**Channel:** {fused.get('channel')}
**Fusion:** {attrs.get('fusion_name')}

**Architecture:** {attrs.get('architecture')}
**Lighting:** {attrs.get('lighting')}
**Materials:** {', '.join(attrs.get('material', []))}
**Mood:** {', '.join(attrs.get('mood', []))}
**FX:** {', '.join(attrs.get('fx', []))}
**Camera:** {attrs.get('camera')}
"""