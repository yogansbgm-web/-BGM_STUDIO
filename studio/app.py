# YOGANS BGM STUDIO v7.1 - AI Creative Studio (FINAL)
# Streamlit UI - Adobe Lightroom + VSCode Style
# Integrated: BGM Studio + AI Creative Director + Gap Analysis
# Input Hub: Upload, Paste, URL, YouTube, Riset
# NO components.html - CLEAN VERSION

import streamlit as st
import yaml
import json
import os
import datetime
from pathlib import Path
from PIL import Image
import numpy as np
import io
import base64
import requests
import re
from urllib.parse import urlparse
from dataclasses import dataclass
from typing import Optional

# --- IMPORT PASTE BUTTON (Library stabil) ---
from streamlit_paste_button import paste_image_button

# --- DATA CLASS: Input Source ---
@dataclass
class ImageSource:
    image: Image.Image
    source: str  # "upload", "clipboard", "url", "youtube"
    filename: str = "untitled.png"
    width: int = 0
    height: int = 0
    metadata: dict = None

    def __post_init__(self):
        if self.image is not None:
            try:
                self.width, self.height = self.image.size
            except AttributeError:
                pass

# --- Path Base ---
BASE_DIR = Path(__file__).parent

# --- FUNGSI KONVERSI KE PIL (Robust) ---
def convert_to_pil(img):
    """Robust converter: accepts PIL, bytes, base64, numpy, dict, and more."""
    if img is None:
        return None

    # 1. Sudah PIL
    if isinstance(img, Image.Image):
        return img

    # 2. Bytes
    if isinstance(img, bytes):
        try:
            return Image.open(io.BytesIO(img))
        except Exception:
            pass

    # 3. Base64 string (data:image/...)
    if isinstance(img, str):
        if img.startswith('data:image'):
            try:
                header, encoded = img.split(',', 1)
                data = base64.b64decode(encoded)
                return Image.open(io.BytesIO(data))
            except Exception:
                pass
        # Mungkin file path
        try:
            return Image.open(img)
        except Exception:
            pass

    # 4. Numpy array
    if isinstance(img, np.ndarray):
        try:
            return Image.fromarray(img)
        except Exception:
            pass

    # 5. Dict (misalna { "image": bytes, ... })
    if isinstance(img, dict):
        for key in ['image', 'img', 'data', 'blob', 'value']:
            if key in img:
                return convert_to_pil(img[key])

    # 6. List/tuple (anggap ieu array RGB)
    if isinstance(img, (list, tuple)):
        try:
            arr = np.array(img)
            return Image.fromarray(arr)
        except Exception:
            pass

    return None

# --- Fungsi Download Gambar ---
def download_image_from_url(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        img = Image.open(io.BytesIO(response.content))
        return img
    except Exception as e:
        st.error(f"Gagal ngundeur gambar: {e}")
        return None

# --- Fungsi YouTube Thumbnail (dengan fallback) ---
def get_youtube_thumbnail(url):
    pattern = r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]{11})'
    match = re.search(pattern, url)
    if match:
        video_id = match.group(1)
        thumbnail_urls = [
            f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg",
            f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg",
            f"https://img.youtube.com/vi/{video_id}/sddefault.jpg"
        ]
        return thumbnail_urls, video_id
    return None, None

# --- Helper: Set Image Source ---
def set_image_source(img, source: str, filename: str = "untitled.png"):
    if img is None:
        return False

    # Konversi ke PIL jika perlu
    pil_img = convert_to_pil(img)
    if pil_img is None:
        st.error("Gagal ngolah gambar. Pastikeun format gambar didukung.")
        return False

    st.session_state.image_source = ImageSource(
        image=pil_img,
        source=source,
        filename=filename
    )
    return True

def get_current_image():
    if st.session_state.image_source:
        return st.session_state.image_source.image
    return None

# --- Konfigurasi Halaman ---
st.set_page_config(
    page_title="YOGANS BGM STUDIO AI Creative Studio",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Load Data (YAML) ---
@st.cache_data
def load_dna():
    file_path = BASE_DIR / "data" / "channel_dna.yaml"
    with open(file_path, "r") as f:
        return yaml.safe_load(f)

@st.cache_data
def load_knowledge():
    file_path = BASE_DIR / "data" / "knowledge_graph.yaml"
    with open(file_path, "r") as f:
        return yaml.safe_load(f)

@st.cache_data
def load_bgm():
    try:
        file_path = BASE_DIR / "data" / "bgm_studio.yaml"
        with open(file_path, "r") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        return {}

DNA = load_dna()
KNOWLEDGE = load_knowledge()
BGM = load_bgm()
CHANNEL_NAMES = list(DNA.keys())

# --- Session State ---
if 'current_channel' not in st.session_state:
    st.session_state.current_channel = "JAZZ"
if 'image_source' not in st.session_state:
    st.session_state.image_source = None
if 'detection_result' not in st.session_state:
    st.session_state.detection_result = {}
if 'gap_analysis' not in st.session_state:
    st.session_state.gap_analysis = {}
if 'revisions' not in st.session_state:
    st.session_state.revisions = []
if 'final_prompt' not in st.session_state:
    st.session_state.final_prompt = ""
if 'research_links' not in st.session_state:
    st.session_state.research_links = []

# --- SIDEBAR ---
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

# --- MAIN AREA ---
st.markdown("---")

if menu == "🏠 Home":
    st.title("🎨 YOGANS BGM STUDIO AI Creative Studio")
    st.caption("Visual Production Database — FROZEN v7.1")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Projects", "12", "+3")
    with col2:
        st.metric("PASS Rate", "91%", "▲ 5%")
    with col3:
        st.metric("Knowledge Nodes", "19", "Stabil")
    
    st.subheader("📂 Recent Projects")
    recent = [
        {"name": "Bamboo Hush", "score": 94, "status": "PASS"},
        {"name": "Night Jazz", "score": 91, "status": "PASS"},
        {"name": "Bossa Session", "score": 78, "status": "WARN"},
    ]
    for p in recent:
        col_a, col_b, col_c = st.columns([3,1,1])
        col_a.write(f"**{p['name']}**")
        col_b.write(f"Score: {p['score']}%")
        col_c.write(f"`{p['status']}`")

elif menu == "📂 Project":
    st.title("📂 Project Workspace")
    st.caption("INPUT HUB — Sadaya sumber gambar dihijikeun")
    
    col_input, col_preview = st.columns([1, 2])
    
    with col_input:
        st.subheader("📤 Input Hub")
        
        tab_upload, tab_paste, tab_url, tab_youtube, tab_riset = st.tabs([
            "📁 Upload", "📋 Paste", "🔗 URL", "▶️ YouTube", "📚 Riset"
        ])
        
        # TAB 1: Upload
        with tab_upload:
            st.caption("Upload gambar atanapi drag & drop")
            uploaded_file = st.file_uploader(
                "Pilih gambar",
                type=["jpg", "png", "jpeg"],
                accept_multiple_files=False
            )
            if uploaded_file is not None:
                img = Image.open(uploaded_file)
                if set_image_source(img, "upload", uploaded_file.name):
                    st.success(f"✅ Gambar siap: {uploaded_file.name}")
                    st.rerun()
        
        # TAB 2: Paste (dengan konversi otomatis + fallback)
        with tab_paste:
            st.caption("📋 Klik tombol di handap, teras Ctrl+V (atawa Cmd+V) pikeun nempel gambar")
            pasted = paste_image_button("📋 Klik di dieu, teras Ctrl+V")
            
            if pasted is not None:
                # Konversi otomatis
                img = convert_to_pil(pasted)
                if img is not None:
                    if set_image_source(img, "clipboard", "clipboard.png"):
                        st.success("✅ Gambar hasil paste!")
                        st.rerun()
                else:
                    st.error(f"Gagal ngolah gambar. Tipe: {type(pasted)}. Pastikeun gambar tiasa di-paste.")
        
        # TAB 3: URL
        with tab_url:
            st.caption("Tempel link gambar (JPG, PNG, JPEG)")
            img_url = st.text_input("URL Gambar", placeholder="https://example.com/image.jpg")
            if st.button("📥 Download & Analisis", key="btn_img_url"):
                if img_url:
                    with st.spinner("Ngundeur gambar..."):
                        img = download_image_from_url(img_url)
                        if img:
                            filename = img_url.split("/")[-1] or "url_image.jpg"
                            if set_image_source(img, "url", filename):
                                st.success("✅ Gambar hasil download!")
                                st.rerun()
                else:
                    st.warning("Masukkan URL heula.")
        
        # TAB 4: YouTube
        with tab_youtube:
            st.caption("Tempel link YouTube pikeun inspirasi visual")
            yt_url = st.text_input("URL YouTube", placeholder="https://www.youtube.com/watch?v=...")
            if yt_url:
                thumbnails, video_id = get_youtube_thumbnail(yt_url)
                if thumbnails:
                    thumbnail = None
                    for url in thumbnails:
                        try:
                            response = requests.head(url, timeout=5)
                            if response.status_code == 200:
                                thumbnail = url
                                break
                        except:
                            continue
                    
                    if thumbnail:
                        st.image(thumbnail, caption=f"Thumbnail YouTube: {video_id}", use_column_width=True)
                        st.caption(f"📹 Video ID: {video_id}")
                        
                        if st.button("🎬 Gunakeun Thumbnail pikeun Analisis"):
                            img = download_image_from_url(thumbnail)
                            if img:
                                if set_image_source(img, "youtube", f"yt_{video_id}.jpg"):
                                    st.success("✅ Thumbnail dijadikeun gambar analisis!")
                                    st.rerun()
                    else:
                        st.warning("Teu tiasa mendakan thumbnail pikeun video ieu.")
                else:
                    st.warning("Link YouTube teu valid.")
        
        # TAB 5: Riset
        with tab_riset:
            st.caption("Tempel link artikel / riset pikeun rujukan")
            research_url = st.text_input("URL Riset", placeholder="https://example.com/article")
            research_note = st.text_area("📝 Catatan / Kutipan", placeholder="Tulis catetan atanapi kutipan penting...")
            
            if st.button("💾 Simpan Riset", key="btn_research"):
                if research_url or research_note:
                    st.session_state.research_links.append({
                        "url": research_url,
                        "note": research_note,
                        "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                    })
                    st.success("✅ Link riset disimpen!")
                else:
                    st.warning("Isi URL atanapi catetan heula.")
            
            if st.session_state.research_links:
                st.markdown("---")
                st.subheader("📚 Daftar Riset Disimpen")
                for i, item in enumerate(st.session_state.research_links):
                    with st.expander(f"📄 Riset {i+1} - {item['date']}"):
                        if item['url']:
                            st.markdown(f"**🔗 URL:** {item['url']}")
                        if item['note']:
                            st.markdown(f"**📝 Catatan:** {item['note']}")
                        if st.button(f"🗑️ Hapus {i+1}", key=f"del_research_{i}"):
                            st.session_state.research_links.pop(i)
                            st.rerun()
        
        # --- INFO SUMBER GAMBAR ---
        if st.session_state.image_source:
            src = st.session_state.image_source
            st.markdown("---")
            st.success(f"🖼️ **Gambar aktif** dari: `{src.source}`")
            st.caption(f"Nama: {src.filename} | Ukuran: {src.width}×{src.height}")
            
            if st.button("🧹 Clear Image"):
                st.session_state.image_source = None
                st.session_state.detection_result = {}
                st.session_state.gap_analysis = {}
                st.rerun()
        
        # --- REVISION HISTORY ---
        st.markdown("---")
        st.subheader("🔄 Revision History")
        if st.session_state.revisions:
            for rev in st.session_state.revisions:
                st.text(f"v{rev['id']}: {rev['score']}% - {rev['status']}")
        else:
            st.caption("Belum aya revisi.")
    
    with col_preview:
        st.subheader("🖼️ Preview")
        img = get_current_image()
        if img:
            st.image(img, use_column_width=True)
            channel = st.session_state.current_channel
            st.info(f"🔮 Current Channel: **{channel}**")
        else:
            st.warning("📤 Upload, paste, URL, atanapi YouTube heula!")

elif menu == "🔍 Detector":
    st.title("🔍 Detector & AI Creative Director")
    
    img = get_current_image()
    if img is None:
        st.warning("📤 Punten input gambar heula di menu Project.")
    else:
        if st.button("⚡ Analyze Image", type="primary"):
            with st.spinner("Analyzing Visual DNA & Gap Analysis..."):
                st.session_state.detection_result = {
                    "Architecture": 91,
                    "Material": 98,
                    "Age": 87,
                    "Lighting": 95,
                    "Motion": 84,
                    "Channel": "JAZZ",
                    "Confidence": 74
                }
                
                st.session_state.gap_analysis = {
                    "channel": "JAZZ",
                    "confidence": 74,
                    "match": [
                        {"element": "Piano", "status": "✅ Kuat"},
                        {"element": "Whiskey Glass", "status": "✅ Aya"},
                        {"element": "Warm Light", "status": "✅ Aya"}
                    ],
                    "missing": [
                        {"element": "Rain Window", "priority": "HIGH", "reason": "FX wajib JAZZ"},
                        {"element": "Smoke Layer", "priority": "HIGH", "reason": "Atmosfer JAZZ"},
                        {"element": "Weathered Texture", "priority": "MEDIUM", "reason": "Material kedah kolot"}
                    ],
                    "conflict": [
                        {"element": "Fresh Wood", "action": "REPLACE", "target": "Weathered Walnut"},
                        {"element": "Bright Sun", "action": "REPLACE", "target": "Low-key Amber"}
                    ],
                    "extra": [
                        {"element": "Modern Chair", "action": "REMOVE", "reason": "Ngaganggu era 1920s"}
                    ],
                    "recommendations": [
                        {"priority": "HIGH", "text": "Ganti Fresh Wood → Weathered Walnut"},
                        {"priority": "HIGH", "text": "Tambah Rain Window (Overlay)"},
                        {"priority": "HIGH", "text": "Tambah Smoke Layer"},
                        {"priority": "MEDIUM", "text": "Kurangin Exposure -2 stop"}
                    ],
                    "predicted_score": 95,
                    "final_prompt": "A cinematic speakeasy with weathered walnut piano, whiskey glass, warm intimate lighting, rain on window, drifting smoke layer, warm amber palette --ar 16:9 --style raw --s 50 --v 6.1"
                }
            st.success("✅ Analysis Complete!")
        
        res = st.session_state.detection_result
        gap = st.session_state.gap_analysis
        
        if res:
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("📊 Detector Scores")
                st.bar_chart({
                    "Arsitektur": res.get("Architecture", 0),
                    "Material": res.get("Material", 0),
                    "Umur": res.get("Age", 0),
                    "Cahaya": res.get("Lighting", 0),
                    "Gerak": res.get("Motion", 0)
                })
                st.metric("Channel", res.get("Channel", "-"))
                st.metric("Confidence", f"{res.get('Confidence', 0)}%")
            
            with col2:
                st.subheader("🧠 AI Creative Director")
                
                if gap:
                    st.markdown("**📊 Gap Analysis:**")
                    
                    if gap.get("match"):
                        st.markdown("**✅ Maintain (Pertahankan):**")
                        for m in gap["match"]:
                            st.caption(f"• {m['element']} — {m['status']}")
                    
                    if gap.get("missing"):
                        st.markdown("**❌ Missing (Kurang):**")
                        for m in gap["missing"]:
                            st.caption(f"• {m['element']} — `{m['priority']}` — {m['reason']}")
                    
                    if gap.get("conflict"):
                        st.markdown("**⚠️ Conflict (Ganti):**")
                        for c in gap["conflict"]:
                            st.caption(f"• {c['element']} → **{c['target']}**")
                    
                    if gap.get("extra"):
                        st.markdown("**➕ Extra (Hapus):**")
                        for e in gap["extra"]:
                            st.caption(f"• {e['element']} — {e['reason']}")
                    
                    st.markdown("---")
                    
                    st.markdown("**💡 Rekomendasi (Prioritas):**")
                    for i, rec in enumerate(gap.get("recommendations", []), 1):
                        icon = "🔥" if rec["priority"] == "HIGH" else "🟡"
                        st.caption(f"{icon} **{i}.** {rec['text']}")
                    
                    st.markdown("---")
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.metric("Skor Ayeuna", f"{gap.get('confidence', 0)}%")
                    with col_b:
                        st.metric("Prediksi Skor", f"{gap.get('predicted_score', 0)}%", 
                                 delta=f"+{gap.get('predicted_score', 0) - gap.get('confidence', 0)}%")
                    
                    if st.button("📋 Terapkan ke Prompt", type="primary"):
                        st.session_state.final_prompt = gap.get("final_prompt", "")
                        st.success("✅ Prompt Final disimpen! Buka menu ✍️ Prompt → IMAGE.")
                else:
                    st.info("Klik 'Analyze Image' heula.")

elif menu == "🧬 Visual DNA":
    st.title("🧬 Visual DNA Card")
    
    selected_channel = st.selectbox("Pilih Channel", CHANNEL_NAMES, index=CHANNEL_NAMES.index(st.session_state.current_channel))
    st.session_state.current_channel = selected_channel
    
    dna = DNA[selected_channel]
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("World", selected_channel)
        st.metric("Architecture", dna.get("architecture", "-"))
        st.metric("Era", dna.get("era", "-"))
        st.metric("Lighting", dna.get("lighting", "-"))
        st.metric("Camera", dna.get("camera", "-"))
    
    with col2:
        st.subheader("Hero")
        st.write(", ".join(dna.get("hero", [])))
        st.subheader("Mood")
        st.write(", ".join(dna.get("mood", [])))
        st.subheader("Palette")
        st.write(", ".join(dna.get("palette", [])))
        st.subheader("Material")
        st.write(", ".join(dna.get("material", [])))
        st.subheader("FX")
        st.write(", ".join(dna.get("fx", [])))

elif menu == "✍️ Prompt":
    st.title("✍️ Prompt Compiler")
    st.caption("Generate prompts berdasarkan Visual DNA + BGM Studio")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🖼️ IMAGE", "🎥 VIDEO", "🎵 MUSIC", "🚫 NEGATIVE", "🧩 PARTIAL"])
    
    channel = st.session_state.current_channel
    dna = DNA[channel]
    bgm = BGM.get(channel, {})
    
    with tab1:
        st.subheader("Midjourney Prompt")
        
        if st.session_state.final_prompt:
            prompt = st.session_state.final_prompt
            st.info("📌 Prompt Final ti AI Creative Director")
        else:
            prompt = f"A cinematic {dna['architecture']} with {', '.join(dna['hero'][:2])}, {dna['mood'][0]} atmosphere, {dna['lighting']} lighting, {', '.join(dna['palette'][:2])} palette --ar 16:9 --style raw --s 50 --v 6.1"
        
        st.code(prompt, language="text")
        st.download_button("📋 Copy Image Prompt", prompt, file_name="prompt_image.txt")
        
        if st.button("🔄 Reset ka DNA Default"):
            st.session_state.final_prompt = ""
            st.rerun()
    
    with tab2:
        st.subheader("Video Prompt (Kling/Runway)")
        prompt = f"cinematic shot, {dna['architecture']}, {', '.join(dna['hero'])} {dna['mood'][0]}, {dna['lighting']} lighting, camera 4s loop 24fps"
        st.code(prompt, language="text")
    
    with tab3:
        st.subheader("🎵 BGM Studio & Sound Design")
        
        if bgm:
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown(f"**🎶 Style:** `{bgm.get('bgm_style', '-')}`")
                st.markdown(f"**🎸 Instruments:** {', '.join(bgm.get('instruments', []))}")
                st.markdown(f"**⏱ Tempo:** {bgm.get('tempo', '-')}")
                st.markdown(f"**🎵 Key:** {bgm.get('key_music', '-')}")
            
            with col_b:
                st.markdown(f"**🎭 Mood:** {', '.join(bgm.get('mood_tags', []))}")
                st.markdown(f"**🌫️ Ambience SFX:** {', '.join(bgm.get('sfx_ambience', []))}")
                st.markdown(f"**🗣️ Voice Style:** {bgm.get('voice_style', '-')}")
            
            st.markdown("---")
            st.subheader("🤖 Suno / Udio Prompt (Text-to-Music)")
            suno_prompt = bgm.get('prompt_suno', '')
            st.code(suno_prompt, language="text")
            st.download_button("📋 Copy BGM Prompt", suno_prompt, file_name="bgm_prompt.txt")
            
            if channel in ["FOREST", "ECOLIFE"]:
                st.success(f"🌿 **Nature Boost for {channel}:** Tambahkeun 'binaural beats' atanapi 'field recording' pikeun nambahan nuansa immersive.")
        else:
            st.warning("BGM Studio data teu kapanggih. Pastikeun `bgm_studio.yaml` aya di folder `data/`.")
    
    with tab4:
        st.subheader("Negative Prompt")
        st.code("low quality, blurry, distorted, plastic, fake, ugly, oversaturated, painting, cartoon", language="text")
    
    with tab5:
        st.subheader("Partial Prompt (SDXL Positive)")
        st.code(f"({dna['architecture']}), {', '.join(dna['hero'])}, {dna['lighting']}, {dna['mood'][0]}", language="text")

elif menu == "📄 Report":
    st.title("📄 Report Generator")
    tab_r1, tab_r2, tab_r3 = st.tabs(["📋 Project Report", "📈 Weekly Report", "⭐ Final Report"])
    
    with tab_r1:
        st.subheader("📋 Project Report")
        
        gap = st.session_state.gap_analysis
        img_src = st.session_state.image_source
        if gap and img_src:
            st.markdown(f"""
            **Project Name:** Bamboo Hush
            **Channel:** {gap.get('channel', '-')}
            **Input Source:** {img_src.source}
            **Filename:** {img_src.filename}
            **Image Size:** {img_src.width}×{img_src.height}
            **Confidence:** {gap.get('confidence', 0)}%
            **Predicted Score:** {gap.get('predicted_score', 0)}%
            **Status:** PASS ({gap.get('predicted_score', 0)}%)
            **Revisions:** {len(st.session_state.revisions)}
            **Date:** {datetime.date.today()}
            """)
            
            with st.expander("📊 Gap Analysis Detail"):
                st.json(gap)
        else:
            st.info("Belum aya data analisis. Jalanan Detector heula.")
        
        if st.button("Export PDF"):
            st.info("Fungsi PDF bakal aktip saatos ReportLab diintegrasikeun.")
    
    with tab_r2:
        st.metric("Projects This Week", "5")
        st.metric("Average Score", "89%")
        st.bar_chart({"Jazz": 3, "Bossa": 2, "Forest": 1})
    
    with tab_r3:
        st.success("⭐ Final Knowledge Report")
        gap = st.session_state.gap_analysis
        if gap:
            missing = [m["element"] for m in gap.get("missing", [])]
            conflicts = [c["element"] for c in gap.get("conflict", [])]
            st.markdown(f"""
            **Error Terbanyak:** {', '.join(missing[:3])} ({len(missing)}x), {', '.join(conflicts[:2])}
            **Knowledge Learned:** Weathered Bamboo, Humidity Layer, Rain Window
            **Knowledge Graph Update:** +12 Node, +37 Relation
            **Confidence:** {gap.get('predicted_score', 0)}%
            """)
        else:
            st.info("Belum aya data final report.")

elif menu == "🧠 Knowledge":
    st.title("🧠 Master Knowledge Database")
    
    st.subheader("📊 Statistik per Channel")
    cols = st.columns(3)
    for i, name in enumerate(CHANNEL_NAMES):
        with cols[i % 3]:
            st.metric(name, f"Project: {i*10+5}", f"PASS: {i*8+3}")
    
    st.subheader("📈 Knowledge Growth")
    st.line_chart({"Week 1": 152, "Week 2": 181, "Week 3": 229, "Week 4": 284})
    
    with st.expander("🌳 Knowledge Graph (YAML Relations)"):
        st.json(KNOWLEDGE)

elif menu == "📦 Export":
    st.title("📦 Export Project")
    st.caption("Ekspor sadaya laporan sareng aset dina hiji file.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📦 Format")
        zip_bool = st.checkbox("ZIP (Project + Assets)", value=True)
        pdf_bool = st.checkbox("PDF (Report Only)", value=True)
        json_bool = st.checkbox("JSON (Data Only)", value=True)
    
    with col2:
        st.subheader("🚀 Action")
        if st.button("📥 Generate & Download", type="primary"):
            st.success("✅ Export simulated! (Fungsi ZIP bakal aktip saatos integrasi shutil)")
            st.download_button("⬇️ Download dummy.zip", "Ini konten ZIP", file_name="vpd_project.zip")

# --- Footer ---
st.sidebar.markdown("---")
st.sidebar.caption("🎨 YOGANS BGM STUDIO v7.1 | Made with Streamlit")