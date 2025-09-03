# Python 3 server example
from http.server import BaseHTTPRequestHandler, HTTPServer

from pysnmp.entity.engine import SnmpEngine
from pysnmp.hlapi import *
from pysnmp.hlapi.v3arch import next_cmd, CommunityData, UdpTransportTarget, ContextData
from pysnmp.smi.rfc1902 import ObjectType, ObjectIdentity
import json

hostName = "localhost"
serverPort = 8080

# try at walk function, connection via udp
# oid input - oid to start walk from
# community is a security thing ?
def snmp_walk(target, community, oid):
    for (errorIndication,
         errorStatus,
         errorIndex,
         varBinds) in next_cmd(SnmpEngine(),
                               CommunityData(community),
                               UdpTransportTarget((target, 161)),
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

        if self.path == '/api/walk':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')  # For CORS
            self.end_headers()

            try:
                # Call your SNMP walk function here
                # For example (modify according to your needs):
                result = snmp_walk("localhost", "public", "1.3.6.1.2.1")

                # Convert result to JSON and send response
                response = {'status': 'success', 'data': result}
                self.wfile.write(json.dumps(response).encode('utf-8'))
            except Exception as e:
                error_response = {'status': 'error', 'message': str(e)}
                self.wfile.write(json.dumps(error_response).encode('utf-8'))
            return



        self.send_response(200)
        self.send_header("Content-type", "text/html")
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