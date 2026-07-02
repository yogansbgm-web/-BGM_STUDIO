# engine/ai/openrouter_client.py
import os
import json
import requests
import base64
from io import BytesIO
from typing import Optional, Dict, Any, List
from PIL import Image
from utils.logger import logger
from config.constants import OPENROUTER_API_KEY

class OpenRouterClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or OPENROUTER_API_KEY
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not set")
        self.base_url = "https://openrouter.ai/api/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.default_vision_model = "qwen/qwen2.5-vl"
        self.default_text_model = "openai/gpt-4o-mini"

    def chat_completion(self, model: str, messages: List[Dict], temperature: float = 0.7, max_tokens: int = 1024) -> Dict:
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        response = requests.post(f"{self.base_url}/chat/completions", headers=self.headers, json=payload, timeout=60)
        response.raise_for_status()
        return response.json()

    def vision_detect(self, image: Image.Image, model: Optional[str] = None) -> Dict[str, Any]:
        model = model or self.default_vision_model
        buff = BytesIO()
        image.convert("RGB").save(buff, format="JPEG", quality=85)
        img_b64 = base64.b64encode(buff.getvalue()).decode()

        prompt = """
        Analyze this image and return ONLY a valid JSON object with this structure:
        {
            "scene": "...",
            "architecture": "...",
            "materials": ["..."],
            "lighting": "...",
            "weather": "...",
            "time": "...",
            "camera": "...",
            "mood": ["..."],
            "objects": ["..."],
            "colors": ["..."],
            "composition": "...",
            "foreground": "...",
            "background": "...",
            "motion": "...",
            "confidence": 0.0
        }
        Only JSON, no other text.
        """
        messages = [{"role": "user", "content": [{"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}, {"type": "text", "text": prompt}]}]
        response = self.chat_completion(model, messages, temperature=0.2)
        content = response["choices"][0]["message"]["content"]
        # Bersihkan markdown
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return {"raw": content, "error": "JSON parse failed"}

    def text_completion(self, prompt: str, model: Optional[str] = None, temperature: float = 0.7) -> str:
        model = model or self.default_text_model
        messages = [{"role": "user", "content": prompt}]
        response = self.chat_completion(model, messages, temperature)
        return response["choices"][0]["message"]["content"]