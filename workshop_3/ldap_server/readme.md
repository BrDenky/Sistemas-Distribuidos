# 1. Start the LDAP directory server first
python ldap_server.py

# 2. Start publishers (each in its own terminal)
python publisher.py WEATHER
python publisher.py NEWS

# 3. Start the subscriber — it automatically discovers addresses via LDAP
python subscriber.py WEATHER NEWS

# Cross-machine: point everything at the same LDAP host
python publisher.py WEATHER --ldap-host <LDAP_IP>
python subscriber.py WEATHER --ldap-host <LDAP_IP>
