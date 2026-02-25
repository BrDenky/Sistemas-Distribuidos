"""
B9: Query a Non-Existent Domain
================================
Equivalent of: nslookup nonexistdomain12345.com

Question: What is the response when querying a non-existent domain?
Expected : NXDOMAIN error (domain does not exist).
"""

import dns.resolver

DOMAIN = "nonexistdomain12345.com"

print(f"{'='*55}")
print(f"  B9: Query a Non-Existent Domain")
print(f"  Domain: {DOMAIN}")
print(f"{'='*55}\n")

try:
    answers = dns.resolver.resolve(DOMAIN, "A")
    # If we somehow get here, print the answers
    print(f"IP address(es) for {DOMAIN}:")
    for rdata in answers:
        print(f"  -> {rdata.address}")

except dns.resolver.NXDOMAIN:
    print(f"** NXDOMAIN Error **")
    print(f"   The domain '{DOMAIN}' does not exist in DNS.")
    print(f"   This is equivalent to nslookup's")
    print(f"   '*** can't find {DOMAIN}: Non-existent domain'")

except dns.resolver.NoAnswer:
    print(f"Error: No records found for '{DOMAIN}'.")
except dns.exception.DNSException as e:
    print(f"DNS Error: {e}")
