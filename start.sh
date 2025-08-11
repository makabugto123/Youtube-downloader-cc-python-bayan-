#!/bin/bash

# Start the Tor service in the background
service tor start

# Start the Python application in the foreground
# The 'exec' command replaces the script process with the python process,
# allowing it to receive signals from Render correctly.
exec python main.py
