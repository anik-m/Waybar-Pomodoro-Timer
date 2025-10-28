#!/usr/bin/env python

import json
import os
import sys
from datetime import datetime, timedelta
from enum import Enum, auto

# --- Configuration ---
# You can adjust these timers (in minutes)
WORK_MINS = 25
SHORT_BREAK_MINS = 5
LONG_BREAK_MINS = 15
SESSIONS_PER_CYCLE = 4  # Number of work sessions before a long break

STATE_FILE = os.path.expanduser("~/.cache/pomodoro_state.json")

# --- Enums for State Management ---

class SessionType(Enum):
    """Defines the type of session."""
    WORK = "WORK"
    SHORT_BREAK = "SHORT BREAK"
    LONG_BREAK = "LONG BREAK"

    def __str__(self):
        return self.value

class TimerState(Enum):
    """Defines the current running state of the timer."""
    STOPPED = auto()
    RUNNING = auto()
    PAUSED = auto()
    FINISHED = auto()

# --- State Data Class ---

class PomodoroState:
    """A simple class to hold and (de)serialize the timer state."""
    
    def __init__(self, state: TimerState, session_type: SessionType, end_time: datetime = None, 
                 remaining_secs: float = 0, work_sessions: int = 0):
        self.state = state
        self.session_type = session_type
        self.end_time = end_time
        self.remaining_secs = remaining_secs
        self.work_sessions = work_sessions # Tracks sessions completed in this cycle

    def to_dict(self):
        """Serialize to a dictionary for JSON storage."""
        return {
            "state": self.state.name,
            "session_type": self.session_type.name,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "remaining_secs": self.remaining_secs,
            "work_sessions": self.work_sessions,
        }

    @classmethod
    def from_dict(cls, data):
        """Deserialize from a dictionary."""
        try:
            state = TimerState[data["state"]]
            session_type = SessionType[data["session_type"]]
            end_time = datetime.fromisoformat(data["end_time"]) if data["end_time"] else None
            remaining_secs = float(data.get("remaining_secs", 0))
            work_sessions = int(data.get("work_sessions", 0))
            
            return cls(state, session_type, end_time, remaining_secs, work_sessions)
        except (KeyError, TypeError):
            # If state file is corrupt or old, return a clean state
            return cls.stopped()

    @classmethod
    def stopped(cls):
        """Returns a default, stopped state."""
        return cls(TimerState.STOPPED, SessionType.WORK, work_sessions=0)

# --- State File Handling ---

def load_state() -> PomodoroState:
    """Loads the timer state from the JSON file."""
    if not os.path.exists(STATE_FILE):
        return PomodoroState.stopped()
        
    try:
        with open(STATE_FILE, 'r') as f:
            data = json.load(f)
            return PomodoroState.from_dict(data)
    except (json.JSONDecodeError, IOError):
        # On corrupt file, return a default state
        return PomodoroState.stopped()

def save_state(state: PomodoroState):
    """Saves the current timer state to the JSON file."""
    try:
        os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
        with open(STATE_FILE, 'w') as f:
            json.dump(state.to_dict(), f)
    except IOError as e:
        print(f"Error saving state: {e}", file=sys.stderr)

# --- Core Timer Logic ---

def get_session_duration_secs(session_type: SessionType) -> int:
    """Returns the duration of a session in seconds."""
    if session_type == SessionType.WORK:
        return WORK_MINS * 60
    elif session_type == SessionType.SHORT_BREAK:
        return SHORT_BREAK_MINS * 60
    elif session_type == SessionType.LONG_BREAK:
        return LONG_BREAK_MINS * 60
    return 0 # Should not happen

def start_session(session_type: SessionType, work_sessions: int) -> PomodoroState:
    """Starts a new session of the given type."""
    now = datetime.now()
    duration_secs = get_session_duration_secs(session_type)
    end_time = now + timedelta(seconds=duration_secs)
    
    return PomodoroState(
        state=TimerState.RUNNING,
        session_type=session_type,
        end_time=end_time,
        remaining_secs=duration_secs,
        work_sessions=work_sessions
    )

def toggle_pause(state: PomodoroState) -> PomodoroState:
    """Toggles the pause state of the timer."""
    now = datetime.now()
    
    if state.state == TimerState.RUNNING:
        # PAUSE: Calculate remaining time and store it
        remaining = (state.end_time - now).total_seconds()
        state.state = TimerState.PAUSED
        state.remaining_secs = remaining
        state.end_time = None # Clear end_time as it's no longer valid
    
    elif state.state == TimerState.PAUSED:
        # RESUME: Calculate new end_time from remaining seconds
        state.state = TimerState.RUNNING
        state.end_time = now + timedelta(seconds=state.remaining_secs)
        # remaining_secs is kept as is until the next pause
    
    return state

def stop_timer() -> PomodoroState:
    """Stops the timer and resets to the default state."""
    return PomodoroState.stopped()

def cycle_state(state: PomodoroState) -> PomodoroState:
    """
    Cycles to the next logical state.
    Called on right-click ("cycle")
    """
    
    if state.state in [TimerState.RUNNING, TimerState.PAUSED]:
        # If timer is running or paused, just stop it
        return stop_timer()

    if state.state == TimerState.STOPPED:
        # Start the first work session
        return start_session(SessionType.WORK, 0)
    
    if state.state == TimerState.FINISHED:
        # The previous session finished, start the next one
        
        if state.session_type == SessionType.WORK:
            # Work finished, check if it's time for a long break
            if (state.work_sessions + 1) % SESSIONS_PER_CYCLE == 0:
                return start_session(SessionType.LONG_BREAK, state.work_sessions + 1)
            else:
                return start_session(SessionType.SHORT_BREAK, state.work_sessions + 1)
        
        elif state.session_type == SessionType.SHORT_BREAK:
            # Short break finished, start next work session
            return start_session(SessionType.WORK, state.work_sessions)
        
        elif state.session_type == SessionType.LONG_BREAK:
            # Long break finished, reset cycle and start work
            # We reset the work_sessions counter to 0
            return start_session(SessionType.WORK, 0)
            
    return state # Should not be reached, but good practice

# --- Output Generation ---

def get_output(state: PomodoroState) -> dict:
    """
    Checks and updates the state, then returns a JSON dict for Waybar.
    """
    now = datetime.now()
    
    # 1. Check for timer completion
    if state.state == TimerState.RUNNING and state.end_time and now >= state.end_time:
        state.state = TimerState.FINISHED
        state.end_time = None
        state.remaining_secs = 0

    # 2. Format output based on the (potentially updated) state
    if state.state == TimerState.STOPPED:
        return {
            "text": "🍅",
            "tooltip": "Pomodoro Stopped\nRight-click to start work.",
            "class": "stopped"
        }

    elif state.state == TimerState.FINISHED:
        next_session_type = ""
        if state.session_type == SessionType.WORK:
            if (state.work_sessions + 1) % SESSIONS_PER_CYCLE == 0:
                next_session_type = SessionType.LONG_BREAK
            else:
                next_session_type = SessionType.SHORT_BREAK
        
        elif state.session_type == SessionType.SHORT_BREAK:
            next_session_type = SessionType.WORK
        elif state.session_type == SessionType.LONG_BREAK:
            next_session_type = SessionType.WORK
        
        return {
            "text": "🎉 00:00",
            "tooltip": f"{state.session_type} finished!\nRight-click to start {next_session_type}.",
            "class": "finished"
        }

    elif state.state == TimerState.PAUSED:
        # Show the time that was remaining when pause was hit
        icon = "⏸️"
        mins, secs = divmod(int(state.remaining_secs), 60)
        time_str = f"{mins:02d}:{secs:02d}"
        tooltip = f"Paused: {state.session_type}\nClick to resume."
        css_class = "paused"
        
        return {
            "text": f"{icon} {time_str}",
            "tooltip": tooltip,
            "class": css_class
        }

    elif state.state == TimerState.RUNNING:
        # Calculate and show remaining time
        icon = "🍅" if state.session_type == SessionType.WORK else "☕"
        remaining = (state.end_time - now).total_seconds()
        
        # Ensure it doesn't go below zero before the next tick
        remaining = max(0, remaining) 
        
        mins, secs = divmod(int(remaining), 60)
        time_str = f"{mins:02d}:{secs:02d}"
        tooltip = f"{state.session_type}\nClick to pause."
        css_class = "work" if state.session_type == SessionType.WORK else "break"

        return {
            "text": f"{icon} {time_str}",
            "tooltip": tooltip,
            "class": css_class
        }

    return {} # Fallback

