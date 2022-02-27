import requests

def main():

    # SR Linux JSON-RPC server
    url = "http://dc-leaf1/jsonrpc"

    # Build get method for interface lo0
    get_interface = {
        "method": "get",
        "params": {"commands": [{"path": "/interface[name=lo0]", "datastore": "running"}]},
        "jsonrpc": "2.0",
        "id": 100,
    }

    print("\nJSON-RPC get method: \n\n", get_interface)

    # Send request as an HTTP POST
    response = requests.post(url, auth=('admin','admin'), json=get_interface)

    # Print request status code
    print(f"\nRequest Status Code: ", response.status_code)

    # Print response
    print("\nJSON-RPC get result: \n\n", response.json())

if __name__ == "__main__":
    main()

