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
