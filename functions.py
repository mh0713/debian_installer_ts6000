import glob
import ipaddress
import os
import subprocess
import sys
import textwrap


def _proc_run(cmd):
    """
    :param cmd: str 実行するコマンド.
    :rtype: generator
    :return: 標準出力 (行毎).
    """
    proc = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )

    while True:
        line = proc.stdout.readline()
        if line:
            yield line

        if not line and proc.poll() is not None:
            break


def proc_run(cmd):
    for line in _proc_run(cmd):
        sys.stdout.write(line.decode("utf-8"))


def get_netifs():
    for entry in os.listdir("/sys/class/net"):
        if entry.startswith("en") or entry.startswith("eth"):
            yield entry


def delete_system_connection():
    for filename in glob.glob("/etc/NetworkManager/system-connections/*"):
        os.remove(filename)


def create_conf(template, args, conf_file):
    # import jinja2 here because jinja2 is not installed at installer starting
    from jinja2 import Template

    template = textwrap.dedent(template)[1:-1]

    conf = Template(template).render(args=args)

    try:
        if os.path.isfile(conf_file):
            os.remove(conf_file)
        with open(conf_file, "w") as f:
            f.write(conf)
        os.chmod(conf_file, 0o600)
    except Exception as e:
        print("failed to save configuration")
        raise e

    return True


def create_netplan(args, conf_file="/etc/netplan/99-default.yaml"):
    if args["ip"] == "dhcp":
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

    return create_conf(netplan_tpl, args, conf_file)


def apply_netplan(plan, conf="/etc/netplan/99-default.yaml"):
    proc_run("netplan apply")


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


def get_hostname():
    while True:
        hostname = input("hostname (proxy.example.org)> ")

        return hostname


def create_inventory(args, conf_file="./ansible/inventory/local.yml"):
    inventory_tpl = """
        all:
            hosts:
                localhost:
                    ansible_connection: local
                    ansible_host: localhost
                    hostname: {{ args["hostname"] }}
                    ip: {{ args["ip"] }}
    """

    return create_conf(inventory_tpl, args, conf_file)
