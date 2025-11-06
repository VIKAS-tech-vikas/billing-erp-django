import os
import webbrowser
import subprocess
import time

# Step 1: Start Django server
subprocess.Popen(["python", "manage.py", "runserver"], shell=True)

# Step 2: Wait a little for server to start
time.sleep(3)

# Step 3: Open in default browser
webbrowser.open("http://127.0.0.1:8000")

# Step 4: Keep the app running
input("Press Ctrl+C to exit...")
