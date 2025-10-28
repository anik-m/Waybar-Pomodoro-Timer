#!/usr/bin/env python

import sys
import json
import os
from waybar_pomodoro.core import (
    load_state,
    save_state,
    toggle_pause,
    stop_timer,
    cycle_state,
    get_output,
    STATE_FILE
)
from datetime import datetime
import traceback # Import traceback for error logging

# --- Simple Logger ---
LOG_FILE = os.path.expanduser("~/.cache/pomodoro.log")
def log_message(msg):
    """Appends a timestamped message to the log file."""
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        with open(LOG_FILE, "a") as f:
            f.write(f"[{datetime.now()}] {msg}\n")
    except Exception as e:
        # If logging fails, we can't do much.
        pass 

# Renamed this function from 'run' back to 'main'
def main():
    """
    Main entry point for the pipx command.
    """
    try:
        # Ensure cache directory exists before trying to load
        os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
        log_message(f"Script started. Command: {sys.argv[1:]}")
        
        state = load_state()
        log_message(f"Loaded state: {state.state.name}, Session: {state.session_type.name}")
        
        command = sys.argv[1] if len(sys.argv) > 1 else "status"

        if command == "toggle":
            state = toggle_pause(state)
            log_message(f"State after 'toggle': {state.state.name}")
        elif command == "stop":
            state = stop_timer()
            log_message("State after 'stop'")
        elif command == "cycle":
            state = cycle_state(state)
            log_message(f"State after 'cycle': {state.state.name}, Session: {state.session_type.name}")
        # "status" command just loads, updates, and prints

        output_dict = get_output(state)
        log_message(f"Generated output. New state: {state.state.name}")
        
        save_state(state)
        log_message("State saved.")
        
        print(json.dumps(output_dict))
        log_message("Output printed.")
        log_message("-" * 20) # Add a separator

    except Exception as e:
        log_message(f"--- SCRIPT FAILED ---")
        log_message(f"Error: {e}")
        log_message(f"Traceback: {traceback.format_exc()}")
        # Still try to print a minimal error for Waybar
        print(json.dumps({"text": "⚠️", "tooltip": f"Pomodoro Error: {e}", "class": "error"}))

if __name__ == "__main__":
    main()

