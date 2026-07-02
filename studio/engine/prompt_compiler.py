# engine/prompt_compiler.py
from typing import Dict, Any, List
from models.detector_result import CreativePlan

class PromptAdapter:
    def compile(self, plan: CreativePlan, dna: Dict[str, Any]) -> str:
        raise NotImplementedError

class MidjourneyAdapter(PromptAdapter):
    def compile(self, plan: CreativePlan, dna: Dict[str, Any]) -> str:
        return plan.final_prompt + " --ar 16:9 --style raw --s 50 --v 6.1"

class SDXLAdapter(PromptAdapter):
    def compile(self, plan: CreativePlan, dna: Dict[str, Any]) -> str:
        return plan.final_prompt

class FluxAdapter(PromptAdapter):
    def compile(self, plan: CreativePlan, dna: Dict[str, Any]) -> str:
        return f"(((cinematic {plan.channel}))), {plan.final_prompt}"

class KlingAdapter(PromptAdapter):
    def compile(self, plan: CreativePlan, dna: Dict[str, Any]) -> str:
        return f"cinematic shot, {plan.channel}, {plan.final_prompt}, camera 4s loop 24fps"

class RunwayAdapter(PromptAdapter):
    def compile(self, plan: CreativePlan, dna: Dict[str, Any]) -> str:
        return f"cinematic shot, {plan.channel}, {plan.final_prompt}, mood"

# ============================================================
# PARTIAL PROMPT — Vocabulary Builder
# ============================================================

def build_partial_prompt_vocabulary(dna: Dict[str, Any], gap_result: Dict[str, Any] = None) -> str:
    """
    Build keyword-based partial prompt (for SDXL Positive / Partial).
    Returns comma-separated descriptive keywords.
    """
    parts = []
    if dna.get('architecture'):
        parts.append(dna['architecture'].lower())
    if dna.get('hero'):
        parts.extend([h.lower() for h in dna['hero'][:3]])
    if dna.get('lighting'):
        parts.append(dna['lighting'].lower())
    if dna.get('mood'):
        parts.append(dna['mood'][0].lower())
    if dna.get('palette'):
        parts.extend([p.lower() for p in dna['palette'][:2]])
    if dna.get('material'):
        parts.extend([m.lower() for m in dna['material'][:2]])
    if dna.get('fx'):
        parts.extend([f.lower() for f in dna['fx'][:2]])
    if gap_result:
        if gap_result.get('missing'):
            for item in gap_result['missing']:
                parts.append(item.get('element', '').lower())
        if gap_result.get('conflict'):
            for item in gap_result['conflict']:
                target = item.get('target', '')
                if target:
                    parts.append(target.lower())
        if gap_result.get('extra'):
            for item in gap_result['extra']:
                parts.append(item.get('element', '').lower())
    
    # Hapus duplikat (jaga urutan)
    seen = set()
    unique = []
    for p in parts:
        if p and p not in seen:
            seen.add(p)
            unique.append(p)
    return ", ".join(unique)