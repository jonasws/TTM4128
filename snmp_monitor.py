import time

from pysnmp.entity.rfc3413.oneliner import ntforg, cmdgen

THRESHOLD = 10000


ntfOrg = ntforg.NotificationOriginator()
cmdGen = cmdgen.CommandGenerator()


HOST = 'localhost'


def fetch_datagram_statistics(host='localhost'):
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
    ntfOrg.sendNotification(
        ntforg.CommunityData('ttm4128'),
        ntforg.UdpTransportTarget((host, 162)),
        'trap',
        ntforg.MibVariable('NTNU-NOTIFICATION-MIB', 'anotif'),
        (ntforg.MibVariable('IP-MIB', 'ipInReceives'), ip_received),
        (ntforg.MibVariable('IP-MIB', 'ipInDelivers',), ip_delivered)
)

ip_received, ip_delivered = fetch_datagram_statistics(HOST)

while True:
    ip_received2, ip_delivered2 = fetch_datagram_statistics(HOST)
    ip_received, ip_delivered = ip_received2 - ip_received, ip_delivered2 - ip_delivered
    if ip_received > THRESHOLD:
        send_trap(ip_received2, ip_delivered2, HOST)
    time.sleep(5)
