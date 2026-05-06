import streamlit as st
import os
from PIL import Image
import whisper
from moviepy import VideoFileClip, TextClip, CompositeVideoClip

# -----------------------
# MOBILE OPTIMIZED APP
# -----------------------
st.set_page_config(
    page_title="Dragon AI Shorts",
    page_icon="🐉",
    layout="centered"
)

# -----------------------
# LOGO SAFE
# -----------------------
icon_path = os.path.join(os.path.dirname(__file__), "logo.png")

if os.path.exists(icon_path):
    st.image(icon_path, width=110)
else:
    st.title("🐉 Dragon AI Shorts")

st.write("📱 PERFECT MOBILE MODE")

# -----------------------
# SESSION STATE
# -----------------------
if "page" not in st.session_state:
    st.session_state.page = "home"

if "video_path" not in st.session_state:
    st.session_state.video_path = None

if "outputs" not in st.session_state:
    st.session_state.outputs = []

# -----------------------
# HOME
# -----------------------
if st.session_state.page == "home":

    uploaded_file = st.file_uploader("📤 Video hochladen", type=["mp4"])

    if uploaded_file:

        os.makedirs("temp", exist_ok=True)
        video_path = "temp/video.mp4"

        with open(video_path, "wb") as f:
            f.write(uploaded_file.read())

        st.session_state.video_path = video_path
        st.success("✅ Video bereit")

    if st.button("🚀 START AI") and st.session_state.video_path:
        st.session_state.page = "run"
        st.rerun()

# -----------------------
# PROCESSING (MOBILE OPTIMIZED)
# -----------------------
if st.session_state.page == "run":

    st.title("⏳ Processing...")

    progress = st.progress(0)
    status = st.empty()

    video_path = st.session_state.video_path

    # ⚡ LIGHT AI MODEL (FAST FOR MOBILE)
    status.text("🧠 AI lädt...")
    model = whisper.load_model("tiny")
    progress.progress(20)

    status.text("📝 Analyse...")
    result = model.transcribe(video_path, fp16=False)
    segments = result["segments"][:6]  # 🔥 weniger = schneller
    progress.progress(50)

    status.text("🎥 Video laden...")
    video = VideoFileClip(video_path).resized(height=720)  # 📱 MOBILE BALANCE

    clips = []

    for s in segments:
        start = int(s["start"])
        end = int(s["end"])
        text = s["text"]

        if end - start < 3:
            continue

        score = len(text) * 0.02
        clips.append((start, end, text, score))

    clips = sorted(clips, key=lambda x: x[3], reverse=True)[:2]  # 🔥 ONLY 2 CLIPS

    os.makedirs("output", exist_ok=True)

    outputs = []

    progress.progress(70)
    status.text("✂️ Clips erstellen...")

    for i, (start, end, text, score) in enumerate(clips):

        clip = video.subclipped(start, end)

        try:
            txt = TextClip(
                text[:50],
                fontsize=35,
                color="white",
                stroke_color="black",
                stroke_width=2,
                method="caption",
                size=(600, None)
            ).set_position(("center", "bottom")).set_duration(clip.duration)

            clip = CompositeVideoClip([clip, txt])

        except:
            pass

        out_path = f"output/clip_{i+1}.mp4"

        clip.write_videofile(
            out_path,
            codec="libx264",
            audio_codec="aac",
            fps=30,
            bitrate="4000k",      # 📱 MOBILE QUALITY
            preset="veryfast"     # ⚡ SPEED MODE
        )

        outputs.append(out_path)

    progress.progress(100)
    status.text("✅ Fertig!")

    st.session_state.outputs = outputs
    st.session_state.page = "result"
    st.rerun()

# -----------------------
# RESULT
# -----------------------
if st.session_state.page == "result":

    st.title("🔥 Deine Clips")

    for file in st.session_state.outputs:

        st.video(file)

        with open(file, "rb") as f:
            st.download_button(
                "⬇️ Download",
                f,
                file_name=os.path.basename(file)
            )

    if st.button("🔁 Neues Video"):
        st.session_state.page = "home"
        st.rerun()