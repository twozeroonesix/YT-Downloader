from flask import Flask, request, render_template, send_from_directory, jsonify
import yt_dlp
import os

app = Flask(__name__)

# Конфигурация папок
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOWNLOAD_FOLDER = os.path.join(BASE_DIR, "downloads")
FFMPEG_FOLDER = os.path.join(BASE_DIR, "ffmpeg", "bin")
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

def check_ffmpeg():
    """
    Проверяет наличие ffmpeg в указанной папке.
    """
    ffmpeg_path = os.path.join(FFMPEG_FOLDER, "ffmpeg.exe")
    if not os.path.exists(ffmpeg_path):
        raise FileNotFoundError(
            f"FFmpeg not found at {ffmpeg_path}. Please ensure FFmpeg is installed and placed in the 'ffmpeg' folder."
        )

@app.route('/', methods=['GET', 'POST'])
def index():
    """
    Главная страница приложения.
    """
    if request.method == 'POST':
        # Логика для POST-запроса, если необходимо
        return jsonify({'message': 'POST request received on index'})
    return render_template('index.html')
@app.route('/download', methods=['POST'])
def download_video():
    """
    Обработчик для загрузки видео с YouTube.
    """
    try:
        check_ffmpeg()
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 500

    url = request.form.get('url')
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    video_quality = request.form.get('video_quality', 'best')
    audio_quality = request.form.get('audio_quality', 'best')
    resolution = request.form.get('resolution', 'best')
    output_format = request.form.get('format', 'mp4')
    codec = request.form.get('codec', 'h264')
    subtitles = request.form.get('subtitles', 'no') == 'yes'

    # Формат для загрузки
    format_string = f"bestvideo[height<={resolution}][ext={output_format}]+bestaudio[ext=m4a]/best[ext={output_format}]"

    # Опции для yt-dlp
    options = {
        'format': format_string,
        'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
        'merge_output_format': output_format,
        'postprocessors': [
            {
                'key': 'FFmpegVideoConvertor',
                'preferedformat': output_format,
            }
        ],
        'ffmpeg_location': FFMPEG_FOLDER,
    }

    if subtitles:
        options.update({
            'writesubtitles': True,
            'subtitleslangs': ['en'],  # Укажите нужные языки субтитров
            'subtitleformat': 'srt',  # Формат субтитров
        })

    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info).replace('.webm', f'.{output_format}')
            description = info.get('description', 'No description available')

        return jsonify({
            'message': 'Video downloaded successfully!',
            'filename': os.path.basename(filename),
            'description': description,
            'file_url': f'/files/{os.path.basename(filename)}'
        })
    except yt_dlp.utils.DownloadError as e:
        return jsonify({"error": f"Download error: {e}"}), 400
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {e}"}), 500

@app.route('/files/<path:filename>')
def serve_file(filename):
    """
    Предоставляет доступ к загруженным файлам.
    """
    try:
        return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=True)
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
