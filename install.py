#!/usr/bin/env python3

import ipaddress
import os
import subprocess
import sys
import textwrap

def proc_run(cmd):
    proc = subprocess.run(cmd, capture_output=True)
    if proc.returncode != 0:
        print(proc.stderr.decode('utf-8'))
        sys.exit(1)
    
def get_netifs():
    for entry in os.listdir("/sys/class/net"):
        if entry in ["bonding_masters","lo"] or entry.startswith("br"):
            continue
        yield entry

def get_if(netif_role, net_ifs):
    while True:
        all_ifs = ", ".join(net_ifs)
        netif = input(f"{netif_role}を[{all_ifs}]から選択してください > ")
        if netif in net_ifs:
            return netif
        else:
            print(f"{netif} not in ${net_ifs}")

def get_mode():
    while True:
        mode = input("モードを選択してください [ブリッジ = b / リバースプロキシ = r] > ")
        if mode == "b":
            return "bridge"
        elif mode == "r":
            return "reverse"

def create_netplan(args):
    dns_text = ",".join([f'{str(d)}' for d in args["dns"]])

    if args["mode"] == "bridge":
        if args["ip"] == "dhcp":
            netplan = f"""
                network:
                    renderer: networkd
                    version: 2
                    ethernets:
                        {args["wan_if"]}:
                            dhcp4: no
                        {args["lan_if"]}:
                            dhcp4: no
                    bridges:
                        br0:
                            interfaces:
                                - {args["wan_if"]}
                                - {args["lan_if"]}
                            dhcp4: yes
            """
        else:
            netplan = f"""
                network:
                    renderer: networkd
                    version: 2
                    ethernets:
                        {args["wan_if"]}:
                            dhcp4: no
                        {args["lan_if"]}:
                            dhcp4: no
                    bridges:
                        br0:
                            interfaces:
                                - {args["wan_if"]}
                                - {args["lan_if"]}
                            dhcp4: no
                            addresses:
                                - {args["ip"]}
                            routes:
                                - to: default
                                  via: {args["dgw"]}
                            nameservers:
                                addresses: [{dns_text}]
            """
    else:
        if args["ip"] == "dhcp":
            netplan = f"""
                network:
                    renderer: networkd
                    version: 2
                    ethernets:
                        {args["lan_if"]}:
                            dhcp4: yes
            """
        else:
            netplan = f"""
                network:
                    renderer: networkd
                    version: 2
                    ethernets:
                        {args["lan_if"]}:
                            dhcp4: no
                            addresses:
                                - {args["ip"]}
                            routes:
                                - to: default
                                  via: {args["dgw"]}
                            nameservers:
                                addresses: [{dns_text}]
            """

    netplan = textwrap.dedent(netplan)[1:-1]

    return netplan

def apply_netplan(plan, conf="/etc/netplan/99-default.yaml"):
    try:
        with open(conf, "w") as f:
            f.write(plan)
            proc_run(["netplan","apply"])
    except Exception as e:
        print("ネットワーク設定の変更に失敗しました")
        print(e)
        return False

    return True
    

def get_ip():
    while True:
        ip = input("IPアドレス or dhcp (192.168.11.254/24 or dhcp)> ")
        if ip.lower().strip() == "dhcp":
            return "dhcp"
        else:
            try:
                return ipaddress.ip_interface(ip)
            except:
                print(f"IPアドレスの形式が不正です: {ip}")

def get_dgw():
    while True:
        dgw = input("デフォルトゲートウェイ (192.168.11.1)> ")
        try:
            return ipaddress.ip_address(dgw)
        except:
            print(f"デフォルトゲートウェイの形式が不正です: {dgw}")
    
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
    wan_if = dgw = None
    dns = []

    if os.getuid() != 0:
        print("root で実行してください")
        sys.exit(1)

    mode = get_mode()

    net_ifs = [netif for netif in get_netifs()]
    if len(net_ifs) == 0:
        print("ネットワークポートが見つかりません")
        sys.exit(1)
    if len(net_ifs) == 1 and mode == "reverse":
        input("ブリッジにはネットワークポートが２つ必要です")
        sys.exit(1)

    if mode == "bridge":
        wan_if = get_if("WANポート", net_ifs)
        net_ifs.remove(wan_if)

    lan_if = get_if("LANポート", net_ifs)

    ip = get_ip()
    if ip != "dhcp":
        dgw = get_dgw()
        dns = get_dns()

    print("■パッケージ情報の更新中")
    proc_run(["apt","update"])
    print("■パッケージのアップデート中")
    proc_run(["apt","-y","upgrade"])
    print("■必要なパッケージをインストール中")
    proc_run(["apt","-y","install","ansible","netplan.io"])

    print("■ネットワーク設定を変更中")
    netplan = create_netplan({"mode":mode, "wan_if":wan_if, "lan_if":lan_if, "ip":ip, "dgw":dgw, "dns":dns})
    apply_netplan(netplan)
    print("■設定が完了しました")
    
if __name__ == '__main__':
    main()