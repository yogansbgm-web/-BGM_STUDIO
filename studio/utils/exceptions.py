# utils/exceptions.py
class VPDError(Exception):
    """Base exception for all VPD errors."""
    pass

class NormalizationError(VPDError):
    """Raised when input cannot be normalized to PIL.Image."""
    pass

class DetectorError(VPDError):
    """Raised when detector fails."""
    pass

class KnowledgeError(VPDError):
    """Raised when knowledge graph operations fail."""
    pass

class ExportError(VPDError):
    """Raised when export fails."""
    pass

class ConfigError(VPDError):
    """Raised when configuration is invalid."""
    pass