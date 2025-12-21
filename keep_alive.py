"""Keep-alive server for Replit to prevent shutdown."""
import os
from flask import Flask
from threading import Thread

app = Flask('')


@app.route('/')
def home():
    """Home endpoint to keep Replit alive."""
    return "Bot is running!"


@app.route('/health')
def health():
    """Health check endpoint."""
    return "OK", 200


def run():
    """Run Flask server."""
    # Replit использует переменную PORT из окружения
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)


def keep_alive():
    """Start keep-alive server in background thread."""
    t = Thread(target=run)
    t.daemon = True
    t.start()
    print("Keep-alive server started")

