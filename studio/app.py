# YOGANS BGM STUDIO v7.1 - AI Creative Studio (FINAL)
# Streamlit UI - Adobe Lightroom + VSCode Style
# Full refactor with modular architecture

import streamlit as st
import yaml
import datetime
from pathlib import Path

# --- Import from our modules (absolute imports) ---
from config.constants import CHANNEL_NAMES, SUPPORTED_IMAGE_TYPES, DATA_DIR
from models import ImageSource, ProjectState
from models.detector_result import DetectorResult, GapResult, CreativePlan
from engine.input_normalizer import normalize_to_pil, NormalizationError
from engine.detector import get_detector
from engine.gap_analyzer import GapAnalyzer
from engine.creative_director import CreativeDirector
from engine.prompt_compiler import MidjourneyAdapter
from services.download import download_image_from_url, get_youtube_thumbnail
from services.export import generate_export_package
from utils.exceptions import VPDError
from utils.logger import logger
from streamlit_paste_button import paste_image_button

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

DNA = load_dna()
KNOWLEDGE = load_knowledge()
BGM = load_bgm()
CHANNEL_LIST = list(DNA.keys())

# ---- Session State (single ProjectState) ----
if 'project' not in st.session_state:
    st.session_state.project = ProjectState()

project = st.session_state.project

# ---- Helper functions ----
def set_image_source(raw_input, source: str, filename: str = "untitled.png") -> bool:
    """Unified setter using the normalizer."""
    if raw_input is None:
        return False
    try:
        pil_img = normalize_to_pil(raw_input)
    except NormalizationError as e:
        st.error(f"❌ Gagal ngolah gambar: {e}")
        return False
    project.image_source = ImageSource(
        image=pil_img,
        source=source,
        filename=filename
    )
    project.clear_analysis()
    return True

def get_current_image():
    return project.image_source.image if project.image_source else None

# ---- Sidebar ----
with st.sidebar:
    st.image("https://placehold.co/200x60/1a1a1a/FFB800?text=YOGANS+BGM+STUDIO", use_column_width=True)
    st.markdown("---")
    menu = st.radio(
        "Navigasi",
        ["🏠 Home", "📂 Project", "🔍 Detector", "🧬 Visual DNA", "✍️ Prompt", "📄 Report", "🧠 Knowledge", "📦 Export"],
        index=0
    )
    st.markdown("---")
    st.caption(f"🔒 FROZEN v7.1 | {datetime.date.today()}")

st.markdown("---")

# ---- MAIN AREA ----
if menu == "🏠 Home":
    st.title("🎨 YOGANS BGM STUDIO AI Creative Studio")
    st.caption("Visual Production Database — FROZEN v7.1")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Projects", "12", "+3")
    col2.metric("PASS Rate", "91%", "▲ 5%")
    col3.metric("Knowledge Nodes", "19", "Stabil")
    st.subheader("📂 Recent Projects")
    for p in [{"name":"Bamboo Hush","score":94,"status":"PASS"}, {"name":"Night Jazz","score":91,"status":"PASS"}, {"name":"Bossa Session","score":78,"status":"WARN"}]:
        a,b,c = st.columns([3,1,1])
        a.write(f"**{p['name']}**")
        b.write(f"Score: {p['score']}%")
        c.write(f"`{p['status']}`")

elif menu == "📂 Project":
    st.title("📂 Project Workspace")
    st.caption("INPUT HUB — Unified input pipeline")
    col_input, col_preview = st.columns([1, 2])

    with col_input:
        st.subheader("📤 Input Hub")
        tab_upload, tab_paste, tab_url, tab_youtube, tab_riset = st.tabs(
            ["📁 Upload", "📋 Paste", "🔗 URL", "▶️ YouTube", "📚 Riset"]
        )

        with tab_upload:
            uploaded = st.file_uploader("Pilih gambar", type=SUPPORTED_IMAGE_TYPES)
            if uploaded:
                if set_image_source(uploaded, "upload", uploaded.name):
                    st.success(f"✅ Gambar siap: {uploaded.name}")
                    st.rerun()

                with tab_paste:
            st.caption("📋 **Pilihan 1:** Klik tombol di handap, teras **Ctrl+V** (atawa Cmd+V)")
            
            # Tombol Paste (Ctrl+V) — tetep aya
            pasted = paste_image_button("📋 Klik di dieu, teras Ctrl+V")
            if pasted is not None:
                if set_image_source(pasted, "clipboard", "clipboard.png"):
                    st.success("✅ Gambar hasil paste (Ctrl+V)!")
                    st.rerun()
            
            st.markdown("---")
            
            st.caption("🖱️ **Pilihan 2:** Klik kotak di handap, teras **klik kanan → Paste**")
            st.caption("(Atanapi anjeun tiasa langsung **Ctrl+V** dina kotak ieu ogé)")
            
            # Text area pikeun nangkep paste (inklusi klik kanan)
            paste_text_area = st.text_area(
                label="",
                placeholder="Klik di dieu, teras klik kanan → Paste (atanapi Ctrl+V)",
                height=80,
                key="paste_area",
                label_visibility="collapsed"
            )
            
            # Cek lamun aya gambar anu di-paste ka text area
            # (Kami henteu tiasa langsung nangkep gambar tina text_area,
            # tapi kami tiasa nambihan JavaScript pikeun nangkep event paste)
            
            # Tambahkeun JavaScript pikeun nangkep paste tina text_area
            import streamlit.components.v1 as components
            paste_js = """
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
                                // Kirim ka Streamlit via input hidden
                                const input = document.createElement('input');
                                input.type = 'hidden';
                                input.id = 'pasted_image_data';
                                input.value = dataUrl;
                                document.body.appendChild(input);
                                
                                // Pencet tombol submit otomatis
                                const btn = document.querySelector('button[data-testid="baseButton-secondary"]');
                                if (btn) {
                                    btn.click();
                                }
                            };
                            reader.readAsDataURL(blob);
                            break;
                        }
                    }
                });
            })();
            </script>
            """
            components.html(paste_js, height=0)
            
            # Tombol pikeun ngolah gambar hasil paste
            if st.button("📥 Proses Gambar dari Paste", key="btn_process_paste", type="secondary"):
                # Cek lamun aya data gambar disimpen
                # (Ieu bakal di-trigger ku JavaScript otomatis)
                st.info("Gambar bakal diprosés otomatis saatos paste.")

        with tab_url:
            img_url = st.text_input("🔗 URL Gambar", placeholder="https://example.com/image.jpg")
            if st.button("📥 Download & Analisis"):
                if img_url:
                    with st.spinner("Ngundeur gambar..."):
                        img = download_image_from_url(img_url)
                        if img and set_image_source(img, "url", img_url.split("/")[-1]):
                            st.success("✅ Gambar hasil download!")
                            st.rerun()
                else:
                    st.warning("Masukkan URL heula.")

        with tab_youtube:
            yt_url = st.text_input("▶️ URL YouTube", placeholder="https://www.youtube.com/watch?v=...")
            if yt_url:
                thumb_url, vid = get_youtube_thumbnail(yt_url)
                if thumb_url:
                    st.image(thumb_url, caption=f"Thumbnail: {vid}", use_column_width=True)
                    if st.button("🎬 Gunakeun Thumbnail"):
                        img = download_image_from_url(thumb_url)
                        if img and set_image_source(img, "youtube", f"yt_{vid}.jpg"):
                            st.success("✅ Thumbnail dipaké!")
                            st.rerun()
                else:
                    st.warning("Teu bisa ménta thumbnail.")

        with tab_riset:
            research_url = st.text_input("🔗 URL Riset", placeholder="https://example.com/article")
            research_note = st.text_area("📝 Catatan", placeholder="Tulis catetan...")
            if st.button("💾 Simpan Riset"):
                if research_url or research_note:
                    project.research_links.append({
                        "url": research_url,
                        "note": research_note,
                        "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                    })
                    st.success("✅ Disimpen!")
            if project.research_links:
                st.markdown("---")
                st.subheader("📚 Daftar Riset")
                for i, item in enumerate(project.research_links):
                    with st.expander(f"📄 {item['date']}"):
                        st.markdown(f"**URL:** {item['url']}")
                        st.markdown(f"**Catatan:** {item['note']}")
                        if st.button(f"🗑️ Hapus {i+1}", key=f"del_{i}"):
                            project.research_links.pop(i)
                            st.rerun()

        # ---- Image info ----
        if project.image_source:
            src = project.image_source
            st.markdown("---")
            st.success(f"🖼️ **Aktif:** `{src.source}` — {src.filename} ({src.width}×{src.height})")
            if st.button("🧹 Clear Image"):
                project.clear_all()
                st.rerun()

        # ---- Revision history ----
        st.markdown("---")
        st.subheader("🔄 Revision History")
        if project.revisions:
            for rev in project.revisions:
                st.text(f"v{rev['id']}: {rev['score']}% - {rev['status']}")
        else:
            st.caption("Belum aya revisi.")

    with col_preview:
        st.subheader("🖼️ Preview")
        img = get_current_image()
        if img:
            st.image(img, use_column_width=True)
            st.info(f"🔮 Channel: **{project.channel}**")
        else:
            st.warning("📤 Upload, paste, URL, atanapi YouTube heula!")

elif menu == "🔍 Detector":
    st.title("🔍 Detector & AI Creative Director")
    img = get_current_image()
    if img is None:
        st.warning("📤 Input gambar heula di Project.")
    else:
        if st.button("⚡ Analyze Image", type="primary"):
            with st.spinner("Analyzing..."):
                try:
                    detector = get_detector()
                    det_result = detector.detect(img)
                    project.detector_result = det_result.to_dict()

                    gap_analyzer = GapAnalyzer()
                    dna_channel = DNA.get(project.channel, {})
                    gap_result = gap_analyzer.analyze(det_result, dna_channel)
                    project.gap_result = gap_result.to_dict()

                    director = CreativeDirector()
                    creative_plan = director.generate(gap_result, dna_channel)
                    project.creative_result = creative_plan.to_dict()
                    project.final_prompt = creative_plan.final_prompt

                    st.success("✅ Analysis Complete!")
                except VPDError as e:
                    st.error(f"❌ Analysis failed: {e}")
                    logger.error(f"Detector error: {e}")

        # Display results
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

elif menu == "🧬 Visual DNA":
    st.title("🧬 Visual DNA Card")
    selected = st.selectbox("Pilih Channel", CHANNEL_LIST, index=CHANNEL_LIST.index(project.channel))
    project.channel = selected
    dna = DNA[selected]
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

elif menu == "✍️ Prompt":
    st.title("✍️ Prompt Compiler")
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🖼️ IMAGE", "🎥 VIDEO", "🎵 MUSIC", "🚫 NEGATIVE", "🧩 PARTIAL"])
    channel = project.channel
    dna = DNA[channel]
    bgm = BGM.get(channel, {})

    with tab1:
        st.subheader("Midjourney Prompt")
        if project.final_prompt:
            prompt = project.final_prompt + " --ar 16:9 --style raw --s 50 --v 6.1"
            st.info("📌 Prompt Final ti Creative Director")
        else:
            prompt = f"A cinematic {dna.get('architecture', '')} with {', '.join(dna.get('hero', [])[:2])}, {dna.get('mood', [''])[0]} atmosphere, {dna.get('lighting', '')} lighting --ar 16:9 --style raw --s 50 --v 6.1"
        st.code(prompt, language="text")
        st.download_button("📋 Copy Image Prompt", prompt, file_name="prompt_image.txt")
        if st.button("🔄 Reset ka DNA Default"):
            project.final_prompt = ""
            st.rerun()

    with tab2:
        video_prompt = f"cinematic shot, {dna.get('architecture', '')}, {', '.join(dna.get('hero', []))}, 4s loop 24fps"
        st.code(video_prompt, language="text")

    with tab3:
        st.subheader("🎵 BGM Studio")
        if bgm:
            st.markdown(f"**Style:** {bgm.get('bgm_style', '-')}")
            st.markdown(f"**Instruments:** {', '.join(bgm.get('instruments', []))}")
            st.markdown(f"**Mood:** {', '.join(bgm.get('mood_tags', []))}")
            st.code(bgm.get('prompt_suno', ''), language="text")
        else:
            st.warning("BGM data teu aya.")

    with tab4:
        st.code("low quality, blurry, distorted, plastic, fake, ugly", language="text")

       with tab5:
        st.subheader("🧩 Partial Prompt (SDXL Positive / Vocabulary)")
        st.caption("Kosakata deskriptif — siap dipaké dina SDXL, ComfyUI, atanapi Midjourney Partial")
        
        from engine.prompt_compiler import build_partial_prompt_vocabulary
        
        # Bangun vocabulary
        partial = build_partial_prompt_vocabulary(
            dna=dna,
            gap_result=project.gap_result or {}
        )
        
        st.code(partial, language="text")
        st.download_button(
            "📋 Copy Partial Prompt",
            partial,
            file_name="partial_prompt.txt"
        )
elif menu == "📄 Report":
    st.title("📄 Report Generator")
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

elif menu == "🧠 Knowledge":
    st.title("🧠 Master Knowledge Database")
    st.subheader("📊 Statistik per Channel")
    cols = st.columns(3)
    for i, name in enumerate(CHANNEL_LIST):
        with cols[i % 3]:
            st.metric(name, f"Project: {i*10+5}", f"PASS: {i*8+3}")
    st.subheader("📈 Knowledge Growth")
    st.line_chart({"Week 1": 152, "Week 2": 181, "Week 3": 229, "Week 4": 284})
    with st.expander("🌳 Knowledge Graph (YAML)"):
        st.json(KNOWLEDGE)

elif menu == "📦 Export":
    st.title("📦 Export Project")
    st.caption("Ekspor sadaya data project.")
    if st.button("📥 Generate & Download ZIP", type="primary"):
        try:
            zip_data = generate_export_package(project)
            st.download_button(
                "⬇️ Download",
                zip_data,
                file_name=f"export_{project.channel}_{datetime.date.today()}.zip",
                mime="application/zip"
            )
        except Exception as e:
            st.error(f"Export gagal: {e}")

# ---- Footer ----
st.sidebar.markdown("---")
st.sidebar.caption("🎨 YOGANS BGM STUDIO v7.1 | Made with Streamlit")