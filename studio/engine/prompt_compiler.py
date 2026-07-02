# engine/prompt_compiler.py
from typing import Dict, Any
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