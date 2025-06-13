import subprocess
import sys
import time
from agent import ai_handle_message

def start_server():
    # Start the uvicorn server in a separate process
    server_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "sprint_board_server:app", "--reload"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    # Give the server a moment to start
    time.sleep(2)
    return server_process

if __name__ == "__main__":
    # Start the server
    server_process = start_server()
    print("Server started in a separate process...")
    
    try:
        while True:
            msg = input("🧑 You: ")
            if msg.lower() in ("exit", "quit"):
                break
            ai_handle_message(msg)
    finally:
        # Clean up the server process when done
        server_process.terminate()
        server_process.wait()
