# Python 3 server example
from http.server import BaseHTTPRequestHandler, HTTPServer

from pysnmp.entity.engine import SnmpEngine
from pysnmp.hlapi import *
from pysnmp.hlapi.v3arch import next_cmd, CommunityData, UdpTransportTarget, ContextData
from pysnmp.smi.rfc1902 import ObjectType, ObjectIdentity

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
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes("<html><head><title>https://pythonbasics.org</title></head>", "utf-8"))
        self.wfile.write(bytes("<p>Request: %s</p>" % self.path, "utf-8"))
        self.wfile.write(bytes("<body>", "utf-8"))
        self.wfile.write(bytes("<p>This is an example web server.</p>", "utf-8"))
        self.wfile.write(bytes("</body></html>", "utf-8"))

if __name__ == "__main__":
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")