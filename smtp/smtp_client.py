#!/usr/bin/env python3

import configparser
import socket
from ssl import wrap_socket
from base64 import b64encode


# Чтение конфигурационного файла
config = configparser.ConfigParser(allow_no_value=True)
with open('./conf/config.cfg', 'r', encoding='utf-8') as f:
    config.read_file(f)

# Получение параметров из конфигурационного файла
msg_params = config['MESSAGE']
acc_params = config['ACCOUNT']
login = acc_params['Login']
password = acc_params['Password'].encode()
receivers = ','.join(config['RECEIVERS'])
subject = msg_params['Subject']
with open(msg_params['Text'], 'r', encoding='cp1251') as f:
    text = f.read()

# Обработка текста сообщения
if text[0] == '.':
    text = '.' + text
text = text.replace("\n.", "\n..")

# Создание частей сообщения
boundary = msg_params['Boundary']
attachments = ''
for attachment in msg_params['Attachments'].split('\n')[1:]:
    attachment = attachment.split(',')
    filename = attachment[0].strip()
    mime_type = attachment[1].strip()
    with open(filename, 'rb') as f:
        filename = filename.replace("./conf/", "")
        file = b64encode(f.read())
        attachments += (
            f'Content-Disposition: attachment; filename="{filename}"\n'
            'Content-Transfer-Encoding: base64\n'
            f'Content-Type: {mime_type}; name="{filename}"\n\n'
        ) + file.decode() + f'\n--{boundary}'

if not all(ord(i) <128 for i in subject):
    subject = f'=?utf-8?B?{b64encode(subject.encode()).decode()}?='

# Формирование сообщения
message = (
    f"From: {login}\n"
    f"To: {receivers}\n"
    f"Subject: {subject}\n"
    "MIME-Version: 1.0\n"
    f'Content-Type: multipart/mixed; boundary="{boundary}"\n\n'
    f"--{boundary}\n"
    "Content-Type: text/plain; charset=utf-8\n"
    "Content-Transfer-Encoding: 8bit\n\n"
    f"{text}\n"
    f"--{boundary}\n"
    f"{attachments}--\n."
)

# Отправка запросов к серверу
def send_request(sock, cmd, buffer_size=1024):
    sock.send(cmd + b'\n')
    return sock.recv(buffer_size).decode()

# Отправка письма
if __name__ == "__main__":
    login = login.encode()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock = wrap_socket(sock)
        server_params = config['SERVER']
        sock.settimeout(float(server_params['Timeout']))
        sock.connect((server_params['Address'], int(server_params['Port'])))
        print(send_request(sock, b'EHLO test'))
        print(send_request(sock, b'AUTH LOGIN'))
        print(send_request(sock, b64encode(login)))
        print(send_request(sock, b64encode(password)))
        print(send_request(sock, b'MAIL FROM: ' + login))
        for recipient in config['RECEIVERS']:
            print(send_request(sock, b'RCPT TO: ' + recipient.encode()))
        # Посылаем самое сообщение
        print(send_request(sock, b'DATA'))
        print(send_request(sock, message.encode()))
        print('Message sent')
