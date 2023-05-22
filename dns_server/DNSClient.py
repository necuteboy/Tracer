from socket import *
from dnslib import *

SERVER_PORT = 53
SERVER_HOST = '127.0.0.1'

# Устанавливаем соединение с сервером
with socket.socket(socket.AF_INET, SOCK_DGRAM) as client_socket:
    client_socket.connect((SERVER_HOST, SERVER_PORT))

    # Запрашиваем у пользователя имя доменного имени и тип запроса
    user_input = input("Введите доменное имя и тип запроса (A, AAAA, NS, PTR): ")

    # Обрабатываем запросы до тех пор, пока пользователь не введет 'q'
    while user_input != 'q':
        input_list = user_input.split(' ')
        dns_request = 0

        # Определяем запроса
        if len(input_list) > 1:
            if input_list[1] == "A":
                dns_request = DNSRecord(q=DNSQuestion(input_list[0], QTYPE.A))
            elif input_list[1] == "AAAA":
                dns_request = DNSRecord(q=DNSQuestion(input_list[0], QTYPE.AAAA))
            elif input_list[1] == "NS":
                dns_request = DNSRecord(q=DNSQuestion(input_list[0], QTYPE.NS))
            elif input_list[1] == "PTR":
                dns_request = DNSRecord(q=DNSQuestion(input_list[0], QTYPE.PTR))
            else:
                print("Неверный тип запроса")
                user_input = input("Введите доменное имя и тип запроса (A, AAAA, NS, PTR): ")
                continue
        elif len(input_list) == 1:
            dns_request = DNSRecord(q=DNSQuestion(input_list[0], QTYPE.A))
        else:
            print("Неверный тип запроса")
            user_input = input("Введите доменное имя и тип запроса (A, AAAA, NS, PTR): ")
            continue

        # Отправляем DNS-запрос на сервер и получаем ответ
        client_socket.send(dns_request.pack())
        response, server_address = client_socket.recvfrom(1024)

        # Выводим ответ на экран
        print(DNSRecord.parse(response))

        # Запрашиваем новый ввод у пользователя
        user_input = input("Введите доменное имя и тип запроса (A, AAAA, NS, PTR): ")

    # Закрываем соединение
    client_socket.close()
