from flask import Flask, render_template, request, url_for, jsonify, redirect
import pyttsx3
import easyocr
import uuid
import os
import pymysql
from contextlib import closing
from photo_preprocess import preprocess
import database


class Uploader:
    def __init__(self, url='https://70046236dd.imdo.co', upload_folder='static/uploads', audio_folder='static/audio'):
        self.app = Flask(__name__)
        self.reader = easyocr.Reader(['ch_sim', 'en'], True)
        self.engine = pyttsx3.init()
        self.url = url
        self.UPLOAD_FOLDER = upload_folder
        self.AUDIO_FOLDER = audio_folder
        # self.file_received = False
        self._setup_routes()
        self.user = database.User()
        self.id = 0
        self.offset = 0

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

        @self.app.route('/user/login', methods=['GET', 'POST'])
        def login():
            if request.method == 'GET':
                return render_template('login.html')
            elif request.method == 'POST':

                data = request.get_json()
                account = data['userName']
                password = data['password']

                self.id = self.user.login(account, password)

                if self.id != 0:
                    response = {
                        "errorCode": 0,
                        "data": {
                            "uid": str(self.id),
                            "userName": account,
                        }
                    }
                    return jsonify(response)
                else:
                    return jsonify({"errorCode": 1, "message": "Invalid credentials"})

        @self.app.route('/user/register', methods=['GET', 'POST'])
        def register():
            if request.method == 'GET':
                return render_template('register.html')
            elif request.method == 'POST':
                data = request.get_json()
                account = data['userName']
                password = data['password']

                user_id = self.user.register(account, password)

                if user_id != 0:
                    response = {
                        "errorCode": 0,
                        "data": {
                            "uid": str(user_id),
                            "userName": account
                        }
                    }
                    return jsonify(response)
                else:
                    return jsonify({"errorCode": 2, 'message': 'Account already exists'})

        @self.app.route('/picture/handle', methods=['GET', 'POST'])
        def upload_file():
            if request.method == 'POST':
                uid = request.form['uid']
                f = request.files['picture']

                connection = self.user.connect()
                with closing(connection) as connection:
                    with closing(connection.cursor()) as cursor:
                        if self.id != 0:
                            # 保存上传的图片
                            unique_id = str(uuid.uuid4())
                            pic_file_name = unique_id + ".jpg"
                            pic_file_path = os.path.join(self.UPLOAD_FOLDER, pic_file_name)
                            f.save(pic_file_path)
                            preprocess(pic_file_path, pic_file_path)

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

                            sql = "INSERT INTO history (user_id, imagepath, audiopath) VALUES (%s, %s, %s)"
                            cursor.execute(sql, (self.id, image_url, audio_url))
                            connection.commit()

                            response = {
                                "errorCode": 0,
                                "data": {
                                    "imageUrl": self.url + image_url,
                                    "audioUrl": self.url + audio_url
                                }
                            }

                            return jsonify(response)
            else:
                return render_template('upload.html')

        @self.app.route('/picture/history', methods=['GET'])
        def get_history():
            connection = self.user.connect()
            sql_1 = "SELECT imagepath FROM history WHERE user_id = %s LIMIT %s OFFSET %s"
            sql_2 = "SELECT audiopath FROM history WHERE user_id = %s LIMIT %s OFFSET %s"
            uid = request.args.get('uid')
            picturesNum = int(request.args.get('picturesNum'))
            index = int(request.args.get('index'))
            with closing(connection) as connection:
                with closing(connection.cursor()) as cursor:
                    cursor.execute(sql_1, (uid, picturesNum, index))
                    images = cursor.fetchall()
                    images = [','.join(item) for item in images]
                    images = [item.replace(',', '') for item in images]
                    images = [item.replace('(', '') for item in images]
                    image_urls = [item.replace(')', '') for item in images]

                    cursor.execute(sql_2, (uid, picturesNum, index))
                    audios = cursor.fetchall()
                    audios = [','.join(item) for item in audios]
                    audios = [item.replace(',', '') for item in audios]
                    audios = [item.replace('(', '') for item in audios]
                    audio_urls = [item.replace(')', '') for item in audios]
            items = []
            num1 = len(image_urls)
            for i in range(num1):
                imerge = {
                    "imageUrl": self.url + image_urls[i],
                    "audioUrl": self.url + audio_urls[i]
                }
                items.append(imerge)
                # print(response)
            response = {
                "errorCode": 0,
                "data": {
                    "picturesNum": num1,
                    "items": items
                }
            }
            return jsonify(response)
            # else:
                # return jsonify({"errorCode": 409, 'message': 'Account already exists'})

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
