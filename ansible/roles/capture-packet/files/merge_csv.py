#!/usr/bin/env python3

import argparse
import glob
import os
import re
import sys

import pandas as pd

output_columns = [
    "hostname",
    "logdatetime",
    "application_category_name",
    "application_name",
    "requested_server_name",
    "bidirectional_bytes",
    "src2dst_bytes",
    "dst2src_bytes",
    "src_ip",
    "dst_ip",
]

parser = argparse.ArgumentParser(
    prog="pcap2csv", description="PCAP parser", add_help=True
)

parser.add_argument("-i", "--input", default="csv_temp/")
parser.add_argument("-o", "--output", default="csv_merged/")
parser.add_argument("-p", "--prefix", required=True)

args = parser.parse_args()

input_dir = args.input
output_dir = args.output
prefix = args.prefix

first = True
for fpath in glob.glob("%s/%s*.csv.gz" % (input_dir, prefix)):
    print(f"fpath: {fpath}")
    fname = os.path.basename(fpath)
    print(f"fname: {fname}")
    # ex) buf-proxy-himeji2-20230124-090001.csv.gz
    # ex) proxy-dev-20230124-090001.csv.gz
    # ホスト名は - を含む可変長文字列

    m = re.match(
        r"(?P<hostname>\S+)-(?P<logdate>\d{8})-(?P<logtime>\d{6})\.pcap\.csv\.gz", fname
    )

    hostname = m.group("hostname")
    logdatetime = "%s/%s/%s %s:%s" % (
        m.group("logdate")[0:4],
        m.group("logdate")[4:6],
        m.group("logdate")[6:8],
        m.group("logtime")[0:2],
        m.group("logtime")[2:4],
    )
    # debug: print(hostname, logdatetime)

    df = pd.read_csv(fpath, compression="gzip", header=0, dtype="object")
    df["hostname"] = hostname
    df["logdatetime"] = logdatetime
    # debug: print( df_temp )

    if first:
        df.to_csv(
            "%s/%s.csv" % (output_dir, prefix), index=False, columns=output_columns
        )
        first = False
    else:
        df.to_csv(
            "%s/%s.csv" % (output_dir, prefix),
            mode="a",
            index=False,
            header=False,
            columns=output_columns,
        )
