# YOGANS BGM STUDIO v7.1 - AI Creative Studio (FINAL)
# Streamlit UI - Adobe Lightroom + VSCode Style
# Full refactor with modular architecture + VPOS Selector + Prompt Formula

import streamlit as st
import yaml
import datetime
from pathlib import Path

# --- Import from our modules ---
from config.constants import CHANNEL_NAMES, SUPPORTED_IMAGE_TYPES, DATA_DIR
from models import ImageSource, ProjectState
from models.detector_result import DetectorResult, GapResult, CreativePlan
from engine.input_normalizer import normalize_to_pil, NormalizationError
from engine.detector import get_detector
from engine.gap_analyzer import GapAnalyzer
from engine.creative_director import CreativeDirector
from engine.prompt_compiler import build_partial_prompt_vocabulary
from engine.agnes import agnes_respond, agnes_suggest
from engine.vpos_selector import TIME_MAP, MOOD_MAP, STYLE_MAP, get_vpos_filters, filter_vpos_by_user, get_user_mode
from engine.vpos_reference import get_reference
from engine.prompt_formula import compile_all_formulas
from engine.vpos_mapper import map_vpos_to_dna, get_channel_match
from services.download import download_image_from_url, get_youtube_thumbnail
from services.export import generate_export_package
from utils.exceptions import VPDError
from utils.logger import logger
from streamlit_paste_button import paste_image_button
import streamlit.components.v1 as components

# ---- Page config ----
st.set_page_config(
    page_title="YOGANS BGM STUDIO AI Creative Studio",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---- Load YAML data ----
@st.cache_data(ttl=300)
def load_dna():
    file_path = DATA_DIR / "channel_dna.yaml"
    with open(file_path, "r") as f:
        return yaml.safe_load(f)

@st.cache_data(ttl=300)
def load_knowledge():
    file_path = DATA_DIR / "knowledge_graph.yaml"
    with open(file_path, "r") as f:
        return yaml.safe_load(f)

@st.cache_data(ttl=300)
def load_bgm():
    try:
        file_path = DATA_DIR / "bgm_studio.yaml"
        with open(file_path, "r") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        return {}

@st.cache_data(ttl=300)
def load_vpos():
    try:
        world_path = DATA_DIR / "vpos_world.yaml"
        with open(world_path, "r") as f:
            worlds = yaml.safe_load(f)
        hero_path = DATA_DIR / "vpos_hero.yaml"
        with open(hero_path, "r") as f:
            heroes = yaml.safe_load(f)
        lighting_path = DATA_DIR / "vpos_lighting.yaml"
        with open(lighting_path, "r") as f:
            lightings = yaml.safe_load(f)
        material_path = DATA_DIR / "vpos_material.yaml"
        with open(material_path, "r") as f:
            materials = yaml.safe_load(f)
        return {
            "worlds": worlds,
            "heroes": heroes,
            "lightings": lightings,
            "materials": materials,
        }
    except FileNotFoundError:
        return {"worlds": [], "heroes": [], "lightings": [], "materials": []}

DNA = load_dna()
KNOWLEDGE = load_knowledge()
BGM = load_bgm()
VPOS = load_vpos()
CHANNEL_LIST = list(DNA.keys())

# ---- Session State ----
if 'project' not in st.session_state:
    st.session_state.project = ProjectState()
if 'agnes_chat_history' not in st.session_state:
    st.session_state.agnes_chat_history = []
if 'vpos_filters' not in st.session_state:
    st.session_state.vpos_filters = {}
if 'vpos_filtered' not in st.session_state:
    st.session_state.vpos_filtered = {}
if 'vpos_applied' not in st.session_state:
    st.session_state.vpos_applied = False
if 'selected_time' not in st.session_state:
    st.session_state.selected_time = "🌙 Malam"
if 'selected_mood' not in st.session_state:
    st.session_state.selected_mood = "📚 Riset"
if 'selected_style' not in st.session_state:
    st.session_state.selected_style = "📸 Standard 50mm"

project = st.session_state.project

# ---- Helper functions ----
def set_image_source(raw_input, source: str, filename: str = "untitled.png") -> bool:
    if raw_input is None:
        return False
    try:
        pil_img = normalize_to_pil(raw_input)
    except NormalizationError as e:
        st.error(f"❌ Gagal ngolah gambar: {e}")
        return False
    project.image_source = ImageSource(image=pil_img, source=source, filename=filename)
    project.clear_analysis()
    return True

def get_current_image():
    return project.image_source.image if project.image_source else None

# ---- Sidebar ----
with st.sidebar:
    st.image("https://placehold.co/200x60/1a1a1a/FFB800?text=YOGANS+BGM+STUDIO", use_container_width=True)
    st.markdown("---")
    
    # ---- Channel Selector ----
    selected_channel = st.selectbox(
        "🎯 Channel",
        CHANNEL_LIST,
        index=CHANNEL_LIST.index(project.channel) if project.channel in CHANNEL_LIST else 0
    )
    if selected_channel != project.channel:
        project.channel = selected_channel
        st.rerun()
    
    # ---- Agnes AI Assistant ----
    with st.expander("🤖 Agnes AI Assistant", expanded=False):
        agnes_input = st.text_input(
            "Tanya Agnes...",
            placeholder="saran, workflow, prompt...",
            key="agnes_sidebar"
        )
        if st.button("💬 Tanya", use_container_width=True):
            if agnes_input.strip():
                response = agnes_respond(agnes_input, project)
                st.session_state.agnes_chat_history.append({"user": agnes_input, "agnes": response})
                st.rerun()
        if st.session_state.agnes_chat_history:
            for chat in st.session_state.agnes_chat_history[-3:]:
                st.caption(f"🧑‍💻 {chat['user']}")
                st.info(f"🤖 {chat['agnes']}")
    
    st.markdown("---")
    menu = st.radio(
        "Navigasi",
        ["🏠 Home", "📂 Project", "🔍 Analyze", "🧬 DNA", "✍️ Prompt", "📊 Report"],
        index=0
    )
    st.caption(f"🔒 v7.1 | {datetime.date.today()}")

# ---- MAIN AREA ----
if menu == "🏠 Home":
    st.title("🎨 YOGANS BGM STUDIO")
    st.caption("AI Creative Studio — Visual Production Database")
    col1, col2, col3 = st.columns(3)
    col1.metric("📁 Projects", "12", "+3")
    col2.metric("✅ PASS Rate", "91%", "▲ 5%")
    col3.metric("🧠 Knowledge", "19", "Stabil")
    st.markdown("---")
    st.subheader("📂 Recent Projects")
    for p in [{"name":"Bamboo Hush","score":94,"status":"PASS"}, {"name":"Night Jazz","score":91,"status":"PASS"}, {"name":"Bossa Session","score":78,"status":"WARN"}]:
        a,b,c = st.columns([3,1,1])
        a.write(f"**{p['name']}**")
        b.write(f"Score: {p['score']}%")
        c.write(f"`{p['status']}`")

elif menu == "📂 Project":
    st.title("📂 Project Workspace")
    st.caption("INPUT HUB — Upload, Paste, URL, YouTube")
    col_input, col_preview = st.columns([1, 2])
    
    with col_input:
        st.subheader("📤 Input")
        tab_upload, tab_paste, tab_url, tab_youtube = st.tabs(["📁 Upload", "📋 Paste", "🔗 URL", "▶️ YouTube"])
        
        with tab_upload:
            uploaded = st.file_uploader("Pilih gambar", type=SUPPORTED_IMAGE_TYPES)
            if uploaded:
                if set_image_source(uploaded, "upload", uploaded.name):
                    st.success(f"✅ {uploaded.name}")
                    st.rerun()
        
        with tab_paste:
            st.caption("📋 **Pilihan 1:** Klik tombol di handap, teras **Ctrl+V** (atawa Cmd+V)")
            pasted = paste_image_button("📋 Klik di dieu, teras Ctrl+V")
            if pasted is not None:
                if set_image_source(pasted, "clipboard", "clipboard.png"):
                    st.success("✅ Gambar hasil paste (Ctrl+V)!")
                    st.rerun()
            
            st.markdown("---")
            st.caption("🖱️ **Pilihan 2:** Klik kotak di handap, teras **Ctrl+V** atanapi **klik kanan → Paste**")
            
            paste_text = st.text_area(
                label="",
                placeholder="Klik di dieu, teras Ctrl+V atanapi klik kanan → Paste",
                height=80,
                key="paste_area",
                label_visibility="collapsed"
            )
            
            components.html("""
            <script>
            (function() {
                const textArea = document.querySelector('textarea[data-testid="stTextArea"]');
                if (!textArea) return;
                
                textArea.addEventListener('paste', function(e) {
                    const items = e.clipboardData.items;
                    for (let item of items) {
                        if (item.type.startsWith('image/')) {
                            e.preventDefault();
                            const blob = item.getAsFile();
                            const reader = new FileReader();
                            reader.onload = function(event) {
                                const dataUrl = event.target.result;
                                const input = document.createElement('input');
                                input.type = 'hidden';
                                input.id = 'pasted_image_data';
                                input.value = dataUrl;
                                document.body.appendChild(input);
                                
                                const btns = document.querySelectorAll('button');
                                for (let btn of btns) {
                                    if (btn.innerText.includes('Proses Gambar dari Paste')) {
                                        btn.click();
                                        break;
                                    }
                                }
                            };
                            reader.readAsDataURL(blob);
                            break;
                        }
                    }
                });
            })();
            </script>
            """, height=0)
            
            if st.button("📥 Proses Gambar dari Paste", key="btn_process_paste", type="secondary"):
                st.info("📸 Gambar bakal diprosés otomatis saatos paste.")
                st.warning("⚠️ Kanggo ayeuna, paste Ctrl+V (Pilihan 1) langkung stabil.")
        
        with tab_url:
            img_url = st.text_input("", placeholder="https://example.com/image.jpg", label_visibility="collapsed")
            if st.button("📥 Download", use_container_width=True):
                if img_url:
                    with st.spinner("..."):
                        img = download_image_from_url(img_url)
                        if img and set_image_source(img, "url", img_url.split("/")[-1]):
                            st.success("✅ Downloaded!")
                            st.rerun()
        
        with tab_youtube:
            yt_url = st.text_input("", placeholder="youtube.com/watch?v=...", label_visibility="collapsed")
            if yt_url:
                thumb_url, vid = get_youtube_thumbnail(yt_url)
                if thumb_url:
                    st.image(thumb_url, use_container_width=True)
                    if st.button("🎬 Use Thumbnail", use_container_width=True):
                        img = download_image_from_url(thumb_url)
                        if img and set_image_source(img, "youtube", f"yt_{vid}.jpg"):
                            st.success("✅ Thumbnail set!")
                            st.rerun()
        
        if project.image_source:
            src = project.image_source
            st.markdown("---")
            st.success(f"🖼️ {src.filename} ({src.width}×{src.height})")
            if st.button("🧹 Clear", use_container_width=True):
                project.clear_all()
                st.rerun()
    
    with col_preview:
        st.subheader("🖼️ Preview")
        img = get_current_image()
        if img:
            st.image(img, use_container_width=True)
            st.caption(f"🔮 {project.channel}")
        else:
            st.info("📤 Upload, paste, atau masukkan URL")

elif menu == "🔍 Analyze":
    st.title("🔍 Analyze & AI Creative Director")
    
    # ---- VPOS Selector ----
    with st.expander("🎯 VPOS Selector — Pilih Waktu, Suasana, Style", expanded=True):
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.session_state.selected_time = st.selectbox("🌅 Waktu", list(TIME_MAP.keys()), index=list(TIME_MAP.keys()).index(st.session_state.selected_time))
        with col_b:
            st.session_state.selected_mood = st.selectbox("🎭 Suasana", list(MOOD_MAP.keys()), index=list(MOOD_MAP.keys()).index(st.session_state.selected_mood))
        with col_c:
            st.session_state.selected_style = st.selectbox("📸 Style", list(STYLE_MAP.keys()), index=list(STYLE_MAP.keys()).index(st.session_state.selected_style))
        
        mood_mode = get_user_mode(st.session_state.selected_mood)
        if mood_mode == "reference":
            st.info("📚 **Mode: Riset** — Tampilkeun inspirasi channel lain")
            references = get_reference(st.session_state.selected_mood)
            if references:
                for ref in references:
                    st.caption(f"🎬 **{ref['name']}** ({ref['subs']}) — {ref['style']}")
        else:
            if st.button("🚀 Apply VPOS Filters", type="primary"):
                filters = get_vpos_filters(st.session_state.selected_time, st.session_state.selected_mood, st.session_state.selected_style)
                st.session_state.vpos_filters = filters
                st.session_state.vpos_filtered = filter_vpos_by_user(VPOS, filters)
                st.session_state.vpos_applied = True
                st.success(f"✅ Filters applied: {filters}")
                st.rerun()
    
    img = get_current_image()
    if img is None:
        st.warning("📤 Input gambar heula di Project.")
    else:
        if st.button("⚡ Analyze Image", type="primary", use_container_width=True):
            with st.spinner("AI Reading Image..."):
                try:
                    from engine.workflow.pipeline import Pipeline
                    pipeline = Pipeline()
                    
                    result = pipeline.run(
                        image=img,
                        project=project,
                        dna=DNA
                    )
                    
                    # Simpen hasil tambahan
                    project.matched_scene = result.get("scene")
                    project.extracted_attributes = result.get("attributes")
                    project.suggested_attributes = result.get("suggested")
                    project.learned = result.get("learned")
                    project.variants = result.get("variants")
                    project.motion_plan = result.get("motion")
                    project.music_plan = result.get("music")
                    
                    st.success("✅ AI Analysis Complete!")
                    
                    scene = result.get("scene")
                    if scene:
                        st.info(f"🏠 **Scene Detected:** {scene.get('name')} (Score: {scene.get('score', 0)}%)")
                    
                    agnes_suggestion = agnes_suggest(project)
                    with st.expander("🤖 Agnes Saran"):
                        st.info(agnes_suggestion)
                        
                except VPDError as e:
                    st.error(f"❌ {e}")
        
        # ---- TAMPILKAN HASIL ----
        if project.detector_result:
            res = project.detector_result
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("📊 Detector Scores")
                st.bar_chart({
                    "Arsitektur": res.get("confidence", 0),
                    "Material": res.get("confidence", 0) * 0.95,
                    "Umur": res.get("confidence", 0) * 0.85,
                    "Cahaya": res.get("confidence", 0) * 0.90,
                    "Gerak": res.get("confidence", 0) * 0.80,
                })
                st.metric("Channel", res.get("channel", "-"))
                st.metric("Confidence", f"{res.get('confidence', 0)}%")
            
            with col2:
                st.subheader("🧠 Gap Analysis")
                if project.gap_result:
                    gap = project.gap_result
                    for k, items in [("✅ Match", gap.get("match", [])), ("❌ Missing", gap.get("missing", [])), ("⚠️ Conflict", gap.get("conflict", []))]:
                        if items:
                            st.markdown(f"**{k}**")
                            for item in items:
                                st.caption(f"• {item.get('element', '-')}")
                if project.creative_result:
                    st.markdown("---")
                    st.subheader("💡 Creative Plan")
                    cr = project.creative_result
                    for rec in cr.get("recommendations", []):
                        st.caption(f"🔥 {rec}")
                    st.metric("Predicted Score", f"{cr.get('predicted_score', 0)}%")
                    if st.button("📋 Terapkan ke Prompt"):
                        st.success("Prompt siap di tab ✍️ Prompt")
            
            # --- DNA FUSION ---
            if hasattr(project, 'fused_result') and project.fused_result:
                st.markdown("---")
                st.subheader("🧬 DNA Fusion")
                fused = project.fused_result
                attrs = fused.get("fused_attributes", {})
                st.success(f"**{attrs.get('fusion_name', 'Fusion')}**")
                col_a, col_b = st.columns(2)
                with col_a:
                    st.caption(f"🏛️ Architecture: {attrs.get('architecture', '-')}")
                    st.caption(f"💡 Lighting: {attrs.get('lighting', '-')}")
                    st.caption(f"📷 Camera: {attrs.get('camera', '-')}")
                with col_b:
                    st.caption(f"🎨 Materials: {', '.join(attrs.get('material', []))}")
                    st.caption(f"🎭 Mood: {', '.join(attrs.get('mood', []))}")
                    st.caption(f"✨ FX: {', '.join(attrs.get('fx', []))}")
            
            # --- Scene & Variants ---
            if project.matched_scene:
                st.markdown("---")
                st.subheader("🏠 Scene Detection")
                scene = project.matched_scene
                st.info(f"**Scene:** {scene.get('name')} (Score: {scene.get('score', 0)}%)")
            
            if hasattr(project, 'variants') and project.variants:
                st.markdown("---")
                st.subheader("🎨 Creative Variants")
                cols = st.columns(3)
                for i, var in enumerate(project.variants[:3]):
                    with cols[i]:
                        st.caption(f"**{var.get('version', 'Variant')}**")
                        st.caption(var.get('description', '')[:60])
            
            if hasattr(project, 'motion_plan') and project.motion_plan:
                st.markdown("---")
                st.subheader("🎬 Motion Plan")
                motion = project.motion_plan
                st.caption(f"**Primary:** {motion.get('primary', '—')}")
                st.caption(f"**Camera:** {motion.get('camera', '—')}")
            
            if hasattr(project, 'music_plan') and project.music_plan:
                st.markdown("---")
                st.subheader("🎵 Music Suggestion")
                music = project.music_plan
                st.caption(f"**Genre:** {music.get('genre', '—')}")
                st.caption(f"**Mood:** {music.get('mood', '—')}")
            
            # --- Knowledge Learned ---
            if hasattr(project, 'learned') and project.learned:
                st.markdown("---")
                st.subheader("🧠 Knowledge Learned")
                learned = project.learned
                new_vocab = learned.get('new_vocabulary', [])
                if new_vocab:
                    st.caption(f"**New Vocabulary:** {', '.join(new_vocab)}")
                new_relations = learned.get('new_relations', [])
                if new_relations:
                    st.caption(f"**New Relations:** {len(new_relations)} added")
                st.caption(f"**Confidence:** {learned.get('confidence', 0)}%")

elif menu == "🧬 DNA":
    st.title("🧬 Visual DNA Card")
    
    # --- Prompt Asli (Gemini) ---
    if project.gap_result and project.gap_result.get('raw'):
        raw = project.gap_result['raw']
        raw_prompt = raw.get('raw_prompt', '')
        description = raw.get('description', '')
        suggestion = raw.get('suggestion', '')
        if raw_prompt:
            st.subheader("🖼️ Prompt Asli (Hasil Deteksi)")
            st.code(raw_prompt, language="text")
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown("**📖 Deskripsi:**")
                st.info(description if description else "—")
            with col_b:
                st.markdown("**💡 Saran:**")
                st.success(suggestion if suggestion else "—")
            st.markdown("---")
    
    # --- DNA Channel ---
    selected = st.selectbox("Pilih Channel", CHANNEL_LIST, index=CHANNEL_LIST.index(project.channel))
    if selected != project.channel:
        project.channel = selected
        st.rerun()
    dna = DNA[selected]
    
    st.subheader("📝 Prompt Awal (DNA Default)")
    initial_prompt = f"A cinematic {dna.get('architecture', '')} with {', '.join(dna.get('hero', [])[:2])}, {dna.get('mood', [''])[0]} atmosphere, {dna.get('lighting', '')} lighting, {', '.join(dna.get('palette', [])[:2])} palette"
    st.code(initial_prompt, language="text")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("World", selected)
        st.metric("Architecture", dna.get("architecture", "-"))
        st.metric("Era", dna.get("era", "-"))
        st.metric("Lighting", dna.get("lighting", "-"))
        st.metric("Camera", dna.get("camera", "-"))
    with col2:
        st.subheader("Hero"); st.write(", ".join(dna.get("hero", [])))
        st.subheader("Mood"); st.write(", ".join(dna.get("mood", [])))
        st.subheader("Palette"); st.write(", ".join(dna.get("palette", [])))
        st.subheader("Material"); st.write(", ".join(dna.get("material", [])))
        st.subheader("FX"); st.write(", ".join(dna.get("fx", [])))
    
    # --- VPOS Filtered Results ---
    if st.session_state.vpos_applied and st.session_state.vpos_filtered:
        st.markdown("---")
        st.subheader("🎯 VPOS Filtered Results")
        for category, items in st.session_state.vpos_filtered.items():
            if items:
                st.markdown(f"**{category.upper()}**")
                for item in items[:3]:
                    name = item.get('name') or item.get('role') or item.get('style') or '-'
                    st.caption(f"• {name}")
    
    # --- Prompt Final ---
    if project.final_prompt:
        st.markdown("---")
        st.subheader("🎯 Prompt Final")
        st.code(project.final_prompt, language="text")

elif menu == "✍️ Prompt":
    st.title("✍️ Prompt Compiler")
    
    # --- Agnes Asisten ---
    with st.expander("🤖 Agnes — Asisten Prompt", expanded=False):
        agnes_prompt = st.text_input("Tanya Agnes...", placeholder="kumaha ngahususkeun prompt?", key="agnes_prompt")
        if agnes_prompt:
            response = agnes_respond(agnes_prompt, project)
            st.info(f"🤖 {response}")
    
    channel = project.channel
    dna = DNA[channel]
    bgm = BGM.get(channel, {})
    
    # --- 4 Formula Prompt ---
    st.subheader("🎯 Prompt Formulas")
    
    # Build data for formulas
    formula_data = {
        "subject": ", ".join(dna.get("hero", ["artist"])),
        "setting": dna.get("architecture", "room"),
        "action": dna.get("motion", ["performing"])[0] if dna.get("motion") else "performing",
        "style": dna.get("mood", ["cinematic"])[0],
        "lighting": dna.get("lighting", "natural"),
        "palette": ", ".join(dna.get("palette", ["neutral"])),
        "foreground": ", ".join(dna.get("fx", ["details"])),
        "background": dna.get("atmosphere", "ambient"),
        "cinematography": "cinematic shot",
        "movement": dna.get("motion", ["gentle movement"])[0] if dna.get("motion") else "gentle movement",
        "camera": "50mm f/1.8, 24fps",
        "ratio": "16:9",
        "stylize": 50,
        "chaos": 10,
        "weird": 5
    }
    
    formulas = compile_all_formulas(dna, project.detector_result or {}, st.session_state.vpos_filters, formula_data)
    
    tab_g, tab_l, tab_m, tab_d = st.tabs(["Google", "Luma", "Midjourney", "DeepSeek"])
    
    with tab_g:
        st.caption("Formula: [Cinematography] + [Subject] + [Action] + [Setting] + [Style]")
        st.code(formulas.get("google", ""), language="text")
        st.download_button("📋 Copy", formulas.get("google", ""), file_name="prompt_google.txt")
    
    with tab_l:
        st.caption("Formula: [Subject] + [Setting] + [Movement] + [Camera]")
        st.code(formulas.get("luma", ""), language="text")
        st.download_button("📋 Copy", formulas.get("luma", ""), file_name="prompt_luma.txt")
    
    with tab_m:
        st.caption("Formula: [Subject] + [Style] + [Lighting] + Parameters")
        st.code(formulas.get("midjourney", ""), language="text")
        st.download_button("📋 Copy", formulas.get("midjourney", ""), file_name="prompt_midjourney.txt")
    
    with tab_d:
        st.caption("Formula: [Subject] + [Foreground] + [Background] + [Palette]")
        st.code(formulas.get("deepseek", ""), language="text")
        st.download_button("📋 Copy", formulas.get("deepseek", ""), file_name="prompt_deepseek.txt")
    
    st.markdown("---")
    
    # --- BGM Studio ---
    with st.expander("🎵 BGM Studio", expanded=False):
        if bgm:
            st.markdown(f"**Style:** {bgm.get('bgm_style', '-')}")
            st.markdown(f"**Instruments:** {', '.join(bgm.get('instruments', []))}")
            st.markdown(f"**Mood:** {', '.join(bgm.get('mood_tags', []))}")
            st.code(bgm.get('prompt_suno', ''), language="text")
        else:
            st.warning("BGM data teu aya.")
    
    # --- Partial Prompt ---
    st.subheader("🧩 Partial Prompt (Vocabulary)")
    partial = build_partial_prompt_vocabulary(dna, project.gap_result or {})
    st.code(partial, language="text")
    st.download_button("📋 Copy Partial", partial, file_name="partial_prompt.txt")

elif menu == "📊 Report":
    st.title("📊 Report Generator")
    tab_r1, tab_r2, tab_r3 = st.tabs(["📋 Project Report", "📈 Weekly Report", "⭐ Final Report"])
    
    with tab_r1:
        st.subheader("📋 Project Report")
        if project.image_source and project.detector_result:
            st.markdown(f"""
            **Channel:** {project.channel}
            **Image:** {project.image_source.filename} ({project.image_source.width}×{project.image_source.height})
            **Confidence:** {project.detector_result.get('confidence', 0)}%
            **Prompt:** {project.final_prompt or 'Belum aya'}
            """)
            if st.button("Export PDF"):
                st.info("Fungsi PDF bakal aktip saatos ReportLab diintegrasikeun.")
        else:
            st.info("Jalanan Detector heula.")
    
    with tab_r2:
        st.metric("Projects This Week", "5")
        st.metric("Average Score", "89%")
        st.bar_chart({"Jazz": 3, "Bossa": 2, "Forest": 1})
    
    with tab_r3:
        st.success("⭐ Final Knowledge Report")
        if project.gap_result:
            st.json(project.gap_result)
        else:
            st.info("Belum aya data.")

# ---- Footer ----
st.sidebar.markdown("---")
st.sidebar.caption("🎨 YOGANS BGM STUDIO v7.1")