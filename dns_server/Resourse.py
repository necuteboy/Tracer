import time
from threading import Thread
from DNSServer import save, load

from dnslib import DNSRecord, QTYPE

class Resourse():
    def __init__(self, name):
        self.name = name
        self.NSA = None
        self.NS = None
        self.A = None
        self.AAAA = None
        self.PTR = None
        self.off = False

    def __hash__(self):
        return hash(self.name)

    def add_resourse(self, data: DNSRecord):
        if data.q.qtype == QTYPE.A:
            self.A = list(map(lambda x: x.rdata, data.rr))
            self.NSA = list(map(lambda x: (x.rname, x.rdata), data.ar))
            self.NS = list(map(lambda x: x.rdata, data.auth))
        elif data.q.qtype == QTYPE.AAAA:
            self.AAAA = list(map(lambda x: x.rdata, data.rr))
            self.NSA = list(map(lambda x: (x.rname, x.rdata), data.ar))
            self.NS = list(map(lambda x: x.rdata, data.auth))
        elif data.q.qtype == QTYPE.PTR:
            self.PTR = data.auth[0].rdata
        elif data.q.qtype == QTYPE.NS:
            self.NS = list(map(lambda x: x.rdata, data.rr))
            self.NSA = list(map(lambda x: (x.rname, x.rdata), data.ar))
        else:
            pass
        Thread(target=Resourse.removeRecourse, args=(self, data.q.qtype,
                                                     20)).start()

    @staticmethod
    def removeRecourse(self, qtype: QTYPE, ttl):
        time.sleep(ttl)
        qtypes = {
            QTYPE.A: [self.A, self.NSA, self.NS],
            QTYPE.AAAA: [self.AAAA, self.NSA, self.NS],
            QTYPE.PTR: [self.PTR],
            QTYPE.NS: [self.NS, self.NSA]
        }
        for item in qtypes[qtype]:
            item = None
        print(f'Убрал из кеша: {self.name}  {qtype}')
        save()
        print(f"Сохранил нынешний кеш")
        load()