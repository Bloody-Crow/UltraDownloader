# 📥 Ultra Downloader
> **The Ultimate CLI Video Downloader for Linux.**
> *Powered by [yt-dlp](https://github.com/yt-dlp/yt-dlp), FFmpeg, and Python.*

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Linux-black?style=for-the-badge&logo=linux&logoColor=white)
![License](https://img.shields.io/badge/License-Unlicense-green?style=for-the-badge)

**Ultra Downloader** is a sophisticated terminal-based application designed to download high-quality videos from virtually any website. It features an intelligent Text User Interface (TUI) that adapts to the platform you are downloading from.

---

## ✨ Key Features

### 🌍 Universal Support
*   **YouTube:** Fetches all available resolutions (144p to 8K). Displays a clean, aligned grid with **calculated file size estimates**.
*   **Social Media:** Auto-detects single-source videos from **TikTok, Instagram, Twitter/X, and Reddit**, skipping the menu for instant downloads.
*   **1000+ Sites:** Supports Vimeo, Twitch, SoundCloud, DailyMotion, and [more](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md).

### 🧠 Smart Logic
*   **Browser Auth Bridge:** Bypasses "Sign-In Required" and "Age Restricted" errors by borrowing cookies from your local browser (Firefox, Chrome, Chromium, or Brave).
*   **Auto-Proxy Detection:** Automatically scans your system and local ports (1080, 7890, etc.) for active VPNs/Proxies and routes traffic through them.
*   **High-Fidelity Merging:** Automatically identifies the best video stream and the best audio stream, downloading them separately and merging them via FFmpeg for maximum quality.

### 🎨 Beautiful TUI
*   Center-aligned interface.
*   Custom progress bar with **Part Detection** (Video vs Audio).
*   Mathematical smoothing for stable **ETA** and **Download Speed**.

---

## ⚙️ Prerequisites

You need a Linux system (Ubuntu/Debian recommended) with the following installed:

1.  **Python 3**
2.  **FFmpeg** (Crucial for merging high-quality streams)
3.  **Node.js & PhantomJS** (Required for solving YouTube's latest crypto-challenges)

#### ⚡ One-Line Prerequisites Installation (Ubuntu/Debian)
```
sudo apt update && sudo apt install ffmpeg nodejs phantomjs python3-venv -y
```

---


## 🚀 Installation

**1. Clone the repository and go to the directory:**
```
git clone https://github.com/YOUR_USERNAME/UltraDownloader.git
cd UltraDownloader
```

**2. Set up the environment:**
```
# Create a virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

**3. Make the launcher executable:**
```
chmod +x launch.sh
```

## 🖥️ Usage

**You can run the app directly from the terminal:**
```
./launch.sh
```

## 🐛 Troubleshooting

### "n challenge solving failed" Warning:
**This means YouTube has updated their anti-bot scripts.**

*   Ensure nodejs and phantomjs are installed.

*   The app uses a custom logger to suppress this warning if it doesn't affect download speed.

### Firefox Permission Denied:
*   Ubuntu installs Firefox as a "Snap" package by default, which blocks external apps from reading cookies.
