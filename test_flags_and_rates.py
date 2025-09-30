#!/usr/bin/env python3
"""
Quick Flag and Rate Analysis Test
"""

from connection_parser import ConnectionParser

def main():
    """Test flag and rate analysis"""
    parser = ConnectionParser()
    
    print("Loading connections...")
    connections = parser.parse_file_simple('sh_conn_detail.txt')
    
    print(f"Loaded {len(connections):,} connections")
    
    # Test flag-based elephant flow detection
    print("\n" + "="*60)
    print("FLAG-BASED ELEPHANT FLOW DETECTION")
    print("="*60)
    
    # Find connections with N3 (elephant-flow) flag
    elephant_flagged = parser.find_elephant_flows(
        min_uptime_hours=0,
        min_bytes=0,
        min_mbps=0,
        sort_by='bytes',
        include_flagged=True,
        include_offloaded=False
    )
    
    n3_flows = [f for f in elephant_flagged if f.get('elephant_flag_type') == 'N3']
    print(f"Connections with N3 (elephant-flow) flag: {len(n3_flows)}")
    
    if n3_flows:
        print("\nTop 5 N3 flagged flows:")
        for i, flow in enumerate(n3_flows[:5]):
            src = f"{flow.get('src_ip', 'N/A')}:{flow.get('src_port', 'N/A')}"
            dst = f"{flow.get('dst_ip', 'N/A')}:{flow.get('dst_port', 'N/A')}"
            bytes_gb = flow.get('bytes_int', 0) / 1e9
            rate_mbps = flow.get('mbps', 0)
            
            print(f"  {i+1}. {flow.get('protocol')} {src} -> {dst}")
            print(f"     Bytes: {bytes_gb:.1f}GB, Rate: {rate_mbps:.1f}Mbps, Uptime: {flow.get('uptime')}")
            print(f"     Flags: {flow.get('raw_flags')}")
    
    # Find offloaded connections
    print(f"\n" + "="*60)
    print("OFFLOADED FLOW DETECTION")
    print("="*60)
    
    offloaded_flows = parser.find_elephant_flows(
        min_uptime_hours=0,
        min_bytes=0,
        min_mbps=0,
        sort_by='bytes',
        include_flagged=False,
        include_offloaded=True
    )
    
    offloaded_only = [f for f in offloaded_flows if f.get('is_offloaded_elephant')]
    print(f"Offloaded connections (o flag): {len(offloaded_only)}")
    
    if offloaded_only:
        print("\nTop 5 offloaded flows:")
        for i, flow in enumerate(offloaded_only[:5]):
            src = f"{flow.get('src_ip', 'N/A')}:{flow.get('src_port', 'N/A')}"
            dst = f"{flow.get('dst_ip', 'N/A')}:{flow.get('dst_port', 'N/A')}"
            bytes_gb = flow.get('bytes_int', 0) / 1e9
            rate_mbps = flow.get('mbps', 0)
            
            print(f"  {i+1}. {flow.get('protocol')} {src} -> {dst}")
            print(f"     Bytes: {bytes_gb:.1f}GB, Rate: {rate_mbps:.1f}Mbps, Uptime: {flow.get('uptime')}")
            print(f"     Flags: {flow.get('raw_flags')}")
    
    # Test high-rate detection
    print(f"\n" + "="*60)
    print("HIGH-RATE FLOW DETECTION (>10 Mbps)")
    print("="*60)
    
    high_rate_flows = parser.find_elephant_flows(
        min_uptime_hours=0,
        min_bytes=0,
        min_mbps=10,  # >10 Mbps
        sort_by='rate',
        include_flagged=True,
        include_offloaded=True
    )
    
    print(f"High-rate flows (>10 Mbps): {len(high_rate_flows)}")
    
    if high_rate_flows:
        print("\nTop 5 highest rate flows:")
        for i, flow in enumerate(high_rate_flows[:5]):
            src = f"{flow.get('src_ip', 'N/A')}:{flow.get('src_port', 'N/A')}"
            dst = f"{flow.get('dst_ip', 'N/A')}:{flow.get('dst_port', 'N/A')}"
            bytes_gb = flow.get('bytes_int', 0) / 1e9
            rate_mbps = flow.get('mbps', 0)
            
            print(f"  {i+1}. {flow.get('protocol')} {src} -> {dst}")
            print(f"     Rate: {rate_mbps:.1f}Mbps, Bytes: {bytes_gb:.1f}GB, Uptime: {flow.get('uptime')}")
            print(f"     Flags: {flow.get('raw_flags')}")
            print(f"     Type: {flow.get('elephant_flow_type')}")
    
    # Summary of all detection methods
    print(f"\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Total connections: {len(connections):,}")
    print(f"N3 flagged (explicit elephant flows): {len(n3_flows):,}")
    print(f"Offloaded flows: {len(offloaded_only):,}")
    print(f"High-rate flows (>10 Mbps): {len(high_rate_flows):,}")
    
    # Export the most interesting findings
    if n3_flows:
        parser.export_elephant_flows(n3_flows, 'n3_flagged_elephant_flows.csv')
        print(f"Exported N3 flagged flows to: n3_flagged_elephant_flows.csv")
    
    if offloaded_only:
        parser.export_elephant_flows(offloaded_only, 'offloaded_elephant_flows.csv')
        print(f"Exported offloaded flows to: offloaded_elephant_flows.csv")
    
    if high_rate_flows:
        parser.export_elephant_flows(high_rate_flows[:100], 'high_rate_elephant_flows.csv')
        print(f"Exported top 100 high-rate flows to: high_rate_elephant_flows.csv")

if __name__ == "__main__":
    main()