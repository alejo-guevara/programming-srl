# Modules
from pygnmi.client import gNMIclient
import pprint

# Variables
host = ('dc-leaf1', '57400')
pcroot = "/home/srcadmin/dc/ca/root/root-ca.pem"

# Main()
def main():
    with gNMIclient(target=host, username='admin', password='admin', path_cert=pcroot, debug=True) as gc:

        # get the configuration for interface lo0
        response = gc.get(path=['/interface[name=lo0]'], datatype='config', encoding='json_ietf')

        # store the configuration in a dictionary
        lo0_dict = response['notification'][0]['update'][0]['val']

        # replace the IP address of lo0 with the IP address of lo1
        lo0_dict['subinterface'][0]['ipv4']['address'][0]['ip-prefix'] = "123.123.123.123/32"

        # create interface lo1 with an update operation
        response = gc.set(update=[('interface[name=lo1]', lo0_dict)], encoding = 'json_ietf')

if __name__ == '__main__':
    main()

