# Modules
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

# Main()
def main():
    # retrieve root CA certificate and create TLS channel credentials
    with open(rootcert, 'rb') as f:
        cert = grpc.ssl_channel_credentials(f.read())

    # Establish HTTP/2 secure channel to SR Linux gnmi server
    # cert will be used to authenticate the server certificate
    channel = grpc.secure_channel('dc-leaf1:57400', credentials=cert)

    # Create gRPC stub
    stub = gNMIStub(channel)

    # Build YANG Path
    path_eth_1_1 = Path(elem = [PathElem(name="interface", key={ "name":"ethernet-1/1" })])
    print("Path to ethernet-1/1:")
    print("-------------------")
    print(path_eth_1_1)

    # Create get request
    # - path must be a list, hence the square brackets
    # - type = 1     -> get config data only
    # - encoding = 4 -> return the result encoded with JSON_IETF
    get_req = GetRequest(path = [path_eth_1_1], type=1, encoding=4)
    print("Get Request:")
    print("-----------")
    print(get_req)

    # call the Get RPC and wait for response
    # append username/password as metadata
    get_response = stub.Get(get_req, metadata=metadata)

    # print out the response
    print("Get Response:")
    print("------------")
    print(get_response)

    # convert the json_ietf string to a python dictionary
    json_dict = json.loads(get_response.notification[0].update[0].val.json_ietf_val)

    # display with pretty print
    print("Returned value as a dictionary:")
    print("-------------------------------")
    pprint.pprint(json_dict)

    # example of a path with 2 pathElem components
    # new request for the operational state of the interface ethernet-1/1
    path_eth_1_1_opstate = Path(elem = [PathElem(name="interface", key={ "name":"ethernet-1/1" }),
                                        PathElem(name="oper-state")])
    print("\n\nPath to ethernet-1/1 op state:")
    print("------------------------------")
    print(path_eth_1_1_opstate)

    # Create get request
    # - path must be a list, hence the square brackets
    # - type = 0     -> get all data
    # - encoding = 4 -> return the result encoded with JSON_IETF
    get_req = GetRequest(path = [path_eth_1_1_opstate], type=0, encoding=4)
    print("Get Request:")
    print("-----------")
    print(get_req)

    # call the Get RPC and wait for response
    # append username/password as metadata
    get_response = stub.Get(get_req, metadata=metadata)

    # print out the response
    print("Get Response:")
    print("------------")
    print(get_response)

    # convert the json_ietf string to a python dictionary
    json_dict = json.loads(get_response.notification[0].update[0].val.json_ietf_val)

    # display with pretty print
    print("Returned value as a dictionary:")
    print("-------------------------------")
    pprint.pprint(json_dict)





if __name__ == "__main__":
    main()


