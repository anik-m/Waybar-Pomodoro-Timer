#!/usr/bin/env python3

"""
Main entry point for the Waybar Pomodoro Timer.
This script parses command-line arguments and calls the appropriate
function from the 'core' module.
"""

import sys
from .core import print_waybar_output, toggle_pause, cycle_state, stop_timer

def main():
    """Parses command-line arguments."""
    if len(sys.argv) == 1:
        print_waybar_output()
    elif sys.argv[1] == "toggle":
        toggle_pause()
    elif sys.argv[1] == "cycle":
        cycle_state()
    elif sys.argv[1] == "stop":
        stop_timer()
        print_waybar_output() # Show the stopped state
    else:
        print(f"Unknown command: {sys.argv[1]}", file=sys.stderr)
        print("Usage: waybar-pomodoro [toggle|cycle|stop]", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
