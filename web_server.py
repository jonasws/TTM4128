from flask import Flask, render_template
from cim_client import fetch_operating_system_information, fetch_ip_interface_info
from snmp_monitor import fetch_operating_system_information as snmp_fetch_system_information
from snmp_monitor import fetch_interface_list as snmp_fetch_interface_list

app = Flask(__name__)
DEBUG = True
PORT = 9000

@app.route('/cim/')
def cim_information():
    """
    Fetches operating system information and information on IP interfaces, using CIM,
    Displays an HTML page with formatted results.
    """
    os_info, conn = fetch_operating_system_information()
    ip_interfaces, conn = fetch_ip_interface_info(conn)

    return render_template('cim_information.html', **{
        'os_info': os_info,
        'ip_interfaces': ip_interfaces
    })

@app.route('/snmp/')
def snmp_information():
    """
    Fetches operating system information and information on IP interfaces, using SNMP.
    Displays an HTML page with formatted results.
    """
    os_info, ip_interfaces = snmp_fetch_system_information(), snmp_fetch_interface_list()

    return render_template('snmp_information.html', **{
        'os_info': os_info,
        'ip_interfaces': ip_interfaces
    })


if __name__ == '__main__':
    app.debug = DEBUG
    app.run(port=PORT)
