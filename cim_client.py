import pywbem

CIM_ENDPOINT = 'http://ttm4128.item.ntnu.no:5988'


def fetch_operating_system_information(conn=None):
    """
    Returns the CIM string describing the operating system, optionally reusing the connection object
    """
    if conn is None:
        conn = pywbem.WBEMConnection(CIM_ENDPOINT)

    os = conn.EnumerateInstances('CIM_OperatingSystem')[0]
    return os['version'], conn


def fetch_ip_interface_info(conn=None):
    """
    Returns a list of dictionaries containing info on IP interfaces
    """
    if conn is None:
        conn = pywbem.WBEMConnection(CIM_ENDPOINT)

    ip_interfaces = conn.EnumerateInstances('Linux_IPProtocolEndpoint')
    interface_infos = []

    for interface in ip_interfaces:
        interface_infos.append({
            'name': interface['elementName'],
            'ip_address': interface['ipv4address'],
            'subnet_mask': interface['subnetmask']
        })
    return interface_infos, conn
