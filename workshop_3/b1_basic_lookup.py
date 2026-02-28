"""
B1: Basic Domain Lookup
=======================
Equivalent of: nslookup yachaytech.edu.ec

Question: What is the IP address of yachaytech.edu.ec?
"""

import dns.resolver

DOMAIN = "yachaytech.edu.ec"

print(f"  B1: Basic Domain Lookup")
print(f"  Domain: {DOMAIN}")

try:
    answers = dns.resolver.resolve(DOMAIN, "A")
    print(f"IP address(es) for {DOMAIN}:")
    for rdata in answers:
        print(f"  -> {rdata.address}")

    print(f"\nDNS Server used: {answers.nameserver}")

except dns.resolver.NXDOMAIN:
    print(f"Error: Domain '{DOMAIN}' does not exist.")
except dns.resolver.NoAnswer:
    print(f"Error: No A record found for '{DOMAIN}'.")
except dns.exception.DNSException as e:
    print(f"DNS Error: {e}")
