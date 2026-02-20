from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path


def _start_process(cmd: list[str], cwd: Path) -> subprocess.Popen:
    return subprocess.Popen(cmd, cwd=str(cwd))


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
            for proc in processes:
                code = proc.poll()
                if code is not None:
                    for other in processes:
                        if other.poll() is None:
                            other.terminate()
                    return code
            time.sleep(1)
    except KeyboardInterrupt:
        for proc in processes:
            if proc.poll() is None:
                proc.terminate()
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
