ip addr flush dev eth1
ip link add link eth1 name eth1.1 type vlan id 1
ip addr add 192.168.201.2/28 brd 192.168.201.15 dev eth1.1
ip link set dev eth1.1 up
ip route del default
ip route add default via 192.168.201.1
