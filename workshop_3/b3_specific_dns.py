"""
B3: Query Specific DNS Server
==============================
Equivalent of: nslookup hpc.cedia.edu.ec 1.1.1.1

Question: What is the IP address returned for hpc.cedia.edu.ec
          when using Cloudflare's DNS (1.1.1.1)?
"""

import dns.resolver

DOMAIN = "hpc.cedia.edu.ec"
CUSTOM_DNS = "1.1.1.1"   # Cloudflare's DNS server

print(f"  B3: Query Specific DNS Server")
print(f"  Domain:     {DOMAIN}")
print(f"  DNS Server: {CUSTOM_DNS} (Cloudflare)")

try:
    resolver = dns.resolver.Resolver()
    resolver.nameservers = [CUSTOM_DNS]

    answers = resolver.resolve(DOMAIN, "A")
    print(f"IP address(es) for {DOMAIN} via {CUSTOM_DNS}:")
    for rdata in answers:
        print(f"  -> {rdata.address}")

except dns.resolver.NXDOMAIN:
    print(f"Error: Domain '{DOMAIN}' does not exist.")
except dns.resolver.NoAnswer:
    print(f"Error: No A record found for '{DOMAIN}'.")
except dns.exception.DNSException as e:
    print(f"DNS Error: {e}")
