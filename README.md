<div align="center">
<h1>OCR_TSS</h1>
<h3>摄像头图像文字识别及语音播报系统</h3>

作者: [David Xie](https://github.com/DavidXie03), [Wei](https://github.com/1094119379), [Zhu](https://github.com/dydjbl)
</div>

## 📜 简介
摄像头图像文字识别及语音播报系统的研究旨在通过摄像头采集图像，利用先进的图像文字识别技术将图像中的文字信息提取出来，并通过语音合成技术将识别结果进行语音播报。

该系统在辅助育人和视障人士获取图像信息、提升信息获取的便捷性以及在智能家居和智能监控等领域具有广泛的应用前景。

主要研究任务包括:开发高精度的图像文字识别算法、实现高效的语音合成技术，以及构建一体化的系统架构以实现实时文字识别与语音播报功能。

## 🎬 演示Demo

https://github.com/user-attachments/assets/75133d9e-675e-485d-b0e0-1341e18c14c5

## 🎮 如何运行

### 1. 环境配置
配置python并下载以下依赖：
```shell
pip install torch torchvision flask easyocr pyttsx3 pymysql pillow
```

### 2. 数据库创建
运行sql代码创建库表，注意默认数据库用户名为`root`，默认密码为`123456`，如需更改请修改`database.py`。
```sql
CREATE DATABASE user_message;

CREATE TABLE user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    account VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(50) NOT NULL
);

CREATE TABLE history (
	user_id INT NOT NULL,
    imagepath VARCHAR(255) NOT NULL,
    audiopath VARCHAR(255) NOT NULL,
    text VARCHAR(1023) NOT NULL,
    upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 3. 内网穿透配置
使用内网穿透以便客户端访问服务端，本地地址为`127.0.0.1:5000`。

### 4. 运行
运行`app.py`启动服务端，并结合客户端app使用。

## 🌞 相关链接
* [接口文档](https://www.showdoc.com.cn/ocrtss2024) （访问密码：ocrtss@）
* [客户端仓库](https://github.com/dydjbl/PhotosAudioApp)
