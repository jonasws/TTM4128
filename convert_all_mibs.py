from os import system, listdir
from os.path import isfile, join


SNMP_MIB_PATH = '/usr/share/snmp/mibs'

for f in listdir(SNMP_MIB_PATH):
    if not join(SNMP_MIB_PATH, f):
        continue
    mib_name = f[:-4]
    full_path = join(SNMP_MIB_PATH, f)

    system('build-pysnmp-mib -o pysnmp_mibs/{}.py {}'.format(mib_name, full_path))
