"""
B5: Retrieve NS (Name Server) Records
======================================
Equivalent of: nslookup -type=ns yachaytech.edu.ec

Question: What are the name servers for yachaytech.edu.ec?
"""

import dns.resolver

DOMAIN = "yachaytech.edu.ec"

print(f"  B5: NS Records")
print(f"  Domain: {DOMAIN}")

try:
    answers = dns.resolver.resolve(DOMAIN, "NS")
    print(f"Name server(s) for {DOMAIN}:")
    for rdata in answers:
        print(f"  -> {rdata.target}")

except dns.resolver.NXDOMAIN:
    print(f"Error: Domain '{DOMAIN}' does not exist.")
except dns.resolver.NoAnswer:
    print(f"Error: No NS records found for '{DOMAIN}'.")
except dns.exception.DNSException as e:
    print(f"DNS Error: {e}")
