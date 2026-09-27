from http.server import HTTPServer, BaseHTTPRequestHandler

class HelloWorldHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b"Hello, World!")

def run(server_class=HTTPServer, handler_class=HelloWorldHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Starting server on port {port}...")
    httpd.serve_forever()

if __name__ == '__main__':
    run()
