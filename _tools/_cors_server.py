import http.server, socketserver

class CORSHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

PORT = 8791
with socketserver.TCPServer(("", PORT), CORSHandler) as httpd:
    print(f"Serving at port {PORT}")
    httpd.serve_forever()
