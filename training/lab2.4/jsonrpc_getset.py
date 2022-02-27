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

    # Extract the lo0 data from the response
    lo0_dict = response.json()['result'][0]

    # replace the IP address
    lo0_dict['subinterface'][0]['ipv4']['address'][0]['ip-prefix'] = "123.123.123.123/32"

    # Build a set method request using the modified dictinary as value for lo2
    set_interface = {
        "method": "set",
        "params": {"commands": [{"action": "update",
                                 "path": "/interface[name=lo2]",
                                 "value": lo0_dict }]},
        "jsonrpc": "2.0",
        "id": 100,
    }

    # print the set method
    print("\nJSON RPC Set method =", set_interface )

    # Send request to SR Linux
    response = requests.post(url, auth=('admin','admin'), json=set_interface)

    # Print the JSON data from the resposne
    print("\nJSON-RPC set result: \n\n", response.json())

if __name__ == "__main__":
    main()

