import os
import sys
import time
import socket
import threading
import uvicorn
import webview

# Add current / bundled dir to python path
BASE_DIR = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from server import app


def find_free_port(start_port: int = 8123) -> int:
    """Find an available TCP port starting from start_port."""
    for p in range(start_port, start_port + 50):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", p))
                return p
            except OSError:
                continue
    # Fallback to OS assigned port
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def run_backend(port: int):
    # Run uvicorn server in background
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="warning")


if __name__ == "__main__":
    port = find_free_port(8123)

    # 1. Start the FastAPI server in a background daemon thread
    server_thread = threading.Thread(target=run_backend, args=(port,), daemon=True)
    server_thread.start()

    # Wait briefly for the server to be ready
    time.sleep(1.2)

    # 2. Launch the desktop native window pointing to local server
    print(f"🚀 Khởi chạy CapCut AI Desktop trên cổng {port}...")
    window = webview.create_window(
        title="CapCut AI - TTS & STT Studio (Desktop)",
        url=f"http://127.0.0.1:{port}",
        width=1000,
        height=820,
        min_size=(700, 650),
        text_select=True,
        background_color="#0a0814",
    )
    
    try:
        webview.start()
    finally:
        # Clean exit when window is closed
        os._exit(0)

