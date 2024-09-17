from flask import Flask, render_template, request, url_for, jsonify, send_from_directory, redirect
import pyttsx3
import easyocr
import uuid
import os
import pymysql
from contextlib import closing
import database


class Uploader:
    def __init__(self, upload_folder='static/uploads', audio_folder='static/audio'):
        self.app = Flask(__name__)
        self.reader = easyocr.Reader(['ch_sim', 'en'], True)
        self.engine = pyttsx3.init()
        self.UPLOAD_FOLDER = upload_folder
        self.AUDIO_FOLDER = audio_folder
        # self.file_received = False
        self._setup_routes()
        self.user = database.User()
        self.id = 0

    def _setup_routes(self):
        @self.app.route('/index')
        def first_page():
            return render_template('first.html')

        @self.app.route('/')
        def redirect_to_index():
            """
            当访问根 URL '/' 时，自动重定向到 '/index'
            """
            return redirect(url_for('first_page'))

        @self.app.route('/login', methods=['GET', 'POST'])
        def login():
            if request.method == 'GET':
                return render_template('login.html')
            elif request.method == 'POST':

                data = request.get_json()
                account = data['username']
                password = data['password']

                try:
                    self.id = self.user.login(account, password)

                    if self.id != 0:
                        return jsonify({'message': 'Login successful'}), 200
                    else:
                        return jsonify({'message': 'Invalid credentials'}), 401

                except Exception as e:
                    print(f"Error during login: {e}")
                    return jsonify({'message': 'An error occurred'}), 500

        @self.app.route('/register', methods=['GET', 'POST'])
        def register():
            if request.method == 'GET':
                return render_template('register.html')
            elif request.method == 'POST':
                data = request.get_json()
                account = data['username']
                password = data['password']

                try:
                    flag = self.user.register(account, password)

                    if flag:
                        return jsonify({'message': 'Registration successful'}), 201
                    else:
                        return jsonify({'message': 'Account already exists'}), 409

                except Exception as e:
                    print(f"Error during registration: {e}")
                    self.user.connect().rollback()
                    return jsonify({'message': 'An error occurred'}), 500

        @self.app.route('/upload', methods=['GET', 'POST'])
        def upload_file():
            if request.method == 'POST':
                f = request.files['file']

                connection = self.user.connect()
                with closing(connection) as connection:
                    with closing(connection.cursor()) as cursor:
                        if self.id != 0:
                            # 保存上传的图片
                            unique_id = str(uuid.uuid4())
                            pic_file_name = unique_id + ".png"
                            pic_file_path = os.path.join(self.UPLOAD_FOLDER, pic_file_name)
                            f.save(pic_file_path)

                            # 识别图片中的文字
                            ocr_result = self.reader.readtext(pic_file_path, detail=0, paragraph=True)
                            ocr_result = ", ".join(ocr_result)

                            # 生成音频文件
                            audio_file_name = unique_id + ".mp3"
                            audio_file_path = os.path.join(self.AUDIO_FOLDER, audio_file_name)
                            self.engine.save_to_file(ocr_result, audio_file_path)
                            self.engine.runAndWait()

                            # 返回图片和音频文件的 URL
                            image_url = url_for('static', filename=f'uploads/{pic_file_name}')
                            audio_url = url_for('static', filename=f'audio/{audio_file_name}')
                            print(image_url)

                            # 插入图像路径
                            sql1 = "INSERT INTO images (user_id, imagepath) VALUES (%s, %s)"
                            cursor.execute(sql1, (self.id, image_url))
                            connection.commit()

                            # 插入音频路径
                            sql2 = "INSERT INTO audios (user_id, audiopath) VALUES (%s, %s)"
                            cursor.execute(sql2, (self.id, audio_url))
                            connection.commit()

                            return jsonify({'image_url': image_url, 'audio_url': audio_url})
            else:
                return render_template('upload.html')

        @self.app.route('/get_images')
        def get_images():
            connection = self.user.connect()
            sql = "SELECT imagepath FROM images WHERE user_id = %s"
            with closing(connection) as connection:
                with closing(connection.cursor()) as cursor:
                    cursor.execute(sql, self.id)
                    images = cursor.fetchall()
                    images = [','.join(item) for item in images]
                    images = [item.replace(',', '') for item in images]
                    images = [item.replace('(', '') for item in images]
                    image_urls = [item.replace(')', '') for item in images]
                    print(images)
            return render_template('get_image.html', image_urls=image_urls)

        @self.app.route('/get_audios')
        def get_audios():
            connection = self.user.connect()
            sql = "SELECT audiopath FROM audios WHERE user_id = %s"
            with closing(connection) as connection:
                with closing(connection.cursor()) as cursor:
                    cursor.execute(sql, self.id)
                    audios = cursor.fetchall()
                    audios = [','.join(item) for item in audios]
                    audios = [item.replace(',', '') for item in audios]
                    audios = [item.replace('(', '') for item in audios]
                    audio_urls = [item.replace(')', '') for item in audios]
                    print(audio_urls)
            return render_template('get_audio.html', audio_urls=audio_urls)

        @self.app.route('/audio/<path:filename>')
        def get_audio(filename):
            return send_from_directory('static/audio', filename)

    def run(self, debug=True):
        if not os.path.exists(self.UPLOAD_FOLDER):
            os.makedirs(self.UPLOAD_FOLDER)
        if not os.path.exists(self.AUDIO_FOLDER):
            os.makedirs(self.AUDIO_FOLDER)
        self.app.run(debug=debug)


# 使用示例
if __name__ == '__main__':
    uploader = Uploader()
    uploader.run(debug=True)
