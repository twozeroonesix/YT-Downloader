#!/bin/bash
chmod +x ffmpeg/ffmpeg
echo "Installing Python dependencies..."
pip3 install Flask yt-dlp colorama
echo "Running YT-Downloader.py"
python3 ytdl.py