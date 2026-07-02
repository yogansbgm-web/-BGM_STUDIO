# engine/creative_director.py
from typing import Dict, Any
from models.detector_result import GapResult, CreativePlan

class CreativeDirector:
    def generate(self, gap_result: GapResult, dna: Dict[str, Any]) -> CreativePlan:
        recommendations = []
        for item in gap_result.missing:
            recommendations.append(f"Tambah {item.element}")
        for item in gap_result.conflicts:
            recommendations.append(f"Ganti {item.element} → {item.target}")

        final_prompt = f"A cinematic {gap_result.channel.lower()} scene with " + ", ".join(recommendations[:3])

        return CreativePlan(
            channel=gap_result.channel,
            current_score=gap_result.confidence,
            predicted_score=min(95.0, gap_result.confidence + 15),
            recommendations=recommendations,
            final_prompt=final_prompt,
            delta=f"+{min(95.0, gap_result.confidence + 15) - gap_result.confidence:.1f}%"
        )