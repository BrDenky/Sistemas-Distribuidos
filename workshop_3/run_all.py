"""
Workshop 3 — Part B: DNS with dnspython
========================================
Runs all exercises B1–B9 in sequence.

Usage:
    python run_all.py
"""

import subprocess
import sys
import os

scripts = [
    ("B1", "b1_basic_lookup.py",       "Basic Domain Lookup"),
    ("B2", "b2_reverse_lookup.py",     "Reverse Lookup (IP → Domain)"),
    ("B3", "b3_specific_dns.py",       "Query Specific DNS Server"),
    ("B4", "b4_mx_records.py",         "MX Records"),
    ("B5", "b5_ns_records.py",         "NS Records"),
    ("B6", "b6_soa_record.py",         "SOA Record"),
    ("B7", "b7_cname_record.py",       "CNAME Record"),
    ("B8", "b8_debug_mode.py",         "Debug Mode"),
    ("B9", "b9_nonexistent_domain.py", "Non-Existent Domain"),
]

base_dir = os.path.dirname(os.path.abspath(__file__))

for tag, script, title in scripts:
    border = "=" * 60
    print(f"\n{border}")
    print(f"  {tag}: {title}")
    print(f"{border}")
    path = os.path.join(base_dir, script)
    result = subprocess.run([sys.executable, path], capture_output=False)
    if result.returncode != 0:
        print(f"[!] {script} exited with code {result.returncode}")

print("\n" + "=" * 60)
print("  All exercises completed.")
print("=" * 60)
