#!/usr/bin/env python3

import argparse
import os
from nfstream import NFStreamer

parser = argparse.ArgumentParser(
          prog="pcap2csv",
          description="PCAP parser",
          add_help=True
          )

parser.add_argument("-i", "--input", required=True)
parser.add_argument("-o", "--output", required=True)

args = parser.parse_args()

pcap_file = args.input
csv_file = args.output

print(pcap_file + " => " + csv_file)

my_streamer = NFStreamer(source=pcap_file, # or live network interface
                         decode_tunnels=True,
                         bpf_filter=None,
                         promiscuous_mode=True,
                         snapshot_length=1536,
                         idle_timeout=120,
                         active_timeout=1800,
                         accounting_mode=0,
                         udps=None,
                         n_dissections=20,
                         statistical_analysis=True,
                         splt_analysis=0,
                         n_meters=0,
                         max_nflows=0,
                         performance_report=0,
                         system_visibility_mode=0,
                         system_visibility_poll_ms=100)

my_streamer.to_csv(path=csv_file,
                   columns_to_anonymize=(),
                   flows_per_file=0,
                   rotate_files=0)

#for flow in my_streamer:
#    print(flow)  # print it.
