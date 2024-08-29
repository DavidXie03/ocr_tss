from flask import Flask, render_template, request, url_for, jsonify
import pyttsx3
import easyocr
import uuid
import os

app = Flask(__name__)
reader = easyocr.Reader(['ch_sim', 'en'], True)
engine = pyttsx3.init()

# 文件保存目录
UPLOAD_FOLDER = 'static/uploads'
AUDIO_FOLDER = 'static/audio'

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        f = request.files['file']

        # 保存上传的图片
        unique_id = str(uuid.uuid4())
        pic_file_name = unique_id + ".png"
        pic_file_path = os.path.join(UPLOAD_FOLDER, pic_file_name)
        f.save(pic_file_path)

        # 识别图片中的文字
        ocr_result = reader.readtext(pic_file_path, detail=0, paragraph=True)
        ocr_result = ", ".join(ocr_result)

        # 生成音频文件
        audio_file_name = unique_id + ".mp3"
        audio_file_path = os.path.join(AUDIO_FOLDER, audio_file_name)
        engine.save_to_file(ocr_result, audio_file_path)
        engine.runAndWait()

        # 返回图片和音频文件的 URL
        image_url = url_for('static', filename=f'uploads/{pic_file_name}')
        audio_url = url_for('static', filename=f'audio/{audio_file_name}')
        return jsonify({'image_url': image_url, 'audio_url': audio_url})
    else:
        return render_template('upload.html')


if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    if not os.path.exists(AUDIO_FOLDER):
        os.makedirs(AUDIO_FOLDER)
    app.run(debug=True)