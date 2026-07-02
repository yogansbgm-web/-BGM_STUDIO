# VPD v7.1 - AI Creative Studio (FINAL)
# Streamlit UI - Adobe Lightroom + VSCode Style
# Integrated: BGM Studio + AI Creative Director + Gap Analysis

import streamlit as st
import yaml
import json
import os
import datetime
from pathlib import Path
from PIL import Image
import numpy as np

# --- Konfigurasi Halaman ---
st.set_page_config(
    page_title="VPD AI Creative Studio",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Load Data (YAML) ---
@st.cache_data
def load_dna():
    with open("data/channel_dna.yaml", "r") as f:
        return yaml.safe_load(f)

@st.cache_data
def load_knowledge():
    with open("data/knowledge_graph.yaml", "r") as f:
        return yaml.safe_load(f)

@st.cache_data
def load_bgm():
    try:
        with open("data/bgm_studio.yaml", "r") as f:
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
if 'uploaded_image' not in st.session_state:
    st.session_state.uploaded_image = None
if 'detection_result' not in st.session_state:
    st.session_state.detection_result = {}
if 'gap_analysis' not in st.session_state:
    st.session_state.gap_analysis = {}
if 'revisions' not in st.session_state:
    st.session_state.revisions = []
if 'final_prompt' not in st.session_state:
    st.session_state.final_prompt = ""

# --- SIDEBAR (8 MENU) ---
with st.sidebar:
    st.image("https://placehold.co/200x60/1a1a1a/FFB800?text=VPD+STUDIO", use_column_width=True)
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
    st.title("🎨 VPD AI Creative Studio")
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
    col_upload, col_preview = st.columns([1, 2])
    
    with col_upload:
        uploaded_file = st.file_uploader("Upload Image", type=["jpg", "png", "jpeg"])
        if uploaded_file is not None:
            st.session_state.uploaded_image = Image.open(uploaded_file)
            st.success("✅ Gambar siap!")
            st.caption("Nama: " + uploaded_file.name)
            
            if st.button("🧹 Clear Image"):
                st.session_state.uploaded_image = None
                st.session_state.detection_result = {}
                st.session_state.gap_analysis = {}
                st.rerun()
                
        st.markdown("---")
        st.subheader("🔄 Revision History")
        if st.session_state.revisions:
            for rev in st.session_state.revisions:
                st.text(f"v{rev['id']}: {rev['score']}% - {rev['status']}")
        else:
            st.caption("Belum aya revisi.")
    
    with col_preview:
        st.subheader("Preview")
        if st.session_state.uploaded_image:
            st.image(st.session_state.uploaded_image, use_column_width=True)
            st.info(f"🔮 Current Channel: **{st.session_state.current_channel}**")
        else:
            st.warning("Tonggo, upload gambar heula!")

elif menu == "🔍 Detector":
    st.title("🔍 Detector & AI Creative Director")
    
    if st.session_state.uploaded_image is None:
        st.warning("📤 Punten upload gambar heula di menu Project.")
    else:
        if st.button("⚡ Analyze Image", type="primary"):
            with st.spinner("Analyzing Visual DNA & Gap Analysis..."):
                # SIMULASI DETECTOR (OpenCV engké)
                st.session_state.detection_result = {
                    "Architecture": 91,
                    "Material": 98,
                    "Age": 87,
                    "Lighting": 95,
                    "Motion": 84,
                    "Channel": "JAZZ",
                    "Confidence": 74
                }
                
                # SIMULASI GAP ANALYSIS (AI Creative Director)
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
                    # Gap Analysis
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
                    
                    # Rekomendasi
                    st.markdown("**💡 Rekomendasi (Prioritas):**")
                    for i, rec in enumerate(gap.get("recommendations", []), 1):
                        icon = "🔥" if rec["priority"] == "HIGH" else "🟡"
                        st.caption(f"{icon} **{i}.** {rec['text']}")
                    
                    st.markdown("---")
                    
                    # Prediksi Skor
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.metric("Skor Ayeuna", f"{gap.get('confidence', 0)}%")
                    with col_b:
                        st.metric("Prediksi Skor", f"{gap.get('predicted_score', 0)}%", 
                                 delta=f"+{gap.get('predicted_score', 0) - gap.get('confidence', 0)}%")
                    
                    # Tombol Terapkan ke Prompt
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
        
        # Gunakan final_prompt lamun aya, lamun henteu make DNA standar
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
        
        # Tampilkan Gap Analysis dina report
        gap = st.session_state.gap_analysis
        if gap:
            st.markdown(f"""
            **Project Name:** Bamboo Hush
            **Channel:** {gap.get('channel', '-')}
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
st.sidebar.caption("🎨 VPD v7.1 | Made with Streamlit")