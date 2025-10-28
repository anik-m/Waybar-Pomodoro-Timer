# Waybar Pomodoro Timer
A simple, stateful pomodoro timer script for Waybar, packaged for easy installation.
## Installation
1. Clone this repository: ```git clone https://github.com/anik-m/Waybar-Pomodoro-Timer```
2. Navigate into the directory: ```cd Waybar-Pomodoro-Timer```
### Standard Python Installation (All other distros)

Install the package using pip. Using the -e flag (editable) is recommended, as it links the package to your source files, allowing you to make changes without reinstalling.
```
pip install -e .
```

If you don't want to edit it, you can just run:
```
pip install .
```
### Arch Linux Installation 
Using pip to install packages globally is discouraged on Arch Linux. Instead, use pipx.


```
pipx install .
```

After installation (with either method), the command waybar-pomodoro will be available in your system's path.

## Waybar Configuration

Update your Waybar config file to use the new waybar-pomodoro command. Note that you no longer need to use the full path.
1. Waybar config
```// Inside your Waybar config file (e.g., ~/.config/waybar/config)
"modules": [
    // ... other modules
    "custom/pomodoro": {
        "format": "{}",
        "exec": "waybar-pomodoro", // <-- No full path needed!
        "return-type": "json",
        "interval": 1,
        "on-click": "waybar-pomodoro toggle",
        "on-click-right": "waybar-pomodoro cycle",
        "on-click-middle": "waybar-pomodoro stop"
    }
    // ... other modules
]
```
2. Waybar style.css

You can use the same CSS as before.

```/* Inside your Waybar style.css (e.g., ~/.config/waybar/style.css) */

#custom-pomodoro {
    padding: 0 10px;
    border-radius: 8px;
    color: #ffffff;
}

#custom-pomodoro.work {
    background-color: #f44336; /* Red for work */
}

#custom-pomodoro.short-break {
    background-color: #4caf50; /* Green for short break */
}

#custom-pomodoro.long-break {
    background-color: #2196f3; /* Blue for long break */
}

#custom-pomodoro.paused {
    background-color: #ff9800; /* Orange for paused */
    color: #333333;
}

#custom-pomodoro.finished {
    background-color: #9c27b0; /* Purple for finished */
    animation: blink 1s ease-in-out infinite;
}

#custom-pomodoro.stopped {
    background-color: #555555; /* Gray for stopped */
}

/* A simple blinking animation for the 'finished' state */
@keyframes blink {
    0% { opacity: 1; }
    50% { opacity: 0.5; }
    100% { opacity: 1; }
}
```
