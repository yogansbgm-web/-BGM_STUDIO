# engine/creative_director.py
from typing import Dict, Any, List
from models.detector_result import CreativePlan

class CreativeDirector:
    def generate(self, gap_result: Dict[str, Any], dna: Dict[str, Any]) -> CreativePlan:
        """
        gap_result is a dict (from GapResult.to_dict()).
        """
        # Ambil data tina dict
        channel = gap_result.get("channel", "JAZZ")
        confidence = gap_result.get("confidence", 70)
        
        # Ambil missing, conflicts, etc.
        missing = gap_result.get("missing", [])   # list of dicts
        conflicts = gap_result.get("conflict", [])
        
        # Rekomendasi
        recommendations = []
        for item in missing:
            element = item.get("element", "")
            recommendations.append(f"Tambah {element}")
        for item in conflicts:
            element = item.get("element", "")
            target = item.get("target", "")
            recommendations.append(f"Ganti {element} → {target}")
        
        # Final prompt (deskriptif)
        final_prompt = self._build_prompt(channel, dna, missing, conflicts)
        
        # Prediksi skor
        predicted = min(95.0, confidence + 15)
        
        return CreativePlan(
            channel=channel,
            current_score=confidence,
            predicted_score=predicted,
            recommendations=recommendations,
            final_prompt=final_prompt,
            delta=f"+{predicted - confidence:.1f}%"
        )
    
    def _build_prompt(self, channel: str, dna: Dict, missing: List, conflicts: List) -> str:
        architecture = dna.get("architecture", "")
        hero = ", ".join(dna.get("hero", [])[:2])
        mood = dna.get("mood", [""])[0]
        lighting = dna.get("lighting", "")
        palette = ", ".join(dna.get("palette", [])[:2])
        
        prompt_parts = [
            f"A cinematic {architecture}",
            f"with {hero}",
            f"featuring {mood} atmosphere",
            f"bathed in {lighting} lighting",
            f"with {palette} tones"
        ]
        
        # Tambah missing elements descriptively
        for item in missing:
            element = item.get("element", "")
            if element:
                prompt_parts.append(f"with {element.lower()} elements")
        
        # Tambah conflict resolutions
        for item in conflicts:
            target = item.get("target", "")
            if target:
                prompt_parts.append(f"featuring {target.lower()} instead")
        
        return ", ".join(prompt_parts) + "."