# Modules
from pygnmi.client import gNMIclient, telemetryParser
import pprint

# Variables
host = ('dc-leaf1', '57400')
root_ca = '/home/srcadmin/dc/ca/root/root-ca.pem'
pp = pprint.PrettyPrinter(indent=2)
subscribe = {
   'subscription': [
       {
          'path': '/interface[name=mgmt0]/traffic-rate',
          'mode': 'sample',
          'sample_interval': 5000000000
       },
#       {
#          'path': '/network-instance[name=default]/protocols/bgp/neighbor[peer-address=10.1.1.0]/session-state',
#          'mode': 'on_change',
#       },
   ],
   'mode': 'stream',
   'encoding': 'json_ietf'
}

# Main
def main():

    with gNMIclient(target=host, username='admin', password='admin', path_cert=root_ca) as gc:

        telemetry_stream = gc.subscribe2(subscribe=subscribe)

        for telemetry_entry in telemetry_stream:
            pp.pprint(telemetry_entry)

if __name__ == '__main__':
    main()

