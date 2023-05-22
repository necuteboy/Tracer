from threading import Thread
import pickle

import Resourse

from dnslib import *

DNS_PORT = 53
DNS_HOST = '127.0.0.1'
HOST_DNS = '8.26.56.26'
cash = {}
Alive = True
flag = False
default_ttl = 20


def save():
    with open("cash.pickle", "wb") as write_file:
        pickle.dump(cash, write_file)


def load():
    global cash, default_ttl
    with open("cash.pickle", "rb") as read_file:
        cash = pickle.load(read_file)


def sendReqDNS(dns_server, p):
    try:
        dns_server.send(p)
        p2, a2 = dns_server.recvfrom(1024)
        print('Отправил запрос своему днс серверу')

        return p2
    except:
        print('Днс сервер не отвечает')
        return


def startServer():
    global cash, Alive, flag, default_ttl
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as dns_server:
            server.bind((DNS_HOST, DNS_PORT))
            server.settimeout(10)
            dns_server.connect((HOST_DNS, DNS_PORT))
            dns_server.settimeout(10)
            print('Сервер запущен')
            while True:
                while Alive:
                    try:
                        client_req, client_addr = server.recvfrom(1024)
                        client_data = DNSRecord.parse(client_req)
                        print(f'Пришел запрос:{client_data.q.qname}  '
                              f'{client_data.q.qtype}')
                    except:
                        print('Не было запросов в течение 10 секунд')
                        continue
                    flag = True
                    if str(client_data.q.qname) in cash:
                        recourse: Resourse = cash.get(str(client_data.q.qname))
                        query = client_data.reply()
                        if client_data.q.qtype == QTYPE.A and recourse.A:
                            flag = False
                            for addr in recourse.A:
                                query.add_answer(
                                    dns.RR(rname=client_data.q.qname,
                                           rclass=client_data.q.qclass,
                                           rtype=QTYPE.A,
                                           ttl=default_ttl,
                                           rdata=A(addr.data)))
                            for ns in recourse.NS:
                                query.add_auth(
                                    dns.RR(rname=client_data.q.qname,
                                           rclass=client_data.q.qclass,
                                           rtype=QTYPE.NS,
                                           ttl=default_ttl,
                                           rdata=NS(ns.label)))
                            for ns, nsA in recourse.NSA:
                                if len(nsA.data) == 4:
                                    query.add_ar(dns.RR(rname=ns.label,
                                                        rclass=client_data.q.qclass,
                                                        rtype=QTYPE.A,
                                                        ttl=default_ttl,
                                                        rdata=A(nsA.data)))
                                elif len(nsA.data) == 16:
                                    query.add_ar(dns.RR(rname=ns.label,
                                                        rclass=client_data.q.qclass,
                                                        rtype=QTYPE.AAAA,
                                                        ttl=default_ttl,
                                                        rdata=AAAA(nsA.data)))

                        elif client_data.q.qtype == QTYPE.AAAA and recourse.AAAA:
                            flag = False
                            for addr in recourse.AAAA:
                                query.add_answer(
                                    dns.RR(rname=client_data.q.qname,
                                           rclass=client_data.q.qclass,
                                           rtype=QTYPE.AAAA,
                                           ttl=default_ttl,
                                           rdata=AAAA(addr.data)))
                            for ns in recourse.NS:
                                query.add_auth(
                                    dns.RR(rname=client_data.q.qname,
                                           rclass=client_data.q.qclass,
                                           rtype=QTYPE.NS,
                                           ttl=default_ttl,
                                           rdata=NS(ns.label)))
                            for ns, nsA in recourse.NSA:
                                if len(nsA.data) == 4:
                                    query.add_ar(dns.RR(rname=ns.label,
                                                        rclass=client_data.q.qclass,
                                                        rtype=QTYPE.A,
                                                        ttl=default_ttl,
                                                        rdata=A(nsA.data)))
                                elif len(nsA.data) == 16:
                                    query.add_ar(dns.RR(rname=ns.label,
                                                        rclass=client_data.q.qclass,
                                                        rtype=QTYPE.AAAA,
                                                        ttl=default_ttl,
                                                        rdata=AAAA(nsA.data)))

                        elif client_data.q.qtype == QTYPE.PTR and recourse.PTR:
                            flag = False
                            query.add_auth(dns.RR(rname=client_data.q.qname,
                                                  rclass=client_data.q.qclass,
                                                  rtype=QTYPE.SOA,
                                                  ttl=default_ttl,
                                                  rdata=recourse.PTR))
                        elif client_data.q.qtype == QTYPE.NS and recourse.NS:
                            flag = False
                            for ns in recourse.NS:
                                query.add_answer(
                                    dns.RR(rname=client_data.q.qname,
                                           rclass=client_data.q.qclass,
                                           rtype=QTYPE.NS,
                                           ttl=default_ttl,
                                           rdata=NS(ns.label)))
                            for ns, nsA in recourse.NSA:
                                if len(nsA.data) == 4:
                                    query.add_ar(dns.RR(rname=ns.label,
                                                        rclass=client_data.q.qclass,
                                                        rtype=QTYPE.A,
                                                        ttl=default_ttl,
                                                        rdata=A(nsA.data)))
                                elif len(nsA.data) == 16:
                                    query.add_ar(dns.RR(rname=ns.label,
                                                        rclass=client_data.q.qclass,
                                                        rtype=QTYPE.AAAA,
                                                        ttl=default_ttl,
                                                        rdata=AAAA(nsA.data)))

                        else:
                            server_packet = sendReqDNS(dns_server, client_req)
                            server_data: DNSRecord = DNSRecord.parse(
                                server_packet)
                            cash.get(str(client_data.q.qname)).add_resourse(
                                server_data)
                            print("Закешировал")
                            server.sendto(server_packet, client_addr)
                            print('Отправил ответ')
                            continue
                    if not cash.get(str(client_data.q.qname)):
                        server_packet = sendReqDNS(dns_server, client_req)
                        cash[str(client_data.q.qname)] = Resourse.Resourse(
                            str(client_data.q.qname))
                        server_data = DNSRecord.parse(server_packet)
                        cash[str(client_data.q.qname)].add_resourse(server_data)
                        print(f'Закешировал: {client_data.q.qname} {client_data.q.qtype}')
                        server.sendto(server_packet, client_addr)
                        print('Отправил ответ')
                    else:
                        server.sendto(query.pack(), client_addr)
                        print(f"Отправил закешированный пакет:  "
                              f"{client_data.q.qname}  {client_data.q.qtype}")
                save()
                cash = {}
                print('Сохранил кеш')
                print('Сервер выключен')
                while not Alive:
                    time.sleep(5)
                print('Сервер запущен')
                load()
                print('Загрузил сейв')


def main():
    global Alive
    Thread(target=startServer).start()
    while True:
        Alive = True
        while input() != 'q':
            continue
        Alive = False
        while input() != 's':
            continue


if __name__ == '__main__':
    main()
