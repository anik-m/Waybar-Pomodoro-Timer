#!/usr/bin/env python3

"""
Core logic for the Waybar Pomodoro Timer.
This module handles state management and JSON output.
"""

import json
import time
import sys
from pathlib import Path

# --- Configuration ---
WORK_MINS = 25
SHORT_BREAK_MINS = 5
LONG_BREAK_MINS = 15

# The cycle of states
STATES = [
    ("WORK", WORK_MINS),
    ("SHORT_BREAK", SHORT_BREAK_MINS),
    ("WORK", WORK_MINS),
    ("SHORT_BREAK", SHORT_BREAK_MINS),
    ("WORK", WORK_MINS),
    ("SHORT_BREAK", SHORT_BREAK_MINS),
    ("WORK", WORK_MINS),
    ("LONG_BREAK", LONG_BREAK_MINS),
]

ICONS = {
    "WORK": "🍅",
    "SHORT_BREAK": "☕",
    "LONG_BREAK": "🧘",
    "PAUSED": "⏸️",
    "STOPPED": "🍅",
    "FINISHED": "🎉",
}

# State file to store the current pomodoro status
STATE_FILE = Path.home() / ".cache/pomodoro_state.json"
# --- End Configuration ---


def get_default_state():
    """Returns the initial state (stopped)."""
    return {
        "state_index": 0,
        "start_time": 0,
        "paused": True,
        "pause_time": 0,
    }

def read_state():
    """Reads the current state from the state file."""
    if not STATE_FILE.exists():
        return get_default_state()
    try:
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return get_default_state()

def write_state(state):
    """Writes the given state to the state file."""
    try:
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f)
    except IOError as e:
        print(f"Error writing state file: {e}", file=sys.stderr)

def stop_timer():
    """Stops the timer and removes the state file."""
    if STATE_FILE.exists():
        STATE_FILE.unlink()

def toggle_pause():
    """Toggles the pause state of the timer."""
    state = read_state()
    if state["start_time"] == 0:  # Can't toggle if never started
        return

    if state["paused"]:
        # Resuming
        pause_duration = time.time() - state["pause_time"]
        state["start_time"] += pause_duration
        state["paused"] = False
        state["pause_time"] = 0
    else:
        # Pausing
        state["paused"] = True
        state["pause_time"] = time.time()
    
    write_state(state)
    print_waybar_output() # Must print output immediately on click

def cycle_state():
    """Cycles to the next state (e.g., work -> break) and starts it."""
    state = read_state()
    
    state["state_index"] = (state["state_index"] + 1) % len(STATES)
    state["start_time"] = time.time()
    state["paused"] = False
    state["pause_time"] = 0
    
    write_state(state)
    print_waybar_output() # Must print output immediately on click

def print_waybar_output():
    """
    Calculates the current timer status and prints the Waybar JSON output.
    This is the main function called by Waybar every second.
    """
    state = read_state()
    
    # Get current state details
    state_name, duration_mins = STATES[state["state_index"]]
    duration_secs = duration_mins * 60

    if state["start_time"] == 0:
        # Timer is stopped
        output = {
            "text": ICONS["STOPPED"],
            "tooltip": "Pomodoro Stopped\nRight-click to start work.",
            "class": "stopped"
        }
        print(json.dumps(output))
        return

    # Calculate time remaining
    if state["paused"]:
        time_elapsed = state["pause_time"] - state["start_time"]
    else:
        time_elapsed = time.time() - state["start_time"]

    time_remaining = int(duration_secs - time_elapsed)

    # Prepare output dictionary
    output = {"text": "", "tooltip": "", "class": ""}

    if state["paused"]:
        icon = ICONS["PAUSED"]
        output["class"] = "paused"
        output["tooltip"] = f"Paused: {state_name.replace('_', ' ')}\nClick to resume."
    
    elif time_remaining <= 0:
        icon = ICONS["FINISHED"]
        output["class"] = "finished"
        next_state_name, _ = STATES[(state["state_index"] + 1) % len(STATES)]
        output["tooltip"] = f"{state_name.replace('_', ' ')} finished!\nRight-click to start {next_state_name.replace('_', ' ')}."
        time_remaining = 0 # Don't show negative numbers
    
    else:
        icon = ICONS.get(state_name, "🍅")
        output["class"] = state_name.lower().replace("_", "-") # e.g., "short-break"
        output["tooltip"] = f"{state_name.replace('_', ' ')}\nClick to pause."

    # Set the text format
    mins, secs = divmod(time_remaining, 60)
    output["text"] = f"{icon} {mins:02d}:{secs:02d}"
    
    # Print the final JSON
    print(json.dumps(output))
