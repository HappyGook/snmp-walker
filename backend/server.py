from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import logging
from datetime import datetime
from pysnmp.hlapi.asyncio import *
from pysnmp.proto.rfc1905 import NoSuchObject, NoSuchInstance, EndOfMibView
import asyncio

hostName = "localhost"
serverPort = 8080

# Logging for the snmp function
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def parse_ipaddress(value_str):
    # 4-Byte-String -> IPv4-Address
    return '.'.join(str(b if isinstance(b, int) else ord(b)) for b in value_str)


async def snmp_walk(target, community, start_oid):
    """
    SNMP walk -- asynch

    Args:
        target (str): IP
        community (str): SNMP community string
        start_oid (str): Starting OID for the walk

    Returns:
        list: List of dictionaries containing OID and value pairs
    """
    results = []
    snmp_engine = SnmpEngine()

    try:
        # Create transport target
        transport_target = await UdpTransportTarget.create((target, 161))

        # Start with the initial OID
        current_oid = ObjectIdentity(start_oid)

        while True:
            error_indication, error_status, error_index, var_binds = await next_cmd(
                snmp_engine,
                CommunityData(community, mpModel=0), #for snmpwalk v1 use mpModel=0
                transport_target,
                ContextData(),
                ObjectType(current_oid),
                lexicographicMode=False,
                ignoreNonIncreasingOid=False
            )

            if error_indication:
                return {"status": "error", "message": str(error_indication)}

            elif error_status:
                return {"status": "error", "message": f"{error_status.prettyPrint()} at {error_index}"}


            # Process response
            if not var_binds:
                break

            for oid_obj, value_obj in var_binds:
                oid_str = str(oid_obj)
                value_type = type(value_obj).__name__

                # Check still within the requested subtree
                if not oid_str.startswith(start_oid):
                    return {"status": "success", "data": results}

                # Handle different value types
                if value_type in ("NoSuchObject", "NoSuchInstance"):
                    value_str = value_type
                elif value_type == "EndOfMibView":
                    return {"status": "success", "data": results}
                elif value_type == "IpAddress":
                    value_str = parse_ipaddress(value_obj.asOctets())
                else:
                    value_str = str(value_obj)

                results.append({
                    "oid": oid_str,
                    "value": value_str,
                    "type": value_type
                })

                # Update current OID for next iteration
                current_oid = ObjectIdentity(oid_str)

    except Exception as e:
        return {"status": "error", "message": str(e)}

    finally:
        # close the SNMP engine
        if hasattr(snmp_engine, "transport_dispatcher"):
            snmp_engine.transport_dispatcher.close_dispatcher()

    return {"status": "success", "data": results}

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

                # Create event loop and run the async function
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(snmp_walk(ip, "public", "1.3.6.1.4.1.41649.2.1.1"))
                loop.close()

                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()

                self.wfile.write(json.dumps(result).encode('utf-8'))
                print("SNMP walk completed successfully")

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