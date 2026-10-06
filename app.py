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

# ---- AD SLOT ----
# Apne ad network ka code yahan paste karein:
# - Google AdSense: AdSense dashboard se mila ad code
# - Ya backup: Monetag / Adsterra / PropellerAds ka code
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

# ---------------- NAV ----------------
page = st.sidebar.radio("Pages", ["🏠 Downloader", "🔒 Privacy Policy", "✉️ Contact"])

# ---------------- CONTACT PAGE ----------------
if page == "✉️ Contact":
    st.title("✉️ Contact")
    st.write(
        "Koi sawal, feedback ya copyright se mutaliq darkhwast ho to "
        "neeche diye gaye email par rabta karein:"
    )
    # >>> APNA EMAIL YAHAN LIKHEIN (AdSense ke liye asli email zaroori hai) <<<
    CONTACT_EMAIL = "your-email@example.com"
    st.markdown(f"📧 **Email:** `{CONTACT_EMAIL}`")
    st.write("Hum aam tor par 48 hours ke andar jawab dene ki koshish karte hain.")
    st.divider()
    st.caption("© 2026 YT Saver. All rights reserved.")

# ---------------- PRIVACY POLICY PAGE ----------------
elif page == "🔒 Privacy Policy":
    st.title("🔒 Privacy Policy")
    st.caption("Last updated: October 2026")
    st.markdown("""
**YT Saver** ("we", "our", "this website") respects your privacy. This policy
explains what information is handled when you use our free YouTube downloader.

### 1. Information we collect
We do **not** require any account, sign-up, or login. We do not ask for your
name, email address, or any personal details to use the downloader.

### 2. How the service works
- The YouTube link you paste is used only to fetch that video's public
  information (title, thumbnail, available formats) and to prepare your download.
- Downloaded files are created temporarily on the server only to deliver them
  to you, and are deleted automatically afterwards.
- We do **not** store your links, your downloads, or any file on our servers
  permanently.

### 3. Cookies and advertising
- This website may display advertisements served by third-party ad networks
  (for example Google AdSense, Monetag, Adsterra, or PropellerAds).
- These ad partners may use cookies or similar technologies to show you
  relevant ads and to measure ad performance. You can control cookies through
  your browser settings.
- We do not control how third-party advertisers use cookies; please review
  their own privacy policies.

### 4. Copyright
This tool is intended only for downloading videos that you own, that are
copyright-free, or that you have permission to download. Downloading
copyrighted material without permission may violate the law and YouTube's
Terms of Service. If you are a rights holder and believe your content is
being misused, please contact us via the Contact page and we will respond
promptly.

### 5. Children's privacy
This website is not directed at children under 13, and we do not knowingly
collect information from children.

### 6. Changes to this policy
We may update this Privacy Policy from time to time. The "Last updated" date
at the top will reflect the latest version.

### 7. Contact
Questions about this policy? Reach us through the **Contact** page.
""")
    st.divider()
    st.caption("© 2026 YT Saver. All rights reserved.")

# ---------------- DOWNLOADER (HOME) ----------------
else:
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
