# engine/knowledge/matcher.py
from typing import Dict, List, Any, Optional
from engine.knowledge.semantic_graph import SemanticGraph

class SceneMatcher:
    def __init__(self):
        self.graph = SemanticGraph()
    
    def match(self, attributes: Dict, channel: str) -> Dict:
        scene = self.graph.match_scene(attributes)
        if scene:
            # Update scene with channel-specific attributes
            variants = self.graph.get_scene_variants(scene.get("id", ""))
            scene["channel_variants"] = variants
            scene["suggestions"] = self.graph.suggest_attributes(scene.get("name", ""), channel)
        return scene