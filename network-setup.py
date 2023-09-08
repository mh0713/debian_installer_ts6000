#!/usr/bin/env python3

import argparse
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
        ip = input("IPアドレス(192.168.11.254/24)> ")
        try:
            return ipaddress.ip_interface(ip)
        except:
            print(f"IPアドレスの形式が不正です: {ip}")


def get_gw():
    while True:
        gw = input("デフォルトゲートウェイ (192.168.11.1)> ")
        try:
            return ipaddress.ip_address(gw)
        except:
            print(f"デフォルトゲートウェイの形式が不正です: {gw}")


def get_dns():
    while True:
        dns = input("DNSサーバー(192.168.11.252 192.168.11.253)> ")
        dns = dns.split()
        try:
            ret_dns = []
            for d in dns:
                ret_dns.append(ipaddress.ip_address(d))
            return ret_dns

        except Exception as e:
            print(e)
            print(f"DNSの形式が不正です: {d}")


def main():
    parser = argparse.ArgumentParser(description="cacheサーバーネットワーク設定ツール")
    parser.add_argument('--ip', default=None, help='IPアドレス ex) 192.168.22.253/24')
    parser.add_argument('--gw', default=None, help='デフォルトゲートウェイ ex) 192.168.22.1')
    parser.add_argument('--dns', default=None, nargs='*', help='DNSサーバー ex) 8.8.8.8 8.8.4.4')
    args = parser.parse_args()

    if os.getuid() != 0:
        print("root で実行してください")
        sys.exit(1)

    net_ifs = [netif for netif in get_netifs()]

    ip = get_ip() if args.ip is None else args.ip
    gw = get_gw() if args.gw is None else args.gw
    dns = get_dns() if args.dns is None else args.dns

    print("■パッケージ情報の更新中")
    proc_run(["apt", "update"])
    print("■パッケージのアップデート中")
    proc_run(["apt", "-y", "upgrade"])
    print("■必要なパッケージをインストール中")
    proc_run(["apt", "-y", "install", "ansible", "netplan.io", "python3-pip", "python3-passlib","curl"])

    print("■ネットワーク設定を変更中")
    netplan = create_netplan({"net_ifs": net_ifs, "ip": ip, "gw": gw, "dns": dns})
    # print(netplan)
    apply_netplan(netplan)
    print("■設定が完了しました")
    print("\n\nインストール方法")
    print("ansible-playbook -i ansible/inventory/local.yml ansible/setup.yml")


if __name__ == "__main__":
    main()
