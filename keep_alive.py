"""Keep-alive server for Replit to prevent shutdown."""
from flask import Flask
from threading import Thread

app = Flask('')


@app.route('/')
def home():
    """Home endpoint to keep Replit alive."""
    return "Bot is running!"


def run():
    """Run Flask server."""
    app.run(host='0.0.0.0', port=8080)


def keep_alive():
    """Start keep-alive server in background thread."""
    t = Thread(target=run)
    t.daemon = True
    t.start()

