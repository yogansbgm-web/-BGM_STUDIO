# engine/workflow/pipeline.py
from typing import Dict, Any
from PIL import Image
from models.project_state import ProjectState
from engine.detector import get_detector
from engine.vision.extractor import AttributeExtractor
from engine.knowledge.matcher import SceneMatcher
from engine.knowledge.semantic_graph import SemanticGraph
from engine.knowledge.learner import KnowledgeLearner
from engine.generation.variant_generator import VariantGenerator
from engine.generation.motion_planner import MotionPlanner
from engine.generation.music_mapper import MusicMapper
from engine.creative_director import CreativeDirector
from engine.gap_analyzer import GapAnalyzer
from config.constants import DNA
from utils.logger import logger
from utils.exceptions import VPDError

class Pipeline:
    """Orchestrate the entire AI workflow."""

    def __init__(self):
        self.detector = get_detector()
        self.extractor = AttributeExtractor()
        self.graph = SemanticGraph()
        self.learner = KnowledgeLearner()
        self.matcher = SceneMatcher()
        self.variant_generator = VariantGenerator()
        self.motion_planner = MotionPlanner()
        self.music_mapper = MusicMapper()
        self.gap_analyzer = GapAnalyzer()
        self.creative_director = CreativeDirector()

    def run(self, image: Image.Image, project: ProjectState, dna: Dict) -> Dict[str, Any]:
        """Execute full workflow."""
        try:
            logger.info("Starting AI workflow pipeline...")

            # 1. DETECTOR
            logger.info("  → Running Vision Detector...")
            det_result = self.detector.detect(image)
            project.detector_result = det_result.to_dict()

            # 2. ATTRIBUTE EXTRACTOR
            logger.info("  → Extracting attributes...")
            attributes = self.extractor.extract(det_result)

            # 3. SCENE MATCHER
            logger.info("  → Matching scene...")
            matched_scene = self.matcher.match(attributes, project.channel)
            if matched_scene:
                project.matched_scene = matched_scene
                logger.info(f"  → Matched Scene: {matched_scene.get('name')}")

            # 4. SUGGEST ATTRIBUTES
            scene_name = matched_scene.get("name", "General") if matched_scene else "General"
            suggested = self.graph.suggest_attributes(scene_name, project.channel)
            attributes["suggested"] = suggested

            # 5. GAP ANALYSIS
            logger.info("  → Running Gap Analysis...")
            dna_channel = dna.get(project.channel, {})
            gap_result = self.gap_analyzer.analyze(det_result, dna_channel)
            project.gap_result = gap_result.to_dict()

            # 6. CREATIVE DIRECTOR
            logger.info("  → Generating creative plan...")
            creative_plan = self.creative_director.generate(gap_result.to_dict(), dna_channel)
            project.creative_result = creative_plan.to_dict()
            project.final_prompt = creative_plan.final_prompt

            # 7. VARIANT GENERATOR
            logger.info("  → Generating variants...")
            variants = self.variant_generator.generate(matched_scene or {}, attributes, project.channel)
            project.variants = variants

            # 8. MOTION PLANNER
            logger.info("  → Planning motion...")
            motion = self.motion_planner.plan(matched_scene or {}, project.channel)
            project.motion_plan = motion

            # 9. MUSIC MAPPER
            logger.info("  → Mapping music...")
            music = self.music_mapper.map(matched_scene or {}, project.channel)
            project.music_plan = music

            # 10. KNOWLEDGE LEARN
            logger.info("  → Updating knowledge database...")
            learned = self.learner.learn_from_project(
                project.to_dict(),
                attributes
            )
            project.learned = learned

            logger.info("✅ Pipeline completed successfully.")

            return {
                "scene": matched_scene,
                "attributes": attributes,
                "suggested": suggested,
                "gap": gap_result,
                "creative": creative_plan,
                "variants": variants,
                "motion": motion,
                "music": music,
                "learned": learned,
                "final_prompt": creative_plan.final_prompt,
            }

        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            raise VPDError(f"AI Workflow failed: {e}")