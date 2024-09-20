# -*- coding = utf-8 -*-
# @Time: 2024-09-19 19:32
# @Author: DavidXie03
# @File: photo_rotate.py
# @Software: PyCharm

from PIL import Image

def load_image(image_path):
    """
    通过给定的路径加载图像。
    :param image_path: 图像的路径
    :return: 返回一个PIL图像对象
    """
    try:
        img = Image.open(image_path)
        print(f"成功加载图像: {image_path}")
        return img
    except Exception as e:
        print(f"加载图像时出错: {e}")
        return None

def preprocess(input_path, output_path, quality=25):
    """
    检测图片方向并进行旋转校正，然后压缩保存
    :param input_path: 要处理的图像路径
    :param output_path: 处理后图像的保存路径
    :param quality: 压缩质量，范围为1-100，默认为85。值越低，压缩率越高，质量越差。
    :return: None
    """
    try:
        image = load_image(input_path)
        exif = image.getexif()

        if exif is not None:
            # 获取图像的方向信息
            orientation = exif.get(274)
            # 根据方向旋转图像
            if orientation == 3:
                image = image.rotate(180, expand=True)
            elif orientation == 6:
                image = image.rotate(270, expand=True)
            elif orientation == 8:
                image = image.rotate(90, expand=True)
            else:
                pass
            image = image.convert('RGB')
            image.save(output_path, "JPEG", quality=quality)
            print(f"图像已成功保存到: {output_path}")
    except Exception as e:
        print(f"保存图像时出错: {e}")

if __name__ == "__main__":
    input_path = "static/uploads/73f273d1-d2cc-45ed-bf46-c11f12816b67.png"
    output_path = "static/uploads/73f273d1-d2cc-45ed-bf46-c11f12816b67-1.png"
    preprocess(input_path, output_path)