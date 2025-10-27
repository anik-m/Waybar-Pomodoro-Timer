from setuptools import setup, find_packages

setup(
    name="waybar-pomodoro",
    version="1.0.0",
    packages=find_packages(),
    author="Your Name",
    author_email="your@email.com",
    description="A simple pomodoro timer for Waybar",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/waybar-pomodoro", # Optional
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    # This is the most important part:
    # It creates a command-line script 'waybar-pomodoro'
    # that runs the 'main' function from 'waybar_pomodoro/main.py'
    entry_points={
        'console_scripts': [
            'waybar-pomodoro = waybar_pomodoro.main:main',
        ],
    },
)

