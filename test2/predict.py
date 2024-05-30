from flask import render_template, Flask, request, Response
import time
import cv2
import random
from models.experimental import attempt_load
from utils.torch_utils import select_device
import torch
import numpy as np
from utils.general import (non_max_suppression, scale_coords, xyxy2xywh, plot_one_box)
import serial
#/dev/ttyAMA0
try:
    ser = serial.Serial("/dev/ttyAMA0", 115200)
    ser_usb = serial.Serial("/dev/ttyUSB0", 9600)
except:
    print('接口未找到!!!')
    pass

if not ser.isOpen() and ser_usb.isOpen():
    print("open failed!!!")

else:
    print("open success: ")
    print(ser)

# 初始化
device = select_device()
# 下载模型
model = attempt_load('weights/flower.pt')

names = model.module.names if hasattr(model, 'module') else model.names
colors = [[random.randint(0, 255) for _ in range(3)] for _ in range(len(names))]


class VideoCamera(object):
    def __init__(self):
        try:
            self.video = cv2.VideoCapture(0)
        except:
            self.video = cv2.VideoCapture(1)

    def __del__(self):
        self.video.release()

    def get_frame(self):
        success, image = self.video.read()

        img = image.copy()
        img = np.transpose(img, (2, 0, 1))  # 三个数排序
        img = torch.from_numpy(img).to(device)
        img = img.float()
        img /= 255.0

        if img.ndimension() == 3:
            img = img.unsqueeze(0)  # 增加一个维度

        pred = model(img)[0]
        # print(pred)

        pred = non_max_suppression(pred, 0.4, 0.5)  # 大于0.4阈值的输出
        # 绘图
        gn = torch.tensor(image.shape)[[1, 0, 1, 0]]  # 获取图片尺寸
        if pred != [None]:
            for i, det in enumerate(pred):
                det[:, :4] = scale_coords(img.shape[2:], det[:, :4], image.shape).round()

                for *xyxy, conf, cls in reversed(det):
                    xywh = (xyxy2xywh(torch.tensor(xyxy).view(1, 4)) / gn).view(-1).tolist()
                    label = '%s %.2f' % (names[int(cls)], conf)
                    plot_one_box(xyxy, image, label=label, color=colors[int(cls)], line_thickness=1)

        # 转为jpg格式
        ret, jpeg = cv2.imencode('.jpg', image)
        return jpeg.tobytes()


def gen(camera):
    while True:
        frame = camera.get_frame()
        # 二进制类型是image/jpeg
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


root = Flask(__name__)


@root.route('/')
def index():
    return render_template("ind.html")


@root.post("/cmd")
def cmd():
    data = request.get_data().decode()
    print(data)
    if data == 'up':
        try:
            recv = '$DGT:75-78,0!'
            print("recv" + recv)
            ser.write(recv.encode())
            time.sleep(0.05)
        except KeyboardInterrupt:
            if ser != None:
                ser.close()
    elif data=='stop':
        try:
            recv = '$DST!'
            print("recv" + recv)
            ser.write(recv.encode())
            time.sleep(0.05)
        except KeyboardInterrupt:
            if ser != None:
                ser.close()
    elif data=='left': 
        try:
            recv = '$DGT:83-86,0!'
            print("recv" + recv)
            ser.write(recv.encode())
            time.sleep(0.05)
        except KeyboardInterrupt:
            if ser != None:
                ser.close()
    elif data=='right':
        try:
            recv = '$DGT:87-90,0!'
            print("recv" + recv)
            ser.write(recv.encode())
            time.sleep(0.05)
        except KeyboardInterrupt:
            if ser != None:
                ser.close()
    elif data=='stoop':
        try:
            recv = '{G0001#006P2400T1000!#007P1900T1000!#008P1500T1000!#003P2400T1000!#004P1900T1000!#005P1500T1000!#012P1500T0000!#002P1500T1000!#001P1900T1000!#000P2400T1000!#023P0600T1000!#022P1100T1000!#021P1500T1000!#011P1500T1000!#018P1500T1000!#019P1100T1000!#020P0600T1000!#015P1500T1000!#016P1100T1000!#017P0600T1000!}'
            print("recv" + recv)
            ser.write(recv.encode())
            time.sleep(0.05)
        except KeyboardInterrupt:
            if ser != None:
                ser.close()
    elif data=='down':
        try:
            recv = '$DGT:79-82,0!'
            print("recv" + recv)
            ser.write(recv.encode())
            time.sleep(0.05)
        except KeyboardInterrupt:
            if ser != None:
                ser.close()
    elif data=='one':
        try:
            recv = ''
            print("recv" + recv)
            ser.write(recv.encode())
            time.sleep(0.05)
        except KeyboardInterrupt:
            if ser != None:
                ser.close()
    elif data=='two':
        try:
            recv = 'd'
            print("recv" + recv)
            ser_usb.write(recv.encode())
            time.sleep(0.05)
        except KeyboardInterrupt:
            if ser != None:
                ser.close()
    elif data=='three':
        try:
            recv = 's'
            print("recv" + recv)
            ser_usb.write(recv.encode())
            time.sleep(0.05)
        except KeyboardInterrupt:
            if ser != None:
                ser.close()
    elif data=='spray':
        try:
            recv = '4'
            print("recv" + recv)
            ser_usb.write(recv.encode())
            time.sleep(0.05)
        except KeyboardInterrupt:
            if ser_usb != None:
                ser_usb.close()
    elif data=='catch':
        try:
            recv = 'a'
            print("recv" + recv)
            ser_usb.write(recv.encode())
            time.sleep(0.05)
        except KeyboardInterrupt:
            if ser_usb != None:
                ser_usb.close()

    response = ser_usb.read_all()
    print(response)
    print('---' * 20)

@root.route('/data')
def data():
    """判断recv值是温度还是湿度"""
    return {"hum": random.randint(36, 38), "tem": random.randint(1, 100), "tim": time.strftime("%H:%M:%S")}

# 这个地址返回视频流响应
@root.route('/video_feed')
def video_feed():
    return Response(gen(VideoCamera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    time.sleep(5)
    root.run(host='192.168.43.63', port=8888)
