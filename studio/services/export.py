# services/export.py
import json
import zipfile
import io
from typing import Dict, Any
from models.project_state import ProjectState

class ExportError(Exception):
    pass

def generate_export_package(project: ProjectState) -> bytes:
    """Generate a ZIP package containing project data."""
    try:
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            summary = {
                "channel": project.channel,
                "has_image": project.has_image(),
                "detector": project.detector_result,
                "gap": project.gap_result,
                "creative": project.creative_result,
                "final_prompt": project.final_prompt,
                "revisions": project.revisions,
                "research": project.research_links,
            }
            zf.writestr("project.json", json.dumps(summary, indent=2))
            if project.final_prompt:
                zf.writestr("prompt.txt", project.final_prompt)
        return buffer.getvalue()
    except Exception as e:
        raise ExportError(f"Failed to create export package: {e}")