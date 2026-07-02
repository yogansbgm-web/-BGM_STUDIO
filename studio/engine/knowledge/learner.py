# engine/knowledge/learner.py
from typing import Dict, List, Any
import yaml
from pathlib import Path
from datetime import datetime
from config.constants import DATA_DIR
from utils.logger import logger
import os

class KnowledgeLearner:
    """Learn from projects and update knowledge database."""
    
    def __init__(self):
        self.vocab_path = DATA_DIR / "knowledge" / "vocabulary.yaml"
        self.relation_path = DATA_DIR / "knowledge" / "relation.yaml"
    
    def learn_from_project(self, project_state: Dict, attributes: Dict) -> Dict:
        """
        Extract new knowledge from a completed project.
        Returns: summary of what was learned.
        """
        learned = {
            "new_vocabulary": [],
            "new_relations": [],
            "confidence": 0
        }
        
        # 1. Extract potential new vocabulary
        raw_description = attributes.get("raw_description", "")
        new_words = self._extract_new_vocabulary(raw_description)
        if new_words:
            learned["new_vocabulary"] = new_words
            self._add_vocabulary(new_words)
        
        # 2. Extract new relations
        new_relations = self._extract_new_relations(attributes)
        if new_relations:
            learned["new_relations"] = new_relations
            self._add_relations(new_relations)
        
        # 3. Confidence based on detector score
        confidence = attributes.get("confidence", 70)
        learned["confidence"] = confidence
        
        return learned
    
    def _extract_new_vocabulary(self, text: str) -> List[str]:
        """Extract words that might be new vocabulary."""
        # Simplified: Look for capitalized adjectives or uncommon nouns
        words = []
        common = ["piano", "whiskey", "bamboo", "coffee", "book", "lamp"]
        potential = [w for w in text.split() if w[0].isupper() and len(w) > 4]
        
        for w in potential:
            if w.lower() not in common:
                words.append(w)
        
        return words[:3]  # Limit to 3 per project
    
    def _add_vocabulary(self, new_words: List[str]):
        """Add new words to vocabulary.yaml."""
        try:
            with open(self.vocab_path, "r") as f:
                data = yaml.safe_load(f) or {"vocabulary": {}}
            
            # Add to "learned" category
            if "learned" not in data["vocabulary"]:
                data["vocabulary"]["learned"] = []
            
            for word in new_words:
                if word not in data["vocabulary"]["learned"]:
                    data["vocabulary"]["learned"].append(word)
            
            with open(self.vocab_path, "w") as f:
                yaml.dump(data, f)
            
            logger.info(f"Added new vocabulary: {new_words}")
        except Exception as e:
            logger.error(f"Failed to add vocabulary: {e}")
    
    def _extract_new_relations(self, attributes: Dict) -> List[Dict]:
        """Extract new relations from attributes."""
        relations = []
        base = attributes.get("base", {})
        objects = attributes.get("objects", [])
        
        # Simple heuristic: pair anchor with FX
        anchor = attributes.get("anchor", "")
        fx_list = attributes.get("fx", [])
        
        for fx in fx_list:
            if fx and anchor:
                relations.append({
                    "source": fx,
                    "target": anchor,
                    "strength": 0.5,
                    "context": [base.get("mood", ["General"])[0]]
                })
        
        return relations
    
    def _add_relations(self, new_relations: List[Dict]):
        """Add new relations to relation.yaml."""
        try:
            with open(self.relation_path, "r") as f:
                data = yaml.safe_load(f) or {"relations": []}
            
            existing_sources = [r.get("source") for r in data["relations"]]
            
            for rel in new_relations:
                if rel.get("source") not in existing_sources:
                    data["relations"].append(rel)
            
            with open(self.relation_path, "w") as f:
                yaml.dump(data, f)
            
            logger.info(f"Added new relations: {new_relations}")
        except Exception as e:
            logger.error(f"Failed to add relations: {e}")