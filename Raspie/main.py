# !/usr/bin/env python
# _*_ coding: utf-8 _*_
from flask import render_template, Flask, request, Response
import cv2
import random
import serial
import time


ser = serial.Serial("/dev/ttyAMA0", 115200)

if not ser.isOpen():
    print("open failed!!!")

else:
    print("open success: ")
    print(ser)


class VideoCamera(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0)

    def __del__(self):
        self.video.release()

    def get_frame(self):
        success, image = self.video.read()
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

@root.post('/cmd')
def cmd():
    data = request.get_data().decode()
    if data == 'up':
        try:
            recv = '$DGT:59-62,0!'
            print("recv" + recv)
            ser.write(recv.encode())
            time.sleep(0.05)
        except KeyboardInterrupt:
            if ser != None:
                ser.close()

    el

@root.route('/data')
def data():
    try:
        count = ser.inWaiting()
        if count > 0:
            recv = ser.read(count)
            print("recv: " + recv)
            """判断recv值是温度还是湿度"""
            return {"hum": random.randint(36, 38), "tem": random.randint(1, 100), "tim": time.strftime("%H:%M:%S")}
    except KeyboardInterrupt:
        if ser != None:
            ser.close()

# 这个地址返回视频流响应
@root.route('/video_feed')
def video_feed():
    return Response(gen(VideoCamera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    root.run(host='192.168.31.75', port=8888)
# 192.168.31.75
