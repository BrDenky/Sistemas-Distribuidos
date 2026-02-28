"""
B7: Query for Canonical Name (CNAME)
=====================================
Equivalent of: nslookup -type=cname www.microsoft.com

Question: Does www.microsoft.com have a CNAME record?
          If so, what is it?
"""

import dns.resolver

DOMAIN = "www.microsoft.com"

print(f"  B7: CNAME Record")
print(f"  Domain: {DOMAIN}")

try:
    answers = dns.resolver.resolve(DOMAIN, "CNAME")
    print(f"CNAME record(s) for {DOMAIN}:")
    for rdata in answers:
        print(f"  -> {DOMAIN}  is an alias for  {rdata.target}")

except dns.resolver.NXDOMAIN:
    print(f"Error: Domain '{DOMAIN}' does not exist.")
except dns.resolver.NoAnswer:
    print(f"  No CNAME record found for '{DOMAIN}'.")
    print("  (The domain may resolve directly via A/AAAA records.)")
except dns.resolver.NoNameservers:
    print(f"Error: Could not reach any name server for '{DOMAIN}'.")
except dns.exception.DNSException as e:
    print(f"DNS Error: {e}")
