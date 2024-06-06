from http.server import HTTPServer, SimpleHTTPRequestHandler
#import what you need from the http.server module
class OTARequestHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/firmware.bin":
            self.send_response(200)
            self.send_header("Content-type", "application/octet-stream")
            self.end_headers()
            with open("firmware.bin", "rb") as f:
                self.wfile.write(f.read())
        else:
            self.send_response(404)
            self.end_headers()
#this is the class that will handle the requests, make sure that you have the firmware.bin file in the same directory as this script

def run(server_class=HTTPServer, handler_class=OTARequestHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting OTA server on port {port}...')
    httpd.serve_forever()
#this function will start the server on the specified port, right now i have it set to 8000, which is what i think the esp32 is also set to? i hope

if __name__ == "__main__":
    run()


#from what ive read, i think this is all you need to start a simple http server that will serve the firmware.bin file when the esp32 requests it