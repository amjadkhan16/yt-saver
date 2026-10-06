import streamlit as st
import streamlit.components.v1 as components
from yt_dlp import YoutubeDL
import os
import re
import tempfile

st.set_page_config(
    page_title="YT Saver — Free YouTube Downloader",
    page_icon="▶",
    layout="centered",
)

# ---- AD SLOT: apne ad network (Monetag/Adsterra/PropellerAds) ka code yahan paste karein ----
AD_CODE = """
<!-- AD SPACE: apna ad code yahan paste karein -->
"""


def show_ad():
    if AD_CODE.strip().startswith("<!--"):
        st.info("🔲 **Ad space** — ad network ka code lagane par yahan ad ayega.")
    else:
        components.html(AD_CODE, height=150, scrolling=False)


def base_opts():
    return {
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "socket_timeout": 25,
        # YouTube bot-check se bachne ke liye android player client
        "extractor_args": {"youtube": {"player_client": ["android"]}},
    }


def valid_yt_url(url: str) -> bool:
    return bool(re.match(
        r"^(https?://)?(www\.|m\.)?(youtube\.com/(watch|shorts|embed)|youtu\.be)/",
        url.strip(),
    ))


def safe_name(title: str, ext: str) -> str:
    name = re.sub(r"[^\w\s-]", "", title or "video").strip()[:60]
    return f"{name or 'video'}.{ext}"


def fmt_dur(s):
    if not s:
        return ""
    return f"{int(s // 60)}:{int(s % 60):02d}"


FORMATS = {
    "Best Quality (MP4)": {"format": "best[ext=mp4]/best", "ext": "mp4", "audio": False},
    "720p (MP4)": {"format": "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720]/best", "ext": "mp4", "audio": False},
    "480p (MP4)": {"format": "bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[height<=480]/best", "ext": "mp4", "audio": False},
    "360p (MP4)": {"format": "bestvideo[height<=360][ext=mp4]+bestaudio[ext=m4a]/best[height<=360]/best", "ext": "mp4", "audio": False},
    "Audio Only (MP3)": {"format": "bestaudio/best", "ext": "mp3", "audio": True},
}

# ---------------- UI ----------------
st.title("▶ YT Saver")
st.write("**Free YouTube Video Downloader** — link paste karo, quality chuno, download karo. Koi signup nahi.")

show_ad()

url = st.text_input("YouTube link", placeholder="https://www.youtube.com/watch?v=...")

if st.button("🎬 Video Lao", type="primary"):
    if not valid_yt_url(url):
        st.error("Sahi YouTube link paste karo (youtube.com ya youtu.be).")
    else:
        with st.spinner("Video ki info li ja rahi hai..."):
            try:
                with YoutubeDL(base_opts()) as ydl:
                    info = ydl.extract_info(url.strip(), download=False)
                st.session_state["vinfo"] = {
                    "title": info.get("title", "Video"),
                    "thumbnail": info.get("thumbnail", ""),
                    "duration": info.get("duration"),
                    "uploader": info.get("uploader", ""),
                }
                st.session_state["vurl"] = url.strip()
                st.session_state.pop("dlpath", None)
            except Exception as e:
                st.error(f"Video nahi mil saki: {e}")

vinfo = st.session_state.get("vinfo")
if vinfo:
    st.divider()
    if vinfo["thumbnail"]:
        st.image(vinfo["thumbnail"], width=480)
    st.subheader(vinfo["title"])
    meta = " • ".join(x for x in [vinfo["uploader"], fmt_dur(vinfo["duration"])] if x)
    if meta:
        st.caption(meta)

    choice = st.selectbox("Quality chuno", list(FORMATS.keys()))
    if st.button("⬇ Download Tayyar Karo"):
        spec = FORMATS[choice]
        tmpdir = tempfile.mkdtemp(prefix="ytsaver_")
        outtmpl = os.path.join(tmpdir, "%(title).60s.%(ext)s")
        opts = base_opts()
        opts.update({
            "format": spec["format"],
            "outtmpl": outtmpl,
            "merge_output_format": "mp4",
        })
        if spec["audio"]:
            opts["postprocessors"] = [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }]
        with st.spinner("Download tayyar ho raha hai... (thoda waqt lag sakta hai)"):
            try:
                with YoutubeDL(opts) as ydl:
                    ydl.download([st.session_state["vurl"]])
                files = [os.path.join(tmpdir, f) for f in os.listdir(tmpdir)]
                if not files:
                    raise RuntimeError("File nahi bani.")
                st.session_state["dlpath"] = files[0]
                st.session_state["dlname"] = safe_name(vinfo["title"], spec["ext"])
            except Exception as e:
                st.error(f"Download mein masla: {e}")

    dlpath = st.session_state.get("dlpath")
    if dlpath and os.path.exists(dlpath):
        with open(dlpath, "rb") as f:
            data = f.read()
        st.download_button(
            "⬇ Abhi Download Karo",
            data=data,
            file_name=st.session_state.get("dlname", "video.mp4"),
            mime="application/octet-stream",
            type="primary",
        )
        st.caption(f"Size: {len(data) / 1048576:.1f} MB")
        try:
            os.remove(dlpath)
        except OSError:
            pass

st.divider()
show_ad()
st.caption(
    "Sirf apni ya copyright-free videos download karein. "
    "Creators ke huqooq aur YouTube ki Terms ka ehtram karein."
)
