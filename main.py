import sys
import os
import re
import argparse
from urllib.request import urlopen
from prettytable import PrettyTable


class IPInfo:
    """ Class for getting information about IP addresses """

    # Regular expression for finding IP addresses
    regex_ip = re.compile("\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")
    # Regular expressions for finding AS, Country and Provider
    regex_as = re.compile("[Oo]riginA?S?: *([\d\w]+?)\n")
    regex_country = re.compile("[Cc]ountry: *([\w]+?)\n")
    regex_provider = re.compile("mnt-by: *([\w\d-]+?)\n")

    @staticmethod
    def trace(hostname: str):
        """ Get the list of IP addresses in the trace route """
        cmd_line = f"tracert {hostname}"
        p = os.popen(cmd_line)
        stdout = p.read()
        return IPInfo.regex_ip.findall(stdout)

    @staticmethod
    def parse(site, regex):
        """ Parse the website content and extract the desired information """
        try:
            result = regex.findall(site)
            return result[0]
        except:
            return ''

    @staticmethod
    def is_grey_ip(ip: str):
        """ Check if the IP address is considered grey """
        return ip.startswith('192.168.') or ip.startswith('10.') or (ip.startswith('172.') and 15 < int(ip.split('.')[1]) < 32)

    @staticmethod
    def info_ip(ip):
        """ Get information about the IP address """
        if IPInfo.is_grey_ip(ip):
            return ip, '', '', ''
        url = f"https://www.nic.ru/whois/?searchWord={ip}"
        try:
            with urlopen(url) as f:
                site = f.read().decode('utf-8')
                return ip, IPInfo.parse(site, IPInfo.regex_as), IPInfo.parse(site, IPInfo.regex_country), IPInfo.parse(site, IPInfo.regex_provider)
        except:
            return ip, '', '', ''


class TraceAS:
    """ Class for tracing the Autonomous Systems on a given route """

    def __init__(self):
        self.headers = ["№", "IP", "AS", "Страна", "Провайдер"]

    def run(self, hostname, save_file=None):
        """ Run the trace and print the results in a table """
        ips = IPInfo.trace(hostname)
        self.make_table(ips, save_file=save_file)

    def make_table(self, ips, save_file=None):
        """ Create a table with the trace results """
        td_data = []
        row_index = 0
        for ip in ips:
            info = IPInfo.info_ip(ip)
            td_data.append(row_index)
            td_data.extend(info)
            row_index += 1
        table = PrettyTable(self.headers)
        columns = len(self.headers)
        while td_data:
            table.add_row(td_data[:columns])
            td_data = td_data[columns:]
        table_str = str(table)
        print(table_str)
        if save_file:
            with open(save_file, 'w') as f:
                f.write(table_str)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('name',type=str,help='domain name or ip address ')
    args = parser.parse_args()
    trace_as = TraceAS()
    trace_as.run(args.name,save_file='table.txt')