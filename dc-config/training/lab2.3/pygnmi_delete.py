# Modules
from pygnmi.client import gNMIclient
import pprint

# Variables
host = ('dc-leaf1', '57400')
pcroot = "/home/srcadmin/dc/ca/root/root-ca.pem"

# Main()
def main():
    with gNMIclient(target=host, username='admin', password='admin', path_cert=pcroot, debug=True) as gc:
        response = gc.set(delete=['interface[name=lo1]'], encoding = 'json_ietf')

if __name__ == '__main__':
    main()

