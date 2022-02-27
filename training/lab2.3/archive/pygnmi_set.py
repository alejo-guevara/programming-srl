from pygnmi.client import gNMIclient
import pprint

# Variables
host = ('dc-leaf1', '57400')
pcroot = "/home/srcadmin/dc/ca/root/root-ca.pem"

# Main()
def main():
    with gNMIclient(target=host, username='admin', password='admin', path_cert=pcroot, debug=True) as gc:
        update_config = [
           ("/interface[name=lo1]/subinterface[index=0]/ipv4/address[ip-prefix=1.1.1.1/32]", []),
           ("/network-instance[name=default]/interface[name=lo1.0]", []),
        ]
        print(type(update_config))
        delete_config = [
           ("/interface[name=lo1]/subinterface[index=0]/ipv4/address[ip-prefix=1.1.1.1/32]"),
           ("/network-instance[name=default]/interface[name=lo1.0]"),
        ]

        result = gc.set(delete=delete_config, encoding = 'json_ietf')
        pprint.pprint(result)

        inter_dict = {
            'admin-state': 'enable',
            'description': 'Connected to dc-spine-1',
            'ethernet': {'flow-control': {}},
            'mtu': 9000,
            'sflow': {},
            'subinterface': [{'admin-state': 'enable',
                   'index': 0,
                   'ipv4': {'address': [{'ip-prefix': '10.1.1.1/31'}],
                            'allow-directed-broadcast': False,
                            'srl_nokia-interfaces-nbr:arp': {'duplicate-address-detection': True,
                                                             'host-route': {},
                                                             'learn-unsolicited': False,
                                                             'timeout': 14400}},
                   'srl_nokia-acl:acl': {'input': {}, 'output': {}},
                   'srl_nokia-interfaces-vlans:vlan': {'encap': {}},
                   'srl_nokia-qos:qos': {'input': {'classifiers': {}},
                                         'output': {'rewrite-rules': {}}}}],
            'transceiver': {}
        }
        print(type(inter_dict))
        print(inter_dict)
        #replace_config = [ ("interface[name=ethernet-1/3]", inter_dict) ]
        #result = gc.set(replace=replace_config, encoding = 'json_ietf')
        #pprint.pprint(result)

        response = gc.get(path=['/interface[name=lo0]'], datatype='config', encoding='json_ietf')

        print("type of response: ", type(response))
        print("with pprint")
        pprint.pprint(response)

        lo0_dict = response['notification'][0]['update'][0]['val']
        print("returned value for lo0:")
        print("--------------------------------")
        pprint.pprint(lo0_dict)


        lo0_dict['subinterface'][0]['ipv4']['address'][0]['ip-prefix'] = "123.123.123.123/32"
        pprint.pprint(lo0_dict)
        result = gc.set(replace= [ ('interface[name=lo1]', lo0_dict) ], encoding = 'json_ietf')
        pprint.pprint(result)


if __name__ == '__main__':
    main()

