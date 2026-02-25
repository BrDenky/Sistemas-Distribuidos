"""
B6: Query Start of Authority (SOA) Record
==========================================
Equivalent of: nslookup -type=soa yachaytech.edu.ec

Question: What information does the SOA record provide about
          yachaytech.edu.ec?
"""

import dns.resolver

DOMAIN = "yachaytech.edu.ec"

print(f"{'='*55}")
print(f"  B6: SOA Record")
print(f"  Domain: {DOMAIN}")
print(f"{'='*55}\n")

try:
    answers = dns.resolver.resolve(DOMAIN, "SOA")
    for rdata in answers:
        print(f"SOA Record for {DOMAIN}:")
        print(f"  Primary name server : {rdata.mname}")
        print(f"  Responsible email   : {rdata.rname}")
        print(f"  Serial number       : {rdata.serial}")
        print(f"  Refresh interval    : {rdata.refresh} seconds")
        print(f"  Retry interval      : {rdata.retry} seconds")
        print(f"  Expire limit        : {rdata.expire} seconds")
        print(f"  Minimum TTL         : {rdata.minimum} seconds")

except dns.resolver.NXDOMAIN:
    print(f"Error: Domain '{DOMAIN}' does not exist.")
except dns.resolver.NoAnswer:
    print(f"Error: No SOA record found for '{DOMAIN}'.")
except dns.exception.DNSException as e:
    print(f"DNS Error: {e}")
