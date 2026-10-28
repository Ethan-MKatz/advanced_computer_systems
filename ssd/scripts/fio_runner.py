"""Safety-checked wrapper around fio for the SSD profiling project.

Every benchmark goes through run_fio(), which:
  * verifies the target is the single disposable regular file under ssd/testfile/
    (not a symlink, not a block device, expected size, ext4 on the expected mount),
  * checks free space, battery level, and NVMe temperature before starting,
  * samples NVMe temperature once per second while fio runs and aborts fio if the
    drive gets too hot,
  * stores fio JSON, stderr, return code, parameters, job-file text, and
    environment metadata under results/raw/<experiment>/.
"""

import hashlib
import json
import os
import shutil
import signal
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

SSD_DIR = Path(__file__).resolve().parents[1]
CONFIG_DIR = SSD_DIR / "configs"
RAW_DIR = SSD_DIR / "results" / "raw"
TESTFILE_DIR = SSD_DIR / "testfile"
TESTFILE = TESTFILE_DIR / "fio_testfile.bin"

GiB = 1024 ** 3
TESTFILE_SIZE = 4 * GiB
MIN_FREE_BYTES = 20 * GiB          # free space that must remain on the root fs
EXPECTED_FSTYPE = "ext4"
EXPECTED_SOURCE = "/dev/nvme0n1p3"

TEMP_START_MAX_C = 60.0            # wait for cooldown above this before starting
TEMP_ABORT_C = 75.0                # kill fio above this (drive warning is 82.8 C)
MIN_BATTERY_PCT = 20               # refuse to run on battery below this level


class SafetyError(RuntimeError):
    pass


# --------------------------------------------------------------------------- sensors

def _nvme_hwmon():
    for hw in Path("/sys/class/hwmon").glob("hwmon*"):
        try:
            if (hw / "name").read_text().strip() == "nvme":
                return hw
        except OSError:
            continue
    return None


def read_nvme_temp_c():
    """Composite NVMe temperature in Celsius, or None if unavailable."""
    hw = _nvme_hwmon()
    if hw is None:
        return None
    try:
        return int((hw / "temp1_input").read_text()) / 1000.0
    except (OSError, ValueError):
        return None


def power_state():
    ps = Path("/sys/class/power_supply")
    state = {"ac_online": None, "battery_pct": None, "platform_profile": None}
    try:
        state["ac_online"] = (ps / "AC" / "online").read_text().strip() == "1"
    except OSError:
        pass
    try:
        state["battery_pct"] = int((ps / "BAT0" / "capacity").read_text())
    except (OSError, ValueError):
        pass
    try:
        state["platform_profile"] = Path("/sys/firmware/acpi/platform_profile").read_text().strip()
    except OSError:
        pass
    return state


def free_bytes():
    return shutil.disk_usage(SSD_DIR).free


# --------------------------------------------------------------------------- safety

def _findmnt(path):
    out = subprocess.run(["findmnt", "-n", "-T", str(path), "-o", "SOURCE,FSTYPE"],
                         capture_output=True, text=True, check=True).stdout.split()
    return out[0], out[1]


def check_filesystem():
    source, fstype = _findmnt(TESTFILE_DIR)
    if fstype != EXPECTED_FSTYPE or source != EXPECTED_SOURCE:
        raise SafetyError(f"testfile dir is on {source} ({fstype}), expected "
                          f"{EXPECTED_SOURCE} ({EXPECTED_FSTYPE})")


def check_target():
    """Raise SafetyError unless TESTFILE is exactly the prepared disposable file."""
    if TESTFILE_DIR.is_symlink() or TESTFILE.is_symlink():
        raise SafetyError("test file or its directory is a symlink")
    if not TESTFILE.exists():
        raise SafetyError(f"{TESTFILE} does not exist; run prepare_testfile.py first")
    st = os.lstat(TESTFILE)
    import stat as _stat
    if not _stat.S_ISREG(st.st_mode):
        raise SafetyError(f"{TESTFILE} is not a regular file")
    if os.path.realpath(TESTFILE) != str(TESTFILE):
        raise SafetyError(f"realpath mismatch: {os.path.realpath(TESTFILE)}")
    if st.st_size != TESTFILE_SIZE:
        raise SafetyError(f"{TESTFILE} has size {st.st_size}, expected {TESTFILE_SIZE}")
    check_filesystem()


def check_resources():
    free = free_bytes()
    if free < MIN_FREE_BYTES:
        raise SafetyError(f"only {free / GiB:.1f} GiB free, need {MIN_FREE_BYTES / GiB:.0f} GiB")
    ps = power_state()
    if ps["ac_online"] is False and ps["battery_pct"] is not None \
            and ps["battery_pct"] < MIN_BATTERY_PCT:
        raise SafetyError(f"on battery at {ps['battery_pct']}%; plug in AC to continue")


def wait_for_cooldown(max_wait_s=600):
    t0 = time.time()
    while True:
        t = read_nvme_temp_c()
        if t is None or t <= TEMP_START_MAX_C:
            return t
        if time.time() - t0 > max_wait_s:
            raise SafetyError(f"NVMe still at {t:.1f} C after {max_wait_s}s cooldown")
        print(f"    NVMe at {t:.1f} C, cooling down...", flush=True)
        time.sleep(15)


# --------------------------------------------------------------------------- runner

def _job_text(job_path):
    text = job_path.read_text()
    if "${TESTFILE}" not in text:
        raise SafetyError(f"{job_path.name} must target ${{TESTFILE}}")
    for bad in ("/dev/", "filename=/"):
        if bad in text:
            raise SafetyError(f"{job_path.name} contains forbidden target '{bad}'")
    if "allow_file_create=0" not in text or "unlink=0" not in text:
        raise SafetyError(f"{job_path.name} must set allow_file_create=0 and unlink=0")
    return text


def _sample_temps(stop, samples, proc, abort_flag, t0):
    while not stop.is_set():
        t = read_nvme_temp_c()
        samples.append((round(time.time() - t0, 2), t))
        if t is not None and t >= TEMP_ABORT_C and proc.poll() is None:
            abort_flag.append(t)
            proc.send_signal(signal.SIGINT)
        stop.wait(1.0)


def run_fio(experiment, name, job, params, trial, output_format="json", force=False):
    """Run one fio job; return path to its metadata file.

    experiment: subdirectory of results/raw (e.g. "exp1_qd1")
    name:       run identifier without trial suffix
    job:        job file name in configs/
    params:     dict of environment variables substituted into the job file
    """
    out_dir = RAW_DIR / experiment
    out_dir.mkdir(parents=True, exist_ok=True)
    run_id = f"{name}_t{trial}"
    json_path = out_dir / f"{run_id}.json"
    meta_path = out_dir / f"{run_id}.meta.json"
    err_path = out_dir / f"{run_id}.stderr.txt"

    if not force and meta_path.exists():
        meta = json.loads(meta_path.read_text())
        if meta.get("returncode") == 0 and json_path.exists():
            print(f"  [skip] {run_id} (already complete)")
            return meta_path

    job_path = CONFIG_DIR / job
    job_text = _job_text(job_path)
    check_target()
    check_resources()
    temp_before = wait_for_cooldown()
    free_before = free_bytes()

    env = os.environ.copy()
    env.update({k: str(v) for k, v in params.items()})
    env["TESTFILE"] = str(TESTFILE)
    cmd = ["fio", f"--output-format={output_format}", f"--output={json_path}", str(job_path)]

    print(f"  [run ] {run_id}  " + " ".join(f"{k}={v}" for k, v in params.items()), flush=True)
    started = datetime.now(timezone.utc).isoformat()
    t0 = time.time()
    with open(err_path, "w") as err:
        proc = subprocess.Popen(cmd, env=env, stdout=subprocess.DEVNULL, stderr=err,
                                cwd=out_dir)
        stop, samples, abort_flag = threading.Event(), [], []
        sampler = threading.Thread(target=_sample_temps,
                                   args=(stop, samples, proc, abort_flag, t0), daemon=True)
        sampler.start()
        rc = proc.wait()
        stop.set()
        sampler.join()
    elapsed = time.time() - t0

    temps = [t for _, t in samples if t is not None]
    meta = {
        "run_id": run_id,
        "experiment": experiment,
        "name": name,
        "trial": trial,
        "job_file": f"configs/{job}",
        "job_sha256": hashlib.sha256(job_text.encode()).hexdigest(),
        "job_text": job_text,
        "params": {k: str(v) for k, v in params.items()},
        "testfile": str(TESTFILE),
        "command": cmd,
        "output_format": output_format,
        "started_utc": started,
        "elapsed_s": round(elapsed, 2),
        "returncode": rc,
        "aborted_for_temperature_c": abort_flag[0] if abort_flag else None,
        "nvme_temp_before_c": temp_before,
        "nvme_temp_after_c": read_nvme_temp_c(),
        "nvme_temp_max_c": max(temps) if temps else None,
        "nvme_temp_trace": samples,
        "free_bytes_before": free_before,
        "free_bytes_after": free_bytes(),
        "power": power_state(),
        "stderr_file": err_path.name,
    }
    meta_path.write_text(json.dumps(meta, indent=1))
    status = "ok" if rc == 0 else f"FAILED rc={rc}"
    print(f"         {status}, {elapsed:.0f}s, NVMe {temp_before}->{meta['nvme_temp_after_c']} C "
          f"(max {meta['nvme_temp_max_c']})", flush=True)
    if abort_flag:
        raise SafetyError(f"aborted {run_id}: NVMe reached {abort_flag[0]} C")
    return meta_path


def idle(seconds, reason=""):
    print(f"  [idle] {seconds}s {reason}", flush=True)
    time.sleep(seconds)


if __name__ == "__main__":
    try:
        check_target()
        check_resources()
        print("target OK:", TESTFILE, "temp", read_nvme_temp_c(), "C", power_state())
    except SafetyError as e:
        print("SAFETY CHECK FAILED:", e)
        sys.exit(1)


# --------------------------------------------------------------------------- shared defaults

TRIALS = 3
BASE = {"SIZE": "4g", "ENGINE": "io_uring", "DIRECT": 1, "RAMP": 2}


def seed(trial):
    """Distinct but reproducible random seed per trial."""
    return 4320 + trial


def params(**overrides):
    p = dict(BASE)
    p.update(overrides)
    return p
