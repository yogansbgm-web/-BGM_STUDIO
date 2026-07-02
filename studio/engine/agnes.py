# engine/agnes.py
from models.project_state import ProjectState

def agnes_respond(user_input: str, project: ProjectState) -> str:
    user_lower = user_input.lower()
    
    if any(word in user_lower for word in ["saran", "rekomendasi", "kumaha"]):
        if project.gap_result:
            missing = project.gap_result.get('missing', [])
            if missing:
                items = ', '.join([m['element'] for m in missing])
                return f"💡 Saran: Tambah {items}. Skor diprediksi naek."
            return "✅ Gambar geus optimal!"
        return "📤 Upload gambar heula."
    
    elif "prompt" in user_lower:
        return f"📝 Prompt: {project.final_prompt or 'Belum aya'}"
    
    else:
        return "👋 Halo! Kuring Agnes. Coba tanya: saran, workflow, prompt."

def agnes_suggest(project: ProjectState) -> str:
    if project.gap_result:
        missing = project.gap_result.get('missing', [])
        if missing:
            items = ', '.join([m['element'] for m in missing])
            return f"💡 Saran: Tambah {items}."
    return "✅ Gambar geus optimal."