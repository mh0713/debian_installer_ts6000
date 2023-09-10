#!/usr/bin/env python3

import os
import sys

import functions as func


def main():
    print("* Configuration start")
    func.proc_run("ansible-playbook -i ansible/inventory/local.yml ansible/setup.yml")
    print("* Configuration applied")


if __name__ == "__main__":
    if os.getuid() != 0:
        print("run as root")
        sys.exit(1)

    main()
