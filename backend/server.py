# Python 3 server example
import data
from http.server import BaseHTTPRequestHandler, HTTPServer

from pysnmp.entity.engine import SnmpEngine
from pysnmp.hlapi import *
from pysnmp.hlapi.v3arch import next_cmd, CommunityData, UdpTransportTarget, ContextData
from pysnmp.smi.rfc1902 import ObjectType, ObjectIdentity
import json
import logging
from datetime import datetime

hostName = "localhost"
serverPort = 8080

# Logging for the snmp function
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


# try at walk function, connection via udp
# oid input - oid to start walk from
# community is a security thing ?
def snmp_walk(target, community, oid):
    for (errorIndication,
         errorStatus,
         errorIndex,
         varBinds) in next_cmd(SnmpEngine(),
                               CommunityData(community),
                               UdpTransportTarget.create((target, 161)),
                               ContextData(),
                               ObjectType(ObjectIdentity(oid)),
                               lexicographicMode=False):
        if errorIndication:
            print(f"Error: {errorIndication}")
            break
        elif errorStatus:
            print(f"Error {errorStatus.prettyPrint()} at {errorIndex and varBinds[int(errorIndex) - 1][0] or '?'}")
            break
        else:
            for varBind in varBinds:
                print(f"{varBind[0]} = {varBind[1]}")

# basic server idea
class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def do_POST(self):
        #api endpoint for walk function
        if self.path == '/api/walk':
            print(f"=== New Request ===")
            print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Client Address: {self.client_address[0]}")

            #Reading request body
            content_length = int(self.headers.get('Content-Length',0))
            post_body = self.rfile.read(content_length)

            try:
                # Parse'n'log the JSON
                data = json.loads(post_body)
                print(f"Request body: {data}")
                ip = data.get('ip')
                print(f"Target IP for SNMP walk: {ip}")

                # Set CORS headers
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()

                print(f"Starting SNMP walk for IP: {ip}")
                result = snmp_walk(ip, "public", "1.3.6.1.2.1")
                print(f"SNMP walk completed successfully")

                response = {'status': 'success', 'data': result}
                self.wfile.write(json.dumps(response).encode('utf-8'))

            except Exception as e:
                print(f"ERROR: {str(e)}")
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                error_response = {'status': 'error', 'message': str(e)}
                self.wfile.write(json.dumps(error_response).encode('utf-8'))

            finally:
                print(f"Request completed")
                print("=" * 50)

    # Browsers send OPTIONS request before POST, to check if the server accepts such requests, so we handle
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Accept')
        self.end_headers()


if __name__ == "__main__":
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")