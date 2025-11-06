import subprocess
import threading
import webview
import time

def start_django():
    """Start the Django development server"""
    subprocess.Popen(["python", "manage.py", "runserver"], shell=True)

# Run Django server in a separate thread
threading.Thread(target=start_django, daemon=True).start()

# Wait a little to ensure server starts
time.sleep(3)

# Open Django ERP in desktop window
webview.create_window(
    "Helpline Telecom ERP",
    "http://127.0.0.1:8000",
    width=1200,
    height=700,
    resizable=True,
    text_select=True,
    confirm_close=True,
    background_color="#f8f9fa"
)
webview.start()
