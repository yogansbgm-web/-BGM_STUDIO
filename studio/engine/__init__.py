# engine/__init__.py
from .input_normalizer import normalize_to_pil, NormalizationError
from .detector import get_detector, BaseDetector, MockDetector, SmartMockDetector, VisionDetector
from .gap_analyzer import GapAnalyzer
from .creative_director import CreativeDirector
from .prompt_compiler import PromptAdapter, MidjourneyAdapter, SDXLAdapter, FluxAdapter, KlingAdapter, RunwayAdapter, build_partial_prompt_vocabulary
from .prompt_formula import PromptFormula, compile_all_formulas, FORMULA_STRUCTURE
from .vpos_selector import TIME_MAP, MOOD_MAP, STYLE_MAP, get_vpos_filters, filter_vpos_by_user, get_user_mode
from .vpos_mapper import map_vpos_to_dna, get_channel_match
from .vpos_reference import get_reference, REFERENCE_CHANNELS
from .agnes import agnes_respond, agnes_suggest

__all__ = [
    "normalize_to_pil",
    "NormalizationError",
    "get_detector",
    "BaseDetector",
    "MockDetector",
    "SmartMockDetector",
    "VisionDetector",
    "GapAnalyzer",
    "CreativeDirector",
    "PromptAdapter",
    "MidjourneyAdapter",
    "SDXLAdapter",
    "FluxAdapter",
    "KlingAdapter",
    "RunwayAdapter",
    "build_partial_prompt_vocabulary",
    "PromptFormula",
    "compile_all_formulas",
    "FORMULA_STRUCTURE",
    "TIME_MAP",
    "MOOD_MAP",
    "STYLE_MAP",
    "get_vpos_filters",
    "filter_vpos_by_user",
    "get_user_mode",
    "map_vpos_to_dna",
    "get_channel_match",
    "get_reference",
    "REFERENCE_CHANNELS",
    "agnes_respond",
    "agnes_suggest",
]