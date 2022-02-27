# Modules
import grpc
from gnmi_pb2_grpc import gNMIStub
from gnmi_pb2 import CapabilityRequest

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

    # Create cap request - There are no parameters for a capabilities request
    cap_request = CapabilityRequest()

    # call the Capabilities RPC and wait for response
    cap_response = stub.Capabilities(cap_request, metadata=metadata)

    # print out the response
    print(cap_response)

if __name__ == "__main__":
    main()


