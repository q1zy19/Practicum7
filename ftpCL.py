#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import socket,re, os, random
from CIPHERS import Ciphers
PORT = 9090
from pathlib import Path
HOST = 'localhost'
CURR_DIR = "\\"
sock = ''
MAIN_DIR = Path(os.getcwd(), 'system_home')

def msg_user(login, password, CURR_DIR, msg, c = 0):
    return f"{login}=login, {password}=password, {CURR_DIR}=curr_dir, {c}=len, {msg}=message".encode()

def _send(login, password, CURR_DIR, req):
    global sock
    name = re.split("[ \\/]+", req)[-1]
    curr_path_file = Path(MAIN_DIR, name)
    sock.send_s(f'send {name}'.encode())
    with open(curr_path_file, 'r') as file:
        text = file.read()
    print(text.encode())
    sock.send_s(msg_user(login, password, CURR_DIR, text.encode(), len(text)))
    return


def _res(req):
    global sock, f1, f2, MAIN_DIR, CURR_DIR
    flag_finder = sock.recv_s(1024)
    name = re.split("[ \\/]+", req)[-1]
    print(name)
    length = sock.recv(1024).decode()
    text = sock.recv(len(length)).decode()
    curr_path_file = Path(MAIN_DIR, name)
    with open(curr_path_file, 'w') as file:
        file.write(text)
    return
def send_s(sock, data):
    global key_low
    data = data.decode()
    C_k = Ciphers()
    data = C_k.encrypt(key_low, data)
    data = data.encode()
    sock.send(data)

def recv_s(sock, vol):
    global key_low
    data = sock.recv(vol).decode()
    C_k = Ciphers()
    data = C_k.decrypt(key_low, data)
    data = data.encode()
    return data

def getting_keys(sock):
    server_keys = sock.recv(1024).decode().split("|")
    server_keys = [int(item) for item in server_keys]
    f1 = random.randint(100, 999)
    f2 = server_keys[0]
    f3 = server_keys[1]
    new_k = pow(f2, f1) % f3
    sock.send(str(new_k).encode())
    serv_a = server_keys[2]
    private = pow(serv_a, f1) % f3
    return private

def main():
    global sock, key_low
    login = input("Введите логин: ")
    password = input("Введите пароль: ")
    CURR_DIR = login
    print(f"Присоединились к {HOST} {PORT}")
    print('help - список команд, exit - выход')
    socket.socket.send_s = send_s
    socket.socket.recv_s = recv_s
    while True:
        req = input(CURR_DIR+'$')
        req = req.strip()
        if req == 'exit':
            break
        sock = socket.socket()
        sock.connect((HOST, PORT))
        key_low = getting_keys(sock)
        if req.find("send_from") == 0:
            if req == "send_":
                print("Нет файла")
            else:
                _send(login, password, CURR_DIR, req)
        else:
            sock.send_s(msg_user(login, password, CURR_DIR, req))
            if req.find("get_to") == 0 or req == "get_to":
                _res(req)
            else:
                response = sock.recv_s(1024).decode()
                if req.find("cd") == 0:
                    if ".." in req:
                        CURR_DIR = login
                    else:
                        CURR_DIR = response[response.find("\\", response.find(login)):]
                else:
                    print(response)

if __name__ == '__main__':
    main()

