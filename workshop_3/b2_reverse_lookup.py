"""
B2: Reverse Lookup (IP to Domain Name)
=======================================
Equivalent of: nslookup 8.8.8.8

Question: What domain is associated with the IP 8.8.8.8?
"""

import dns.resolver
import dns.reversename

IP_ADDRESS = "8.8.8.8"

print(f"  B2: Reverse Lookup (IP -> Domain)")
print(f"  IP: {IP_ADDRESS}")

try:
    # Build the reverse-lookup name (e.g. 8.8.8.8 -> 8.8.8.8.in-addr.arpa)
    reverse_name = dns.reversename.from_address(IP_ADDRESS)
    print(f"Reverse query name: {reverse_name}")

    answers = dns.resolver.resolve(reverse_name, "PTR")
    print(f"\nDomain name(s) associated with {IP_ADDRESS}:")
    for rdata in answers:
        print(f"  -> {rdata.target}")

except dns.resolver.NXDOMAIN:
    print(f"Error: No reverse record found for '{IP_ADDRESS}'.")
except dns.resolver.NoAnswer:
    print(f"Error: No PTR record found for '{IP_ADDRESS}'.")
except dns.exception.DNSException as e:
    print(f"DNS Error: {e}")
