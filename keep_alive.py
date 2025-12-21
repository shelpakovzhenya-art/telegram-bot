"""Keep-alive server for Replit to prevent shutdown."""
import os
import sys
from flask import Flask
from threading import Thread

app = Flask(__name__)


@app.route('/')
def home():
    """Home endpoint to keep Replit alive."""
    return "Bot is running!", 200


@app.route('/health')
def health():
    """Health check endpoint."""
    return "OK", 200


@app.route('/ping')
def ping():
    """Ping endpoint for UptimeRobot."""
    return "pong", 200


def run():
    """Run Flask server."""
    try:
        # Replit использует переменную PORT из окружения
        port = int(os.environ.get('PORT', 8080))
        print(f"Starting keep-alive server on port {port}")
        app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)
    except Exception as e:
        print(f"Error starting keep-alive server: {e}", file=sys.stderr)


def keep_alive():
    """Start keep-alive server in background thread."""
    try:
        t = Thread(target=run, daemon=True)
        t.start()
        print("✅ Keep-alive server started successfully")
    except Exception as e:
        print(f"❌ Failed to start keep-alive server: {e}", file=sys.stderr)

