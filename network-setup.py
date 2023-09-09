#!/usr/bin/env python3

import argparse
import glob
import ipaddress
import os
import subprocess
import sys
import textwrap


def proc_run(cmd):
    proc = subprocess.run(cmd, capture_output=True)
    if proc.returncode != 0:
        print(proc.stderr.decode("utf-8"))
        sys.exit(1)


def get_netifs():
    for entry in os.listdir("/sys/class/net"):
        if entry.startswith("en") or entry.startswith("eth"):
            yield entry

def delete_system_connection():
    for filename in  glob.glob("/etc/NetworkManager/system-connections/*"):
        os.remove(filename)

def create_netplan(args, conf="/etc/netplan/99-default.yaml"):
    from jinja2 import Template

    if args["ip"] == "dhcp":
        netplan_tpl = """
            network:
                renderer: NetworkManager
                version: 2
                ethernets:
                {%- for net_if in args["net_ifs"] %}
                    - {{ net_if }}:
                        dhcp4: no
                {%- endfor %}
                bridges:
                    br0:
                        interfaces:
                        {%- for net_if in args["net_ifs"] %}
                            - {{ net_if }}
                        {%- endfor %}
                        dhcp4: yes
        """
    else:
        netplan_tpl = """
            network:
                renderer: NetworkManager
                version: 2
                ethernets:
                {%- for net_if in args["net_ifs"] %}
                    {{ net_if }}:
                        dhcp4: no
                {%- endfor %}
                bridges:
                    br0:
                        interfaces:
                        {%- for net_if in args["net_ifs"] %}
                            - {{ net_if }}
                        {%- endfor %}
                        dhcp4: no
                        addresses:
                            - {{args["ip"]}}
                        routes:
                            - to: default
                              via: {{args["gw"]}}
                        nameservers:
                            addresses:
                            {%- for dns in args["dns"] %}
                                - {{ dns }}
                            {%- endfor %}
        """

    netplan_tpl = textwrap.dedent(netplan_tpl)[1:-1]

    netplan = Template(netplan_tpl).render(args=args)

    try:
        with open(conf, "w") as f:
            f.write(netplan)
    except Exception as e:
        print("ネットワーク設定の保存に失敗しました")
        print(e)
        return False

    return True


def apply_netplan(plan, conf="/etc/netplan/99-default.yaml"):
    proc_run(["netplan", "apply"])


def get_ip():
    while True:
        ip = input("IP address (192.168.11.254/24)> ")
        try:
            return ipaddress.ip_interface(ip)
        except:
            print(f"Invalid IP address format: {ip}")


def get_gw():
    while True:
        gw = input("default gateway (192.168.11.1)> ")
        try:
            return ipaddress.ip_address(gw)
        except:
            print(f"Invalid gateway format: {gw}")


def get_dns():
    while True:
        dns = input("DNS server(192.168.11.252 192.168.11.253)> ")
        dns = dns.split()
        try:
            ret_dns = []
            for d in dns:
                ret_dns.append(ipaddress.ip_address(d))
            return ret_dns

        except Exception as e:
            print(e)
            print(f"Invalid DNS server: {d}")


def main():
    parser = argparse.ArgumentParser(description="Network Configuration Tool")
    parser.add_argument('--ip', default=None, help='IP address ex) 192.168.22.253/24')
    parser.add_argument('--gw', default=None, help='default gateway ex) 192.168.22.1')
    parser.add_argument('--dns', default=None, nargs='*', help='DNS server ex) 8.8.8.8 8.8.4.4')
    args = parser.parse_args()

    if os.getuid() != 0:
        print("run as root")
        sys.exit(1)

    net_ifs = [netif for netif in get_netifs()]

    ip = get_ip() if args.ip is None else args.ip
    gw = get_gw() if args.gw is None else args.gw
    dns = get_dns() if args.dns is None else args.dns

    print("* Updating apt database")
    proc_run(["apt", "update"])
    print("* Upgrading apt packages")
    proc_run(["apt", "-y", "upgrade"])
    print("* Installing required packages")
    proc_run(["apt", "-y", "install", "ansible", "netplan.io", "python3-pip", "python3-passlib","curl"])

    print("* Deleting unnecessary files")
    delete_system_connection()
    print("* Genarating netplan configuration")
    netplan = create_netplan({"net_ifs": net_ifs, "ip": ip, "gw": gw, "dns": dns})
    # print(netplan)
    apply_netplan(netplan)
    print("* Configuration applied")
    print("\n\nInstallation command")
    print("ansible-playbook -i ansible/inventory/local.yml ansible/setup.yml")

if __name__ == "__main__":
    main()
