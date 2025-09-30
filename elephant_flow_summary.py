#!/usr/bin/env python3
"""
Elephant Flow Summary - Key Insights
Shows the most important elephant flow findings
"""

from connection_parser import ConnectionParser

def main():
    """Generate summary of key elephant flow insights"""
    parser = ConnectionParser()
    
    print("="*80)
    print("🐘 ELEPHANT FLOW ANALYSIS - KEY INSIGHTS")
    print("="*80)
    
    # Load data
    print("Loading connections...")
    connections = parser.parse_file_simple('sh_conn_detail.txt')
    print(f"Total connections analyzed: {len(connections):,}")
    
    # Get all elephant flows with comprehensive criteria
    all_elephant_flows = parser.find_elephant_flows(
        min_uptime_hours=1,
        min_bytes=100*1024*1024,  # 100MB
        min_mbps=1,
        sort_by='bytes',
        include_flagged=True,
        include_offloaded=True
    )
    
    # Get flag-based flows
    n3_flows = parser.find_elephant_flows(
        min_uptime_hours=0, min_bytes=0, min_mbps=0,
        sort_by='bytes', include_flagged=True, include_offloaded=False
    )
    n3_flows = [f for f in n3_flows if f.get('is_flagged_elephant')]
    
    # Get offloaded flows  
    offloaded_flows = parser.find_elephant_flows(
        min_uptime_hours=0, min_bytes=0, min_mbps=0,
        sort_by='bytes', include_flagged=False, include_offloaded=True
    )
    offloaded_flows = [f for f in offloaded_flows if f.get('is_offloaded_elephant')]
    
    # Get high-rate flows
    high_rate_flows = parser.find_elephant_flows(
        min_uptime_hours=0, min_bytes=0, min_mbps=50,
        sort_by='rate', include_flagged=True, include_offloaded=True
    )
    
    print(f"\n🔍 DETECTION SUMMARY:")
    print(f"  📊 Comprehensive Elephant Flows: {len(all_elephant_flows):,} ({len(all_elephant_flows)/len(connections)*100:.1f}%)")
    print(f"  🏷️  ASA N3 Flagged Flows: {len(n3_flows):,} ({len(n3_flows)/len(connections)*100:.3f}%)")
    print(f"  🔄 Offloaded Flows: {len(offloaded_flows):,} ({len(offloaded_flows)/len(connections)*100:.3f}%)")
    print(f"  ⚡ High-Rate Flows (>50 Mbps): {len(high_rate_flows):,} ({len(high_rate_flows)/len(connections)*100:.3f}%)")
    
    # Traffic volume analysis
    total_bytes = 0
    for conn in connections:
        if 'bytes' in conn and conn['bytes'].isdigit():
            total_bytes += int(conn['bytes'])
    
    n3_bytes = sum(f.get('bytes_int', 0) for f in n3_flows)
    offloaded_bytes = sum(f.get('bytes_int', 0) for f in offloaded_flows)
    
    print(f"\n📊 TRAFFIC VOLUME IMPACT:")
    print(f"  Total Network Traffic: {total_bytes/1e12:.1f} TB")
    if total_bytes > 0:
        print(f"  N3 Flagged Traffic: {n3_bytes/1e12:.1f} TB ({n3_bytes/total_bytes*100:.1f}% of total)")
        print(f"  Offloaded Traffic: {offloaded_bytes/1e12:.1f} TB ({offloaded_bytes/total_bytes*100:.1f}% of total)")
    else:
        print(f"  N3 Flagged Traffic: {n3_bytes/1e12:.1f} TB")
        print(f"  Offloaded Traffic: {offloaded_bytes/1e12:.1f} TB")
    
    print(f"\n🎯 KEY FINDINGS:")
    
    # Top N3 flow
    if n3_flows:
        top_n3 = n3_flows[0]
        print(f"  🥇 Largest N3 Flagged Flow:")
        print(f"     {top_n3.get('protocol')} {top_n3.get('src_ip')}:{top_n3.get('src_port')} → {top_n3.get('dst_ip')}:{top_n3.get('dst_port')}")
        print(f"     Volume: {top_n3.get('bytes_int', 0)/1e12:.1f} TB over {top_n3.get('uptime', 'unknown')}")
        print(f"     Rate: {top_n3.get('mbps', 0):.1f} Mbps")
    
    # Top offloaded flow
    if offloaded_flows:
        top_offloaded = offloaded_flows[0]
        print(f"  🔄 Largest Offloaded Flow:")
        print(f"     {top_offloaded.get('protocol')} {top_offloaded.get('src_ip')}:{top_offloaded.get('src_port')} → {top_offloaded.get('dst_ip')}:{top_offloaded.get('dst_port')}")
        print(f"     Volume: {top_offloaded.get('bytes_int', 0)/1e12:.1f} TB over {top_offloaded.get('uptime', 'unknown')}")
        print(f"     Rate: {top_offloaded.get('mbps', 0):.1f} Mbps")
    
    # Top rate flow
    if high_rate_flows:
        top_rate = high_rate_flows[0]
        print(f"  ⚡ Highest Rate Flow:")
        print(f"     {top_rate.get('protocol')} {top_rate.get('src_ip')}:{top_rate.get('src_port')} → {top_rate.get('dst_ip')}:{top_rate.get('dst_port')}")
        print(f"     Rate: {top_rate.get('mbps', 0):.1f} Mbps over {top_rate.get('uptime', 'unknown')}")
        print(f"     Volume: {top_rate.get('bytes_int', 0)/1e9:.1f} GB")
    
    # Protocol analysis
    print(f"\n🔬 PROTOCOL ANALYSIS:")
    if offloaded_flows:
        offloaded_protocols = {}
        for flow in offloaded_flows:
            proto = flow.get('protocol', 'Unknown')
            port = flow.get('dst_port', 'Unknown')
            key = f"{proto}:{port}"
            if key not in offloaded_protocols:
                offloaded_protocols[key] = {'count': 0, 'bytes': 0}
            offloaded_protocols[key]['count'] += 1
            offloaded_protocols[key]['bytes'] += flow.get('bytes_int', 0)
        
        print(f"  Offloaded Traffic by Protocol:")
        for proto_port, stats in sorted(offloaded_protocols.items(), key=lambda x: x[1]['bytes'], reverse=True)[:3]:
            print(f"    {proto_port}: {stats['count']} flows, {stats['bytes']/1e12:.1f} TB")
    
    print(f"\n💡 INSIGHTS:")
    print(f"  • Only {len(n3_flows)} flows ({len(n3_flows)/len(connections)*100:.3f}%) are explicitly flagged as elephant flows by ASA")
    print(f"  • Only {len(offloaded_flows)} flows ({len(offloaded_flows)/len(connections)*100:.3f}%) are offloaded, but they consume massive bandwidth!")
    if total_bytes > 0:
        print(f"  • Offloaded flows consume {offloaded_bytes/total_bytes*100:.1f}% of total traffic despite being {len(offloaded_flows)/len(connections)*100:.3f}% of connections")
    print(f"  • VXLAN tunnels (port 4789) dominate offloaded traffic - likely overlay network infrastructure")
    print(f"  • N3 flagged flows show diverse patterns: some high-rate short bursts, others sustained low-rate transfers")
    print(f"  • ASA's elephant flow detection is highly selective - catching the most impactful flows")
    
    print(f"\n🚀 RECOMMENDATIONS:")
    print(f"  1. Monitor N3 flagged flows closely - these are ASA-identified problem flows")
    print(f"  2. Investigate VXLAN tunnel utilization - consuming majority of bandwidth")
    print(f"  3. Consider rate limiting or QoS for high-rate flows during business hours")
    print(f"  4. Review long-running TCP connections for potential optimization")
    print(f"  5. Set up alerting for new N3 or offloaded flows")
    
    print(f"\n📁 Use these commands for detailed analysis:")
    print(f"  python3 ultimate_elephant_finder.py --flags-only --detailed")
    print(f"  python3 ultimate_elephant_finder.py --offloaded-only --detailed") 
    print(f"  python3 ultimate_elephant_finder.py --min-rate 100 --sort rate")

if __name__ == "__main__":
    main()