import requests

def main():

    # SR Linux JSON-RPC server
    url = "http://dc-leaf1/jsonrpc"

    # Build a set method request to delete lo2
    delete_interface = {
        "method": "set",
        "params": {"commands": [{"action": "delete",
                                 "path": "/interface[name=lo2]"}]},
        "jsonrpc": "2.0",
        "id": 100,
    }

    # print the set method
    print("\nJSON RPC Set method =", delete_interface )

    # Send request to SR Linux
    response = requests.post(url, auth=('admin','admin'), json=delete_interface)

    # Print the JSON data from the resposne
    print("\nJSON-RPC set result: \n\n", response.json())

    assert response.json()['result'] == {}
    assert response.json()['jsonrpc'] == '2.0'
    assert response.json()['id'] == 100

if __name__ == "__main__":
    main()

