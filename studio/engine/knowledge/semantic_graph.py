# engine/knowledge/semantic_graph.py
from typing import Dict, List, Any, Optional
import yaml
from pathlib import Path
from config.constants import DATA_DIR
from utils.logger import logger

class SemanticGraph:
    """Manage relationships between attributes (knowledge graph)."""
    
    def __init__(self):
        self.relations = self._load_relations()
        self.vocabulary = self._load_vocabulary()
        self.scenes = self._load_scenes()
    
    def _load_relations(self) -> Dict:
        path = DATA_DIR / "knowledge" / "relation.yaml"
        try:
            with open(path, "r") as f:
                return yaml.safe_load(f) or {"relations": []}
        except Exception:
            return {"relations": []}
    
    def _load_vocabulary(self) -> Dict:
        path = DATA_DIR / "knowledge" / "vocabulary.yaml"
        try:
            with open(path, "r") as f:
                return yaml.safe_load(f) or {"vocabulary": {}}
        except Exception:
            return {"vocabulary": {}}
    
    def _load_scenes(self) -> List:
        path = DATA_DIR / "knowledge" / "scene_library.yaml"
        try:
            with open(path, "r") as f:
                data = yaml.safe_load(f)
                return data.get("scenes", [])
        except Exception:
            return []
    
    def get_related(self, source: str) -> List[Dict]:
        """Get all related attributes for a given source."""
        results = []
        for rel in self.relations.get("relations", []):
            if rel.get("source", "").lower() == source.lower():
                results.append(rel)
        return results
    
    def get_synonyms(self, word: str) -> List[str]:
        """Get synonyms for a given word from vocabulary."""
        vocab = self.vocabulary.get("vocabulary", {})
        for key, values in vocab.items():
            if word.lower() == key.lower():
                return values
            for val in values:
                if val.lower() == word.lower():
                    return [key] + values
        return []
    
    def match_scene(self, attributes: Dict) -> Optional[Dict]:
        """Find the best matching scene from library based on attributes."""
        best_match = None
        best_score = 0
        
        extracted_objects = attributes.get("objects", [])
        extracted_scenes = attributes.get("scenes", [])
        extracted_fx = attributes.get("fx", [])
        extracted_emotions = attributes.get("emotions", [])
        
        for scene in self.scenes:
            score = 0
            scene_name = scene.get("name", "").lower()
            scene_attrs = scene.get("attributes", {})
            
            # Check if scene name matches
            for es in extracted_scenes:
                if es.lower() in scene_name:
                    score += 10
            
            # Check objects
            for obj in extracted_objects:
                if any(obj.lower() in anchor.lower() for anchor in scene_attrs.get("anchor", [])):
                    score += 5
                if any(obj.lower() in mat.lower() for mat in scene_attrs.get("material", [])):
                    score += 3
            
            # Check FX
            for fx in extracted_fx:
                if any(fx.lower() in sfx.lower() for sfx in scene_attrs.get("fx", [])):
                    score += 4
            
            # Check emotions
            for emo in extracted_emotions:
                if any(emo.lower() in mood.lower() for mood in scene_attrs.get("mood", [])):
                    score += 4
            
            if score > best_score:
                best_score = score
                best_match = scene
        
        if best_match:
            best_match["score"] = best_score
        
        return best_match
    
    def get_scene_variants(self, scene_id: str) -> List[str]:
        """Get available variants for a scene."""
        for scene in self.scenes:
            if scene.get("id") == scene_id:
                return scene.get("variants", [])
        return []
    
    def suggest_attributes(self, scene_name: str, channel: str) -> Dict:
        """Suggest additional attributes based on scene + channel."""
        result = {"materials": [], "fx": [], "mood": [], "camera": []}
        scene_name_lower = scene_name.lower()
        
        for scene in self.scenes:
            if scene_name_lower in scene.get("name", "").lower():
                attrs = scene.get("attributes", {})
                result["materials"] = attrs.get("material", [])
                result["fx"] = attrs.get("fx", [])
                result["mood"] = attrs.get("mood", [])
                result["camera"] = attrs.get("camera", [])
                break
        
        # Filter by channel if possible
        # This is a simplified version
        return result