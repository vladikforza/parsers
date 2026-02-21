from __future__ import annotations

import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path


def _start_process(cmd: list[str], cwd: Path) -> subprocess.Popen:
    return subprocess.Popen(cmd, cwd=str(cwd))


def _timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def main() -> int:
    root = Path(__file__).resolve().parent
    commands = [
        [sys.executable, "-m", "lenta.lenta_parser.runner"],
        [sys.executable, "-m", "ria.ria_parser.runner"],
        [sys.executable, "-m", "telegram_parser.runner"],
    ]

    processes = [_start_process(cmd, root) for cmd in commands]

    try:
        while True:
            for index, proc in enumerate(processes):
                code = proc.poll()
                if code is None:
                    continue
                cmd = commands[index]
                print(f"{_timestamp()} process exited ({code}): {' '.join(cmd)}")
                time.sleep(1)
                processes[index] = _start_process(cmd, root)
                print(f"{_timestamp()} process restarted: {' '.join(cmd)}")
            time.sleep(1)
    except KeyboardInterrupt:
        for proc in processes:
            if proc.poll() is None:
                proc.terminate()
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
