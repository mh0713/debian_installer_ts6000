#!/usr/bin/env python3.8


import datetime
from collections import Counter
from pathlib import Path

NGINX_LOG_ROOT = Path(r"/var/log/nginx/")
COUNT_DELTA = datetime.timedelta(minutes=5)
COUNT_DELTA_MIN = COUNT_DELTA.total_seconds() / 60


def count_access(file: Path, time_start: datetime.datetime, delta: int) -> Counter:
    date_strings = [(time_start + datetime.timedelta(minutes=i)).strftime("[%Y-%m-%dT%H:%M:") for i in range(delta)]
    print(date_strings)
    with file.open("r") as f:
        lines = [line for line in f if any((d in line) for d in date_strings)]
        print(lines)
        lines = [line.split(" ")[-1].strip() for line in lines]
    return Counter(lines)


def main():
    # 集計期間
    time_now = datetime.datetime.now()
    time_end = time_now.replace(
        minute=int((time_now.minute // COUNT_DELTA_MIN) * COUNT_DELTA_MIN),
        second=0,
        microsecond=0,
    )
    time_start = time_end - COUNT_DELTA

    # 下位フォルダごとに処理
    for dir in NGINX_LOG_ROOT.iterdir():
        if not dir.is_dir():
            continue
        try:
            access_log = dir / "access.log"
            access_log_1 = dir / "access.log.1"
            counter = Counter()
            if access_log.exists():
                counter += count_access(access_log, time_start, int(COUNT_DELTA_MIN))
            if access_log_1.exists():
                counter += count_access(access_log_1, time_start, int(COUNT_DELTA_MIN))
            print(counter)
            access_delta = dir / "access_delta"
            access_delta_lines = [f"{count} {status}" for status, count in counter.items()]
            access_delta.write_text("\n".join(access_delta_lines) + "\n", encoding="utf-8")
        except Exception:
            pass


if __name__ == "__main__":
    main()
