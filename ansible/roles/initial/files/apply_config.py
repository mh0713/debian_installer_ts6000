#!/usr/bin/env python3

import argparse
import json
import random
import shutil
import subprocess
import time
from pathlib import Path

import ruamel.yaml

yaml = ruamel.yaml.YAML()
yaml.indent(sequence=4, offset=2)


def generate_nginx_cert(
    conf: dict,
    ca_dir: Path = Path("/etc/nginx/ssl/ca/"),
    cert_dir: Path = Path("/etc/nginx/ssl/"),
) -> None:
    OPENSSL_BIN = "openssl"
    ca_crt: Path = ca_dir / "ca.crt"
    ca_key: Path = ca_dir / "ca.key"
    for target_name, target_conf in conf["proxy-cache"]["targets"].items():
        target_name: str = target_name
        if len(target_conf["domains"]) <= 0:
            continue
        first_domain = target_conf["domains"][0]
        out_key = cert_dir / f"{target_name}.key"
        out_csr = cert_dir / f"{target_name}.csr"
        out_san = cert_dir / f"{target_name}.san"
        out_crt = cert_dir / f"{target_name}.crt"
        # 秘密鍵を作成
        subprocess.run([OPENSSL_BIN, "genrsa", "-out", str(out_key), "2048"])
        # CSRを作成
        subprocess.run(
            [
                OPENSSL_BIN,
                "req",
                "-out",
                str(out_csr),
                "-key",
                str(out_key),
                "-new",
                "-subj",
                f"/C=JP/ST=Aichi/L=Nagoya/O=Buffalo Inc./CN={first_domain}",
            ]
        )
        out_san.write_text("subjectAltName = " +
                           ", ".join(f"DNS:{d}" for d in target_conf["domains"]))
        # 証明書を作成
        subprocess.run(
            [
                OPENSSL_BIN,
                "x509",
                "-req",
                "-days",
                "3650",
                "-CA",
                str(ca_crt),
                "-CAkey",
                str(ca_key),
                "-CAcreateserial",
                "-in",
                str(out_csr),
                "-out",
                str(out_crt),
                "-extfile",
                str(out_san),
            ]
        )


def generate_nginx_sites(
    conf: dict,
    sites_dir: Path = Path("/etc/nginx/sites-cache/"),
    cert_dir: Path = Path("/etc/nginx/ssl/"),
    log_dir: Path = Path("/var/log/nginx/"),
) -> None:
    # 既存の設定を削除
    for file in sites_dir.iterdir():
        if file.is_file():
            file.unlink()
    # 新しい設定を作成
    for target_name, target_conf in conf["proxy-cache"]["targets"].items():
        target_name: str = target_name

        # 新しい設定を作成
        lines: list[str] = [
            "server {",
        ]
        if "http" in target_conf["schemes"]:
            lines += [
                "    listen 80;",
            ]
        if "https" in target_conf["schemes"]:
            lines += [
                "    listen 443 ssl;",
            ]
        log_path = log_dir / target_name / "access.log"
        log_ltsv_path = log_dir / target_name / "access.ltsv"
        crt_path = cert_dir / f"{target_name}.crt"
        key_path = cert_dir / f"{target_name}.key"
        proxy_ssl_ciphers = ["HIGH", "!aNULL", "!MD5"]
        if "proxy-ssl-ciphers" in target_conf:
            proxy_ssl_ciphers += [c for c in target_conf["proxy-ssl-ciphers"]
                                  if c not in proxy_ssl_ciphers]
        lines += [
            f"    server_name {' '.join(target_conf['domains'])};",
            f"    access_log {log_path} main;",
            f"    access_log {log_ltsv_path} ltsv;",
            "    proxy_http_version 1.1;",
            "    proxy_set_header X-Real-IP $remote_addr;",
            "    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;",
            "    proxy_set_header Host $host;",
            "    proxy_set_header Connection '';",
            "    proxy_read_timeout 2m;",
            "    proxy_connect_timeout 2m;",
            "    proxy_send_timeout 2m;",
            f"    proxy_ssl_ciphers {':'.join(proxy_ssl_ciphers)};",
            f"    ssl_certificate {crt_path};",
            f"    ssl_certificate_key {key_path};",
            "    ssl_session_cache shared:SSL:10m;",
            "    ssl_session_timeout 5m;",
            "    ssl_ciphers  HIGH:!aNULL:!MD5;",
            "    ssl_prefer_server_ciphers on;",
        ]
        for location_conf in target_conf["locations"]:
            path: str = location_conf["path"]
            cache_enable: bool = location_conf["cache"]["enable"]
            cache_valid: str = location_conf["cache"].get("valid", "23h")
            cache_extensions: list[str] = location_conf["cache"].get(
                "extensions")
            ignore_cache_control: list[str] = location_conf["cache"].get(
                "ignore-cache-control", False)

            lines += [
                f"    location {path} {{",
                "        proxy_pass $scheme://$host;",
                "        proxy_set_header Host $host;",
                "        proxy_ssl_server_name on;",
                "        proxy_ssl_name $host;",
            ]
            if cache_enable:
                if cache_extensions:
                    lines += [
                        "        set $do_not_cache 1;",
                        f"        if ($uri ~* '\\.({'|'.join(cache_extensions)})$') {{",
                        "            set $do_not_cache 0;",
                        "        }",
                        "        proxy_no_cache $do_not_cache;",
                        "        proxy_cache_bypass $do_not_cache;",
                    ]
                else:
                    lines += [
                        "        proxy_no_cache 0;",
                        "        proxy_cache_bypass 0;",
                    ]
                if ignore_cache_control:
                    lines += [
                        "        proxy_ignore_headers Cache-Control;",
                    ]
                lines += [
                    "        proxy_cache cache_buffalo;",
                    "        proxy_cache_key $scheme://$host$request_uri;",
                    "        proxy_cache_revalidate on;",
                    f"        proxy_cache_valid 200 {cache_valid};",
                    "        proxy_cache_valid any 0s;",
                    "        add_header X-Cache-Status $upstream_cache_status;",
                ]
            lines += [
                "    }",
            ]
        lines += [
            "}",
        ]
        (sites_dir / target_name).write_text("\n".join(lines) + "\n", encoding="utf-8")


def make_nginx_log_dir(conf: dict, log_dir: Path = Path("/var/log/nginx/")) -> None:
    for target_name, target_conf in conf["proxy-cache"]["targets"].items():
        target_name: str = target_name
        (log_dir / target_name).mkdir(mode=0o755, parents=True, exist_ok=True)


def generate_dnsmasq_hosts(
    conf: dict,
    dnsmasq_hosts: Path = Path("/etc/hosts-dnsmasq"),
    dnsmasq_inline_hosts: Path = Path("/etc/hosts-dnsmasq-inline.template"),
) -> None:
    lines: list[str] = []
    lines_inline: list[str] = []
    if conf["proxy-cache"]["enable"]:
        for target_name, target_conf in conf["proxy-cache"]["targets"].items():
            target_name: str = target_name
            lines += [f"{a} {d}" for d in target_conf["domains"]
                      for a in addresses]
            lines_inline += [f"<IP> {d}" for d in target_conf["domains"]]
    dnsmasq_hosts.write_text("\n".join(lines) + "\n", encoding="utf-8")
    dnsmasq_inline_hosts.write_text(
        "\n".join(lines_inline) + "\n", encoding="utf-8")


if __name__ == "__main__":
    # 引数の処理
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-restart", dest="restart",
                        action="store_const", const=False, default=True)
    args = parser.parse_args()

    # 読み取り
    CONFIG_FILE = Path("/etc/melco/proxy-server.yaml")
    config = yaml.load(CONFIG_FILE.read_text(encoding="utf-8"))

    # 設定
    print("Generating...")
    generate_dnsmasq_hosts(config)
    generate_nginx_cert(config)
    make_nginx_log_dir(config)
    generate_nginx_sites(config)

    # 再起動
    if args.restart:
        print("Reloading nginx...")
        subprocess.run(["systemctl", "reload", "nginx"])
        time.sleep(1)
        print("Reloading NetworkManager...")
        subprocess.run(["systemctl", "reload", "NetworkManager"])
        time.sleep(1)
        print("Reloading dnsmasq...")
        subprocess.run(["systemctl", "reload", "dnsmasq"])
        subprocess.run(["/usr/local/bin/update-hosts-inline"])
        print("Updating iptables...")
        subprocess.run(["/usr/local/bin/update-redirect-rules"])
        time.sleep(1)
        print("Enabling ufw...")
        subprocess.run(["ufw", "--force", "enable"])

    print("Done.")
