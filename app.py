#!/usr/bin/env python3
"""
app.py

Lightweight HTTP server to run and serve the Interactive Magnetic Periodic Table.
Usage:
    python3 app.py [--port 8000]

Features:
- Serves interactive_table.html as root `/`
- Serves magnetic_elements_enriched.json and magnetic_periodic_table.png
- Zero third-party dependencies (pure standard library http.server)
- Automatic free-port fallback if port 8000 is already in use
"""

import argparse
import http.server
import os
import socketserver
import sys
import webbrowser

DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class PeriodicTableRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def translate_path(self, path):
        # Route root path directly to interactive_table.html
        if path in ('/', '/index.html'):
            path = '/interactive_table.html'
        return super().translate_path(path)

    def log_message(self, format, *args):
        # Format clean, readable request logging
        sys.stderr.write(f"[{self.log_date_time_string()}] {args[0]} {args[1]}\n")


def find_free_port(start_port=8000, max_attempts=20):
    for port in range(start_port, start_port + max_attempts):
        try:
            with socketserver.TCPServer(("", port), None) as s:
                return port
        except OSError:
            continue
    raise RuntimeError("No available port found.")


def run_server(port=8000, open_browser=False):
    try:
        actual_port = port
        try:
            httpd = socketserver.TCPServer(("", actual_port), PeriodicTableRequestHandler)
        except OSError:
            actual_port = find_free_port(port + 1)
            httpd = socketserver.TCPServer(("", actual_port), PeriodicTableRequestHandler)

        url = f"http://localhost:{actual_port}/"
        print("=" * 70)
        print("🧲 INTERACTIVE MAGNETIC PERIODIC TABLE SERVER")
        print("=" * 70)
        print(f" Serving directory : {DIRECTORY}")
        print(f" Web Application   : {url}")
        print(f" Enriched Database : {url}magnetic_elements_enriched.json")
        print(f" High-Res PNG      : {url}magnetic_periodic_table.png")
        print("=" * 70)
        print("Press Ctrl+C to stop the server.")
        print("-" * 70)

        if open_browser:
            webbrowser.open(url)

        httpd.serve_forever()

    except KeyboardInterrupt:
        print("\nServer terminated by user. Exiting...")
    except Exception as e:
        print(f"\nError running server: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Serve the Interactive Magnetic Periodic Table")
    parser.add_argument("--port", type=int, default=8000, help="Port to serve on (default: 8000)")
    parser.add_argument("--open", action="store_true", help="Automatically open browser")
    args = parser.parse_args()

    run_server(port=args.port, open_browser=args.open)
