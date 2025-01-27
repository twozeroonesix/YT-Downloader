#!/bin/bash
echo "Installing Python dependencies..."
pip3 install Flask yt-dlp colorama
echo "Running YT-Downloader.py"
python3 ytdl.py