import argparse
import os
import socket
import threading
import time
from collections import deque

import cv2
import imutils

os.chdir(os.path.dirname(__file__))

# telloへのアクセス用
tello_ip = '192.168.10.1'
tello_port = 8889
tello_address = (tello_ip, tello_port)

# telloからの受信用
VS_UDP_IP = '0.0.0.0'
VS_UDP_PORT = 11111

# VideoCapture用のオブジェクト準備
cap = None
# データ受信用のオブジェクト準備
response = None

# 通信用のソケットを作成
# ※アドレスファミリ：AF_INET（IPv4）、ソケットタイプ：SOCK_DGRAM（UDP）
socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# リッスン状態にする
socket.bind(('', tello_port))


# データ受け取り用の関数
def run_udp_receiver():
    while True:
        try:
            response, _ = socket.recvfrom(1024)
        except Exception as e:
            print(e)
            break


thread = threading.Thread(target=run_udp_receiver, args=())
thread.daemon = True
thread.start()

# コマンドモードを使うため'command'というテキストを投げる
socket.sendto('command'.encode('utf-8'), tello_address)

# 離陸
# socket.sendto('takeoff'.encode('utf-8'), tello_address)
socket.sendto('speed 50'.encode('utf-8'), tello_address)
# time.sleep(5)
# socket.sendto('cw 360'.encode('utf-8'), tello_address)
# time.sleep(5)
# socket.sendto('down 50'.encode('utf-8'), tello_address)
# time.sleep(5)
# socket.sendto('speed 10'.encode('utf-8'), tello_address)


# ビデオストリーミング開始
socket.sendto('streamon'.encode('utf-8'), tello_address)
udp_video_address = 'udp://@' + VS_UDP_IP + ':' + str(VS_UDP_PORT)
if cap is None:
   cap = cv2.VideoCapture(1)
#    cap = cv2.VideoCapture(udp_video_address)
if not cap.isOpened():
    cap.open(udp_video_address)

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video",
                help="path to the (optional) video file")
ap.add_argument("-b", "--buffer", type=int, default=64,
                help="max buffer size")
args = vars(ap.parse_args())
# list of tracked points
greenLower = (30, 50, 50)
greenUpper = (80, 255, 255)
xoffset = 0
yoffset = 0
xradius = 0
pts = deque(maxlen=args["buffer"])
socket.sendto('speed 2'.encode('utf-8'), tello_address)

# cap = cv2.VideoCapture(0)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
size = (width, height)
print(size)
frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
print(frame_count)
# frame_count = 600  # 6000/30=200=3分20秒
# フレームレート(1フレームの時間単位はミリ秒)の取得
frame_rate = int(cap.get(cv2.CAP_PROP_FPS))
print(frame_rate)

# 保存用
fps = 30
size = (960, 720)
frame_count = 3
fourcc = cv2.VideoWriter_fourcc(*'h264')
video = cv2.VideoWriter('./output/Test_ green.mp4', fourcc, fps, size, True)
midx = int(width / 2)
midy = int(height / 2)
font = cv2.FONT_HERSHEY_SIMPLEX

i = 0
while (cap.isOpened()):
    ret, frame = cap.read()
    frame = cv2.resize(frame, dsize=(960, 720))
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, greenLower, greenUpper)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    center = None
    if len(cnts) > 0 and i % 4 == 0:
        c = max(cnts, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        xradius = int(radius)
        M = cv2.moments(c)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
        # only proceed if the radius meets a minimum size
        xoffset = int(center[0] - midx)
        yoffset = int(midy - center[1])

        #   if 450 > xoffset > 150 and -150 < yoffset < 150:
        if 450 > xoffset > 100:
            socket.sendto('right 30'.encode('utf-8'), tello_address)

        #   elif -450 < xoffset < -150 and -150 < yoffset < 150:
        elif -450 < xoffset < -100:
            socket.sendto('left 30'.encode('utf-8'), tello_address)
        elif 350 > yoffset > 100 and -100 < xoffset < 100:
            #    socket.sendto('speed 5'.encode('utf-8'), tello_address)
            socket.sendto('up 40'.encode('utf-8'), tello_address)
        elif -350 < yoffset < -100 and -100 < xoffset < 100:
            socket.sendto('down 30'.encode('utf-8'), tello_address)
        elif xradius > 50:
            # elif -100 < yoffset < 0 and -100 < xoffset < 100:
            socket.sendto('back 50'.encode('utf-8'), tello_address)
        elif xradius < 20:
            # elif 0 < yoffset < 100 and -100 < xoffset < 100:
            socket.sendto('forward 40'.encode('utf-8'), tello_address)
        else:
            socket.sendto('stop'.encode('utf-8'), tello_address)

        if radius > 10:
            cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)
            cv2.circle(frame, center, 5, (0, 0, 255), -1)
    i = i + 1
    if i % 1 == 0:
        cv2.putText(frame, "X-offset: " + str(xoffset), (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.25, (0, 255, 255), 4)
        cv2.putText(frame, "Y-offset: " + str(yoffset), (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 1.25, (0, 255, 255), 4)
        cv2.putText(frame, "o-radius: " + str(xradius), (10, 190), cv2.FONT_HERSHEY_SIMPLEX, 1.25, (0, 255, 255), 4)
        cv2.rectangle(frame, (0, 210), (960, 510), (255, 255, 255), thickness=8, lineType=cv2.LINE_4)
        cv2.line(frame, (0, 360), (960, 360), (0, 0, 0), thickness=1, lineType=cv2.LINE_4)
        cv2.rectangle(frame, (330, 0), (630, 960), (255, 255, 255), thickness=8, lineType=cv2.LINE_4)

        cv2.imshow("Frame", frame)
        video.write(frame)  # escを押したら終了。
    if cv2.waitKey(1) & 0xFF == 27:
        break

socket.sendto('land'.encode('utf-8'), tello_address)
socket.sendto('streamoff'.encode('utf-8'), tello_address)
cv2.destroyWindow("Frame")
cap.release()
video.release()
time.sleep(10)

import cv2
import os

os.chdir(os.path.dirname(__file__))

cap = cv2.VideoCapture('./output/Test_ green.mp4')
fps = 3
size = (960, 720)
fourcc = cv2.VideoWriter_fourcc(*'H264')
video = cv2.VideoWriter('./output/output_Test_ green.mp4', fourcc, fps, size, True)

while (cap.isOpened()):
    ret, frame = cap.read()
    if ret == True:
        cv2.imshow('New', frame)
        video.write(frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        break

# 終了処理
cap.release()
video.release()
cv2.destroyAllWindows()
