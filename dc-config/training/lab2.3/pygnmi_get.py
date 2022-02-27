# Modules
from pygnmi.client import gNMIclient
import pprint

# Variables
host = ('dc-leaf1', '57400')
pcroot = "/home/srcadmin/dc/ca/root/root-ca.pem"
pp = pprint.PrettyPrinter()

# Main()
def main():
    with gNMIclient(target=host, username='admin', password='admin', path_cert=pcroot) as gc:

        response = gc.get(path=['/interface[name=lo0]'], datatype='config', encoding='json_ietf')


        print("type of response: ", type(response))
        print("\nresponse['notification'][0]:")
        print("---------------------------")
        pp.pprint(response['notification'][0])


        lo0_dict = response['notification'][0]['update'][0]['val']
        print("returned value for lo0:")
        print("--------------------------------")
        pp.pprint(lo0_dict)

if __name__ == '__main__':
    main()

