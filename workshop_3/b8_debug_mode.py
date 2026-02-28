"""
B8: Debug Mode
==============
Equivalent of: nslookup -debug yachaytech.edu.ec

Question: What additional details are provided in debug mode?

dnspython exposes the full DNS message (flags, question/answer/authority/
additional sections) which mirrors what nslookup -debug shows.
"""

import dns.message
import dns.query
import dns.rdatatype
import dns.name

DOMAIN  = "yachaytech.edu.ec"
DNS_SERVER = "8.8.8.8"

print(f"  B8: Debug Mode")
print(f"  Domain: {DOMAIN}")
print(f"  Using DNS: {DNS_SERVER}")

try:
    qname   = dns.name.from_text(DOMAIN)
    request = dns.message.make_query(qname, dns.rdatatype.A)

    print("=== RAW QUERY MESSAGE ===")
    print(request.to_text())

    response = dns.query.udp(request, DNS_SERVER, timeout=5)

    print("\n=== RAW RESPONSE MESSAGE ===")
    print(response.to_text())

    print("\n=== PARSED DETAILS ===")
    print(f"  Flags          : {dns.flags.to_text(response.flags)}")
    print(f"  Question count : {len(response.question)}")
    print(f"  Answer count   : {len(response.answer)}")
    print(f"  Authority count: {len(response.authority)}")
    print(f"  Additional cnt : {len(response.additional)}")

    if response.answer:
        print("\n  Answer section:")
        for rrset in response.answer:
            for rdata in rrset:
                print(f"    {rrset.name}  TTL={rrset.ttl}  {rdata}")

except Exception as e:
    print(f"Error: {e}")
