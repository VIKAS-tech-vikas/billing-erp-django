import subprocess
import threading
import webview
import time

def start_django():
    """Start Django server in background"""
    subprocess.Popen(["python", "manage.py", "runserver"], shell=True)

# Start Django server in a separate thread
threading.Thread(target=start_django, daemon=True).start()

# Wait for Django to start
time.sleep(3)

# Open directly the Add Item page instead of home
webview.create_window(
    "Helpline Telecom ERP - Add Item",
    "http://127.0.0.1:8000/add-item/",
    width=1200,
    height=700,
    resizable=True,
    confirm_close=True,
    background_color="#f8f9fa"
)
webview.start()
