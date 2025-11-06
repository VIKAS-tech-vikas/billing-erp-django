import subprocess
import time
import webbrowser
import socket

# Step 1: Start Django server
subprocess.Popen(["python", "manage.py", "runserver"], shell=True)

# Step 2: Wait until server is ready
def wait_for_server(host="127.0.0.1", port=8000, timeout=30):
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            with socket.create_connection((host, port), timeout=1):
                print("✅ Server is ready!")
                return True
        except OSError:
            time.sleep(1)
    print("❌ Server did not start in time.")
    return False

if wait_for_server():
    # Step 3: Open Add Item page in browser
    webbrowser.open("http://127.0.0.1:8000/add-item/")
else:
    print("Server not reachable. Please check Django setup.")

# Step 4: Keep the app running
input("Press Ctrl+C to exit...")
