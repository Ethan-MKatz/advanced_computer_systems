#!/usr/bin/env python3
"""Create (once) the disposable 4 GiB fio target file under ssd/testfile/.

Refuses to overwrite anything: if the file already exists with the expected size it
is left alone; any other existing path is an error.
"""
import os
import subprocess
import sys

import fio_runner as fr


def main():
    fr.check_filesystem()
    if fr.TESTFILE_DIR.is_symlink():
        sys.exit("testfile directory is a symlink; refusing")
    if fr.TESTFILE.exists() or fr.TESTFILE.is_symlink():
        fr.check_target()
        print(f"{fr.TESTFILE} already prepared ({fr.TESTFILE_SIZE} bytes); nothing to do")
        return
    free = fr.free_bytes()
    if free - fr.TESTFILE_SIZE < fr.MIN_FREE_BYTES:
        sys.exit(f"not enough free space: {free / fr.GiB:.1f} GiB")
    print(f"free before: {free / fr.GiB:.1f} GiB; creating {fr.TESTFILE}")
    env = dict(os.environ, TESTFILE=str(fr.TESTFILE))
    out = fr.RAW_DIR / "prepare_testfile.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["fio", "--output-format=json", f"--output={out}",
                    str(fr.CONFIG_DIR / "prepare_testfile.fio")], env=env, check=True)
    fr.check_target()
    print(f"prepared {fr.TESTFILE}: {os.path.getsize(fr.TESTFILE)} bytes; "
          f"free after: {fr.free_bytes() / fr.GiB:.1f} GiB")


if __name__ == "__main__":
    main()
