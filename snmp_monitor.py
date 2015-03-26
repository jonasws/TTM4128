from __future__ import print_function
import time
from pysnmp.entity.rfc3413.oneliner import ntforg, cmdgen



ntfOrg = ntforg.NotificationOriginator()
cmdGen = cmdgen.CommandGenerator()
HOST = 'localhost'
THRESHOLD = 1900000
INTERVAL = 60


def fetch_datagram_statistics(host='localhost', ipv6=False):
    """
    Issues SNMP GET to retrieve IP-MIB::ipInReceives and IP-MIB::ipInDelivers and
    returns the two variables as a tuple.
    """
    errorIndication, errorStatus, errorIndex, varBinds = cmdGen.getCmd(
        cmdgen.CommunityData('ttm4128'),
        cmdgen.UdpTransportTarget((host, 161)),
        cmdgen.MibVariable('IP-MIB', 'ipInReceives', 0),
        cmdgen.MibVariable('IP-MIB', 'ipInDelivers', 0),
        lookupNames=True, lookupValues=True
    )
    ip_r = varBinds[0][1]
    ip_d = varBinds[1][1]
    return ip_r, ip_d


def fetch_operating_system_information(host='localhost'):
    errorIndication, errorStatus, errorIndex, varBinds = cmdGen.getCmd(
        cmdgen.CommunityData('ttm4128'),
        cmdgen.UdpTransportTarget((host, 161)),
        cmdgen.MibVariable('SNMPv2-MIB', 'sysDescr', 0),
        lookupNames=True, lookupValues=True
    )
    operating_system_info = varBinds[0][1]

    return str(operating_system_info)


def fetch_interface_list(host='localhost'):
    errorIndication, errorStatus, errorIndex, varBinds = cmdGen.bulkCmd(
        cmdgen.CommunityData('ttm4128'),
        cmdgen.UdpTransportTarget((host, 161)),
        0,
        25,
        cmdgen.MibVariable('IP-MIB', 'ipAddrTable',),
        lookupNames=True, lookupValues=True
    )
    interface_list = group_interface_information_list(varBinds)
    return interface_list


def group_interface_information_list(info_list):
    info_list = [v[0] for v in info_list]

    ip_address_class = info_list[0][1].__class__
    number_of_addresses = 0

    for index, ip_addr in enumerate(info_list):
        if not isinstance(ip_addr[1], ip_address_class):
            number_of_addresses = index
            break
        s = ip_addr[1].prettyPrint()
        assert isinstance(s, str)

    ip_information = []

    if number_of_addresses > 0:
        ip_addresses = [v[1].prettyPrint() for v in info_list[:number_of_addresses]]
        ip_entity_indexes = [int(v[1].prettyPrint()) for v in info_list[number_of_addresses:2*number_of_addresses]]
        ip_subnet_masks = [v[1].prettyPrint() for v in info_list[2*number_of_addresses:3*number_of_addresses]]

        interface_names = query_interface_name(ip_entity_indexes)
        ip_information = []
        for ipa, ipe, ips in zip(ip_addresses, interface_names, ip_subnet_masks):
            ip_information.append({
                'name': ipe,
                'ip_address': ipa,
                'subnet_mask': ips
            })

        return ip_information


def query_interface_name(entity_indexes, host='localhost'):
    errorIndication, errorStatus, errorIndex, varBinds = cmdGen.bulkCmd(
        cmdgen.CommunityData('ttm4128'),
        cmdgen.UdpTransportTarget((host, 161)),
        0,
        25,
        cmdgen.MibVariable('IF-MIB', 'ifTable',),
        lookupNames=True, lookupValues=True)

    info_list = [v[0] for v in varBinds]
    entity_index_class = info_list[0][1].__class__
    number_of_interfaces = 0

    for index, interface in enumerate(info_list):
        if not isinstance(interface[1], entity_index_class):
            number_of_interfaces = index
            break

    if number_of_interfaces > 0:
        interface_names = info_list[number_of_interfaces:2*number_of_interfaces]

        return [interface_names[e-1][1].prettyPrint() for e in entity_indexes]
    else:
        return [None]*len(entity_indexes)


def send_trap(ip_delivered, ip_received, host='localhost'):
    """
    Sends SNMP TRAP to the given host with the provided ip_delivered and ip_received parameters.
    """
    ntfOrg.sendNotification(
        ntforg.CommunityData('ttm4128'),
        ntforg.UdpTransportTarget((host, 162)),
        'trap',
        ntforg.MibVariable('NTNU-NOTIFICATION-MIB', 'anotif'),
        (ntforg.MibVariable('IP-MIB', 'ipInReceives'), ip_received),
        (ntforg.MibVariable('IP-MIB', 'ipInDelivers',), ip_delivered)
    )


if __name__ == '__main__':
    # In order to reuse the module
    while True:
        ip_received, ip_delivered = fetch_datagram_statistics(HOST)
        if ip_received > THRESHOLD:
            send_trap(ip_received, ip_delivered, HOST)
            print('IP RECEIVED: {}'.format(ip_received))
            print('IP DELIVERED: {}'.format(ip_delivered))
        time.sleep(INTERVAL)
