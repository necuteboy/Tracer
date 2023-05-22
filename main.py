import os
import re
import argparse
from ipwhois import IPWhois
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
        print(2)
        """ Get the list of IP addresses in the trace route """
        cmd_line = f"tracert {hostname}"
        p = os.popen(cmd_line)
        stdout = p.read()
        return IPInfo.regex_ip.findall(stdout)

    @staticmethod
    def is_grey_ip(ip: str):
        """ Check if the IP address is considered grey """
        return ip.startswith('192.168.') or ip.startswith('10.') or (ip.startswith('172.') and 15 < int(ip.split('.')[1]) < 32)

    @staticmethod
    def info_ip(ip):
        print(1)
        """ Get information about the IP address """
        if IPInfo.is_grey_ip(ip):
            return ip, '', '', ''
        try:
            ipwhois_data = IPWhois(ip).lookup_rdap()
            return ip, ipwhois_data['asn'], ipwhois_data['asn_country_code'], ipwhois_data['network']['name']
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
        table = PrettyTable(["№", "IP", "AS Name", "Country", "Provider"])
        for i, ip in enumerate(ips):
            info = IPInfo.info_ip(ip)
            table.add_row([i, *info])

        print(table)
        if save_file:
            with open(save_file, 'w') as f:
                f.write(str(table))
        return table

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('name',type=str,help='domain name or ip address ')
    args = parser.parse_args()
    trace_as = TraceAS()
    trace_as.run(args.name,save_file='table.txt')