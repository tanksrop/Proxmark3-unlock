#!/usr/bin/env python3
import subprocess
import re
import time
from pydbus import SessionBus
from gi.repository import GLib

# === CONFIG ===
UID_FILE = "/home/ben/rfid/uid-list.txt"
COOLDOWN = 3  # seconds between unlocks
PM3_COMMAND = ["pm3", "-c", "hf 14a reader -w -s"]  # PM3 command (adjust if in distrobox)
PM3_READ_INTERVAL = 0.2  # seconds between reading PM3 lines

# === LOAD AUTHORIZED UIDS ===
try:
    with open(UID_FILE, "r") as f:
        AUTHORIZED_UIDS = set(line.strip().upper() for line in f if line.strip())
    print(f"Loaded {len(AUTHORIZED_UIDS)} authorized UID(s) from {UID_FILE}")
except FileNotFoundError:
    print(f"UID list file not found: {UID_FILE}")
    AUTHORIZED_UIDS = set()

# === STATE ===
pm3_proc = None
last_unlock = 0

# === FUNCTIONS ===
def start_pm3():
    """Start PM3 reader."""
    global pm3_proc
    if pm3_proc is None:
        print("Starting PM3...")
        pm3_proc = subprocess.Popen(
            PM3_COMMAND,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True
        )

def stop_pm3():
    """Stop PM3 reader."""
    global pm3_proc
    if pm3_proc:
        print("Stopping PM3...")
        pm3_proc.terminate()
        pm3_proc.wait()
        pm3_proc = None

def unlock_session():
    """Unlock the current session."""
    subprocess.run(["loginctl", "unlock-session"])

def process_pm3_output():
    """Read lines from PM3 and unlock if authorized UID seen."""
    global last_unlock, pm3_proc
    if pm3_proc is None or pm3_proc.stdout is None:
        return True  # Continue GLib loop

    # Stop PM3 immediately if screen unlocked (failsafe)
    if not screensaver.GetActive():
        stop_pm3()
        return True

    line = pm3_proc.stdout.readline()
    if line and "UID:" in line:
        m = re.search(r"UID:\s*([0-9A-F ]+)", line)
        if m:
            uid = m.group(1).strip()
            print("Seen UID:", uid)
            now = time.time()
            if uid in AUTHORIZED_UIDS and (now - last_unlock) > COOLDOWN:
                print("Authorized UID — unlocking")
                unlock_session()
                last_unlock = now
    return True  # Continue GLib loop

def handle_lock_change(locked):
    """Callback for screen lock/unlock events."""
    if locked:
        print("Screen locked — starting PM3")
        start_pm3()
        GLib.timeout_add(int(PM3_READ_INTERVAL * 1000), process_pm3_output)
    else:
        print("Screen unlocked — stopping PM3")
        stop_pm3()

# === MAIN ===
print("RFID DBus watcher ready")

# Connect to DBus session
bus = SessionBus()
screensaver = bus.get(".ScreenSaver")

# Check initial lock state (for already locked screen at startup)
try:
    initial_locked = screensaver.GetActive()
    if initial_locked:
        print("Screen already locked at startup — starting PM3")
        start_pm3()
        GLib.timeout_add(int(PM3_READ_INTERVAL * 1000), process_pm3_output)
except Exception as e:
    print("Failed to get initial lock state:", e)

# Listen for future lock/unlock events
screensaver.ActiveChanged.connect(handle_lock_change)

# Start the GLib event loop
loop = GLib.MainLoop()
loop.run()