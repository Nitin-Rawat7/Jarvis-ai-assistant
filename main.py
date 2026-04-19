from ui import app

if __name__ == "__main__":
    import subprocess
    import threading
    import time

    BRAVE_PATH = "C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe"

    def open_jarvis_in_brave():
        """Open JARVIS UI in Brave after server starts."""
        time.sleep(2)  # wait for server to start
        try:
            subprocess.Popen([BRAVE_PATH, "--new-tab", "http://localhost:7860"])
            print("✅ JARVIS opened in Brave!")
        except Exception as e:
            print(f"❌ Could not open Brave: {e}")
            print("👉 Manually open: http://localhost:7860")

    print("\n" + "="*50)
    print("  JARVIS is starting...")
    print("  Opening in Brave browser...")
    print("="*50 + "\n")

    # Open Brave after 2 seconds in background
    threading.Thread(target=open_jarvis_in_brave, daemon=True).start()

    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        show_error=True,
        inbrowser=False,   # ← disable auto open in default browser
    )