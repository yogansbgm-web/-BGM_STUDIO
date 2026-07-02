# engine/generation/variant_generator.py
from typing import List, Dict, Any

class VariantGenerator:
    """Generate creative variants based on scene and channel."""

    def generate(self, scene: Dict, attributes: Dict, channel: str) -> List[Dict]:
        """Generate 3-5 variants."""
        variants = []

        # Base scene
        base = {
            "name": scene.get("name", "Scene"),
            "attributes": attributes,
            "channel": channel
        }

        # Get variants from scene library
        scene_variants = scene.get("variants", ["Luxury", "Vintage", "Rain", "Minimal", "Noir"])

        for var in scene_variants[:5]:
            variants.append({
                "version": var,
                "description": self._build_description(base, var),
                "prompt": self._build_prompt(base, var),
                "keywords": self._build_keywords(base, var)
            })

        return variants

    def _build_description(self, base: Dict, variant: str) -> str:
        return f"{base.get('name')} in {variant} style"

    def _build_prompt(self, base: Dict, variant: str) -> str:
        return f"A cinematic {base.get('name')} with {variant} atmosphere, moody, detailed, 8k."

    def _build_keywords(self, base: Dict, variant: str) -> List[str]:
        return [base.get('name', '').lower(), variant.lower(), "cinematic", "detailed"]