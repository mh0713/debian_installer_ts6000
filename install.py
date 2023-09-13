#!/usr/bin/env python3

import argparse
import os
import sys

import functions as func


def main():
    parser = argparse.ArgumentParser(description="Network Configuration Tool")
    parser.add_argument("--ip", default=None, help="IP address ex) 192.168.22.253/24")
    parser.add_argument("--gw", default=None, help="default gateway ex) 192.168.22.1")
    parser.add_argument(
        "--dns", default=None, nargs="*", help="DNS server ex) 8.8.8.8 8.8.4.4"
    )
    parser.add_argument(
        "--hostname", default=None, help="hostname ex) proxy.example.org"
    )
    args = parser.parse_args()

    if os.getuid() != 0:
        print("run as root")
        sys.exit(1)

    os.chdir(os.path.dirname(__file__))
    print(f"running in {os.getcwd()}")
    input("start ?")

    net_ifs = [netif for netif in func.get_netifs()]

    hostname = func.get_hostname() if args.hostname is None else args.hostname
    ip = func.get_ip() if args.ip is None else args.ip

    if ip == "dhcp":
        gw = None
        dns = None
    else:
        gw = func.get_gw() if args.gw is None else args.gw
        dns = func.get_dns() if args.dns is None else args.dns

    print(f"hostname: {hostname}")
    print(f"ip: {ip}")
    print(f"gateway: {gw}")
    print(f"dns: {dns}")

    print("* Updating apt database")
    func.proc_run("apt update")
    print("* Upgrading apt packages")
    func.proc_run(["apt -y upgrade"])
    print("* Installing required packages")
    func.proc_run(
        ["apt -y install ansible netplan.io python3-pip python3-passlib curl"]
    )

    print("* Deleting unnecessary files")
    func.delete_system_connection()
    print("* Genarating netplan configuration")
    netplan = func.create_netplan({"net_ifs": net_ifs, "ip": ip, "gw": gw, "dns": dns})
    print("* Genarating ansible inventory")
    func.create_inventory({"hostname": hostname, "ip": ip})

    print("* Configuration start")
    func.proc_run("ansible-playbook -i ansible/inventory/local.yml ansible/setup.yml")

    func.apply_netplan(netplan)
    print("* Configuration applied")


if __name__ == "__main__":
    main()
