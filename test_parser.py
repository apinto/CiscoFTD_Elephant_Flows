#!/usr/bin/env python3
"""
Simple test script to verify parsing with a small sample
"""

from connection_parser import ConnectionParser

# Test with a small sample first
sample_data = """UDP FORTISIEM: 10.1.76.4/45879 dc2: 10.1.5.101/53,
    flags - N1, idle 21s, uptime 21s, timeout 2m0s, bytes 28, Rx-RingNum 45, Internal-Data0/1
  Connection lookup keyid: 100587686

UDP FORTISIEM: 10.1.76.4/55229 dc2: 10.1.5.101/53,
    flags - N1, idle 1m55s, uptime 1m55s, timeout 2m0s, bytes 38, Rx-RingNum 37, Internal-Data0/1
  Connection lookup keyid: 503480914

TCP FORTISIEM: 10.1.76.3/57798 beproxy: 10.1.19.90/8000,
    flags UIO N1, idle 8s, uptime 2h39m, timeout 1h0m, bytes 14395, Rx-RingNum 61, Internal-Data0/1
  Initiator: 10.1.76.3, Responder: 10.1.19.90
  Connection lookup keyid: 1931784606"""

# Write sample to file
with open('sample_data.txt', 'w') as f:
    f.write(sample_data)

# Test the simple parser
parser = ConnectionParser()
connections = parser.parse_file_simple('sample_data.txt')

print("Sample parsing results:")
for i, conn in enumerate(connections):
    print(f"\nConnection {i+1}:")
    for key, value in conn.items():
        print(f"  {key}: {value}")

# Test analysis
parser.analyze_connections()
parser.print_summary()