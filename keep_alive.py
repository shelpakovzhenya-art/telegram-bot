"""Keep-alive server for Replit to prevent shutdown."""
import os
import sys
from datetime import datetime
from flask import Flask, jsonify
from threading import Thread

app = Flask(__name__)

# Track server start time
START_TIME = datetime.now()


@app.route('/')
def home():
    """Home endpoint to keep Replit alive."""
    uptime = (datetime.now() - START_TIME).total_seconds()
    return f"Bot is running! Uptime: {int(uptime)}s", 200


@app.route('/health')
def health():
    """Health check endpoint for UptimeRobot."""
    uptime = (datetime.now() - START_TIME).total_seconds()
    return jsonify({
        "status": "ok",
        "uptime_seconds": int(uptime),
        "timestamp": datetime.now().isoformat()
    }), 200


@app.route('/ping')
def ping():
    """Ping endpoint for UptimeRobot."""
    return "pong", 200


@app.route('/status')
def status():
    """Status endpoint with detailed information."""
    uptime = datetime.now() - START_TIME
    return jsonify({
        "status": "online",
        "uptime_seconds": int(uptime.total_seconds()),
        "uptime_formatted": str(uptime).split('.')[0],
        "started_at": START_TIME.isoformat(),
        "current_time": datetime.now().isoformat()
    }), 200


def run():
    """Run Flask server."""
    try:
        # Replit использует переменную PORT из окружения
        port = int(os.environ.get('PORT', 8080))
        print(f"🚀 Starting keep-alive server on port {port}")
        print(f"📡 Server will be available at: http://0.0.0.0:{port}")
        print(f"✅ Use these endpoints for UptimeRobot:")
        print(f"   - http://your-repl-url.repl.co/")
        print(f"   - http://your-repl-url.repl.co/health")
        print(f"   - http://your-repl-url.repl.co/ping")
        app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)
    except Exception as e:
        print(f"❌ Error starting keep-alive server: {e}", file=sys.stderr)


def keep_alive():
    """Start keep-alive server in background thread."""
    try:
        t = Thread(target=run, daemon=True)
        t.start()
        print("✅ Keep-alive server started successfully")
        print("💡 Configure UptimeRobot to ping your Repl URL every 5 minutes")
    except Exception as e:
        print(f"❌ Failed to start keep-alive server: {e}", file=sys.stderr)

