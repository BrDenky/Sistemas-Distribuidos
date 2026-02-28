"""
B4: Retrieve MX (Mail Exchanger) Records
=========================================
Equivalent of: nslookup -type=mx yachaytech.edu.ec

Question: What are the mail servers for yachaytech.edu.ec?
"""

import dns.resolver

DOMAIN = "yachaytech.edu.ec"

print(f"  B4: MX Records")
print(f"  Domain: {DOMAIN}")

try:
    answers = dns.resolver.resolve(DOMAIN, "MX")
    print(f"Mail server(s) for {DOMAIN}:")
    for rdata in answers:
        print(f"  Priority {rdata.preference:3d}  ->  {rdata.exchange}")

except dns.resolver.NXDOMAIN:
    print(f"Error: Domain '{DOMAIN}' does not exist.")
except dns.resolver.NoAnswer:
    print(f"Error: No MX records found for '{DOMAIN}'.")
except dns.exception.DNSException as e:
    print(f"DNS Error: {e}")
