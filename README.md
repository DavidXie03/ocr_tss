# ocr_tss

### 简介
摄像头图像文字识别及语音播报系统的研究旨在通过摄像头采集图像，利用先进的图像文字识别技术将图像中的文字信息提取出来，并通过语音合成技术将识别结果进行语音播报。

该系统在辅助育人和视障人士获取图像信息、提升信息获取的便捷性以及在智能家居和智能监控等领域具有广泛的应用前景。

主要研究任务包括:开发高精度的图像文字识别算法、实现高效的语音合成技术，以及构建一体化的系统架构以实现实时文字识别与语音播报功能。

### 环境配置
```shell
pip install torch torchvision flask easyocr pyttsx3
```

### 数据库user_message创建
```shell
CREATE TABLE user (
	id INT AUTO_INCREMENT PRIMARY KEY,
    account VARCHAR(50) NOT NULL UNIQUE,
    passowrd VARCHAR(50) NOT NULL
);

CREATE TABLE images (
	user_id INT NOT NULL,
    imagepath VARCHAR(255) NOT NULL,
    upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE audios (
	user_id INT NOT NULL,
    audiopath VARCHAR(255) NOT NULL,
    upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 运行方式
网页端：运行`main.py`后访问 http://127.0.0.1:5000/upload ，上传文件后即可得到语音播报结果（待进一步完善）。"# software" 
