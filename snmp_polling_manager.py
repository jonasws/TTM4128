import time
import getpass
import smtplib
from email.mime.text import MIMEText
from snmp_monitor import fetch_datagram_statistics
from jinja2 import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader('./templates'))


HOSTS = ('129.241.208.60', '129.241.209.21')

INTERVAL = 5 * 60
smtpObj = smtplib.SMTP(host='smtp.stud.ntnu.no', port=587)
smtpObj.starttls()
smtpObj.login('jonasws', password=getpass.getpass(prompt='Enter your password:'))


def compose_email_summary(traffic_data):
    template = env.get_template('email.html')
    text = template.render(traffic_data=traffic_data)
    msg = MIMEText(text, _subtype='html')
    msg['Subject'] = 'Traffic data summary'
    msg['From'] = 'jonasws@stud.ntnu.no'
    msg['To'] = 'ttm4128@item.ntnu.no'
    smtpObj.sendmail('jonasws@stud.ntnu.no', ('ttm4128.item.ntnu.no', 'jonasws@stud.ntnu.no'), msg.as_string())
    print "The email was sent!"


if __name__ == '__main__':
    while True:
        traffic_data = []
        for host in HOSTS:
            ip_received, ip_delivered = fetch_datagram_statistics(host=host, ipv6=False)
            traffic_data.append({
                'ip_received': ip_received,
                'ip_delivered': ip_delivered,
                'host': host
            })
        compose_email_summary(traffic_data)
        time.sleep(INTERVAL)
