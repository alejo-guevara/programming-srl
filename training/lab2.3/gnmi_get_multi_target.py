import grpc
from gnmi_pb2_grpc import gNMIStub
from gnmi_pb2 import GetRequest, Path, PathElem

import json
import pprint

# Variables
username = 'admin'
password = 'admin'
metadata = [('username', username), ('password', password)]
rootcert = "../dc/ca/root/root-ca.pem"

sr_linux_routers = [
    {
        "hostname": "dc-leaf1",
        "port": "57400"
    },
    {
        "hostname": "dc-leaf2",
        "port": "57400"
    },
    {
        "hostname": "dc-spine1",
        "port": "57400"
    },
    {
        "hostname": "dc-spine2",
        "port": "57400"
    },
]



# Main()
def main():
    # retrieve root CA certificate and create TLS channel credentials
    with open(rootcert, 'rb') as f:
        cert = grpc.ssl_channel_credentials(f.read())

    for sr_linux in sr_linux_routers:
        target = f"{sr_linux['hostname']}:{sr_linux['port']}"

        # Establish HTTP/2 secure channel to SR Linux gnmi server
        # cert will be used to authenticate the server certificate
        channel = grpc.secure_channel(target, credentials=cert)

        # Create gRPC stub
        stub = gNMIStub(channel)

        # new request for the IPv4 address of the interface ethernet-1/1
        path_eth_1_1_opstate = Path(elem = [PathElem(name="interface", key={ "name":"ethernet-1/1" }),
                                            PathElem(name="subinterface", key= { "index":"0" }),
                                            PathElem(name="ipv4"),
                                            PathElem(name="address")])

        # Create get request
        # - path must be a list, hence the square brackets
        # - type = 0     -> get all data
        # - encoding = 4 -> return the result encoded with JSON_IETF
        get_req = GetRequest(path = [path_eth_1_1_opstate], type=0, encoding=4)

        # call the Get RPC and wait for response
        # append username/password as metadata
        get_response = stub.Get(get_req, metadata=metadata)

        # convert the json_ietf string to a python dictionary
        json_dict = json.loads(get_response.notification[0].update[0].val.json_ietf_val)

        # display the ethernet-1/1 IP address for each SR linux router
        print(f"The IP address of ethernet-1/1 on {sr_linux['hostname']} is:")
        print("----", json_dict['address'][0]['ip-prefix'])

if __name__ == "__main__":
    main()

