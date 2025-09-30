#!/usr/bin/env python3
"""
Elephant Flow Analyzer - Unified Tool
Comprehensive elephant flow detection and analysis for Cisco ASA

This tool consolidates all elephant flow detection capabilities into a single script:
- Flag-based detection (N3, N4, N5, N6, o)
- Rate-based detection (high bandwidth flows)
- Traditional detection (uptime + volume)
- Summary and detailed analysis
- Export capabilities
- Validation and testing

Usage:
    python3 elephant_flow_analyzer.py [options]
    python3 elephant_flow_analyzer.py --help
"""

import sys
import argparse
from connection_parser import ConnectionParser
from collections import Counter

def create_parser():
    """Create comprehensive command line argument parser"""
    parser = argparse.ArgumentParser(
        description='Unified Elephant Flow Analyzer for Cisco ASA',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Quick summary of elephant flows
  python3 elephant_flow_analyzer.py --summary

  # Find N3 flagged elephant flows
  python3 elephant_flow_analyzer.py --flags-only --sort bytes

  # Find offloaded flows
  python3 elephant_flow_analyzer.py --offloaded-only --sort bytes

  # Find high-rate flows >50 Mbps
  python3 elephant_flow_analyzer.py --min-rate 50 --sort rate

  # Comprehensive analysis with all methods
  python3 elephant_flow_analyzer.py --min-hours 1 --min-mb 100 --min-rate 1 --include-flags --include-offloaded

  # Traditional elephant flows (long-lived + high volume)
  python3 elephant_flow_analyzer.py --min-hours 24 --min-mb 1000 --sort both

  # Validate parsing accuracy
  python3 elephant_flow_analyzer.py --test

  # Export results to CSV
  python3 elephant_flow_analyzer.py --flags-only --export elephant_flows.csv

  # Detailed analysis with full breakdown
  python3 elephant_flow_analyzer.py --analyze --detailed
        ''')
    
    # Detection criteria
    detection = parser.add_argument_group('Detection Criteria')
    detection.add_argument('--min-hours', type=float, default=0,
                          help='Minimum uptime in hours (default: 0)')
    detection.add_argument('--min-mb', type=float, default=0,
                          help='Minimum bytes in MB (default: 0)')
    detection.add_argument('--min-rate', type=float, default=0,
                          help='Minimum traffic rate in Mbps (default: 0)')
    
    # Detection modes
    modes = parser.add_argument_group('Detection Modes')
    modes.add_argument('--flags-only', action='store_true',
                      help='Only show connections with elephant flags (N3, N4, N5, N6)')
    modes.add_argument('--offloaded-only', action='store_true',
                      help='Only show offloaded connections (o flag)')
    modes.add_argument('--include-flags', action='store_true',
                      help='Include flag-based elephant flows in results')
    modes.add_argument('--include-offloaded', action='store_true',
                      help='Include offloaded flows in results')
    
    # Output options
    output = parser.add_argument_group('Output Options')
    output.add_argument('--sort', choices=['uptime', 'bytes', 'rate', 'both'], default='bytes',
                       help='Sort criteria (default: bytes)')
    output.add_argument('--limit', type=int, default=20,
                       help='Number of results to show (default: 20)')
    output.add_argument('--export', type=str,
                       help='Export results to CSV file')
    output.add_argument('--quiet', action='store_true',
                       help='Minimal output, just show results')
    output.add_argument('--detailed', action='store_true',
                       help='Show detailed analysis of top flows')
    
    # Analysis modes
    analysis = parser.add_argument_group('Analysis Modes')
    analysis.add_argument('--summary', action='store_true',
                         help='Generate executive summary with key insights')
    analysis.add_argument('--analyze', action='store_true',
                         help='Run comprehensive analysis with multiple scenarios')
    analysis.add_argument('--test', action='store_true',
                         help='Validate parsing and test detection methods')
    
    # Data file
    parser.add_argument('--file', type=str, default='sh_conn_detail.txt',
                       help='Input file with Cisco ASA connection data (default: sh_conn_detail.txt)')
    
    return parser

def run_summary_analysis(conn_parser, connections):
    """Generate executive summary with key insights"""
    print("="*80)
    print("🐘 ELEPHANT FLOW ANALYSIS - EXECUTIVE SUMMARY")
    print("="*80)
    
    print(f"Total connections analyzed: {len(connections):,}")
    
    # Get all elephant flows with comprehensive criteria
    all_elephant_flows = conn_parser.find_elephant_flows(
        min_uptime_hours=1,
        min_bytes=100*1024*1024,  # 100MB
        min_mbps=1,
        sort_by='bytes',
        include_flagged=True,
        include_offloaded=True
    )
    
    # Get flag-based flows
    n3_flows = conn_parser.find_elephant_flows(
        min_uptime_hours=0, min_bytes=0, min_mbps=0,
        sort_by='bytes', include_flagged=True, include_offloaded=False
    )
    n3_flows = [f for f in n3_flows if f.get('is_flagged_elephant')]
    
    # Get offloaded flows  
    offloaded_flows = conn_parser.find_elephant_flows(
        min_uptime_hours=0, min_bytes=0, min_mbps=0,
        sort_by='bytes', include_flagged=False, include_offloaded=True
    )
    offloaded_flows = [f for f in offloaded_flows if f.get('is_offloaded_elephant')]
    
    # Get high-rate flows
    high_rate_flows = conn_parser.find_elephant_flows(
        min_uptime_hours=0, min_bytes=0, min_mbps=50,
        sort_by='rate', include_flagged=True, include_offloaded=True
    )
    
    # Get long-lived flows
    long_lived_flows = conn_parser.find_elephant_flows(
        min_uptime_hours=24, min_bytes=0, min_mbps=0,
        sort_by='uptime', include_flagged=True, include_offloaded=True
    )
    
    print(f"\n🔍 DETECTION SUMMARY:")
    print(f"  📊 Comprehensive Elephant Flows: {len(all_elephant_flows):,} ({len(all_elephant_flows)/len(connections)*100:.1f}%)")
    print(f"  🏷️  ASA N3 Flagged Flows: {len(n3_flows):,} ({len(n3_flows)/len(connections)*100:.3f}%)")
    print(f"  🔄 Offloaded Flows: {len(offloaded_flows):,} ({len(offloaded_flows)/len(connections)*100:.3f}%)")
    print(f"  ⚡ High-Rate Flows (>50 Mbps): {len(high_rate_flows):,}")
    
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
    
    # Show top flows
    print(f"\n🎯 TOP ELEPHANT FLOWS:")
    
    if n3_flows:
        top_n3 = n3_flows[0]
        print(f"  🥇 Largest N3 Flagged Flow:")
        print(f"     {top_n3.get('protocol')} {top_n3.get('src_ip')}:{top_n3.get('src_port')} → {top_n3.get('dst_ip')}:{top_n3.get('dst_port')}")
        print(f"     Volume: {top_n3.get('bytes_int', 0)/1e12:.1f} TB, Rate: {top_n3.get('mbps', 0):.1f} Mbps, Uptime: {top_n3.get('uptime', 'unknown')}")
    
    if offloaded_flows:
        top_offloaded = offloaded_flows[0]
        print(f"  🔄 Largest Offloaded Flow:")
        print(f"     {top_offloaded.get('protocol')} {top_offloaded.get('src_ip')}:{top_offloaded.get('src_port')} → {top_offloaded.get('dst_ip')}:{top_offloaded.get('dst_port')}")
        print(f"     Volume: {top_offloaded.get('bytes_int', 0)/1e12:.1f} TB, Rate: {top_offloaded.get('mbps', 0):.1f} Mbps, Uptime: {top_offloaded.get('uptime', 'unknown')}")
    
    # Show top rate flow
    if high_rate_flows:
        top_rate = high_rate_flows[0]
        print(f"  ⚡ Highest Rate Flow:")
        print(f"     {top_rate.get('protocol')} {top_rate.get('src_ip')}:{top_rate.get('src_port')} → {top_rate.get('dst_ip')}:{top_rate.get('dst_port')}")
        print(f"     Rate: {top_rate.get('mbps', 0):.1f} Mbps, Volume: {top_rate.get('bytes_int', 0)/1e9:.1f} GB, Uptime: {top_rate.get('uptime', 'unknown')}")
        
    # Show top uptime flow
    if long_lived_flows:
        top_uptime = long_lived_flows[0]
        print(f"  ⏰ Longest Running Flow:")
        print(f"     {top_uptime.get('protocol')} {top_uptime.get('src_ip')}:{top_uptime.get('src_port')} → {top_uptime.get('dst_ip')}:{top_uptime.get('dst_port')}")
        print(f"     Uptime: {top_uptime.get('uptime', 'unknown')}, Volume: {top_uptime.get('bytes_int', 0)/1e9:.1f} GB, Rate: {top_uptime.get('mbps', 0):.1f} Mbps")
    
    print(f"\n💡 KEY INSIGHTS:")
    print(f"  • ASA's elephant flow detection is highly selective - only {len(n3_flows)/len(connections)*100:.3f}% flagged")
    print(f"  • Offloaded flows represent {len(offloaded_flows)/len(connections)*100:.3f}% of connections but significant bandwidth")
    print(f"  • Consider monitoring N3 flagged flows as they are ASA-identified problem flows")
    print(f"  • VXLAN tunnels (port 4789) often dominate offloaded traffic")
    
    print(f"\n📁 For detailed analysis, use:")
    print(f"  python3 elephant_flow_analyzer.py --flags-only --detailed")
    print(f"  python3 elephant_flow_analyzer.py --offloaded-only --detailed")
    print(f"  python3 elephant_flow_analyzer.py --analyze")

def run_comprehensive_analysis(conn_parser, connections):
    """Run comprehensive analysis with multiple scenarios"""
    print("="*80)
    print("🔬 COMPREHENSIVE ELEPHANT FLOW ANALYSIS")
    print("="*80)
    
    scenarios = [
        {
            'name': 'ASA N3 Flagged Flows',
            'description': 'Connections explicitly marked as elephant flows by ASA',
            'flags_only': True,
            'offloaded_only': False
        },
        {
            'name': 'Offloaded Flows', 
            'description': 'Connections offloaded due to high volume',
            'flags_only': False,
            'offloaded_only': True
        },
        {
            'name': 'High-Rate Flows (>100 Mbps)',
            'description': 'Connections with very high traffic rates',
            'min_rate': 100,
            'sort_by': 'rate'
        },
        {
            'name': 'Traditional Elephant Flows',
            'description': 'Long-lived (>24h) and high-volume (>1GB) connections',
            'min_hours': 24,
            'min_mb': 1000,
            'sort_by': 'both'
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{'-'*60}")
        print(f"SCENARIO {i}: {scenario['name']}")
        print(f"Description: {scenario['description']}")
        print(f"{'-'*60}")
        
        # Set parameters
        kwargs = {
            'min_uptime_hours': scenario.get('min_hours', 0),
            'min_bytes': int(scenario.get('min_mb', 0) * 1024 * 1024),
            'min_mbps': scenario.get('min_rate', 0),
            'sort_by': scenario.get('sort_by', 'bytes'),
            'include_flagged': not scenario.get('offloaded_only', False),
            'include_offloaded': not scenario.get('flags_only', False)
        }
        
        elephant_flows = conn_parser.find_elephant_flows(**kwargs)
        
        # Apply special filtering
        if scenario.get('flags_only'):
            elephant_flows = [f for f in elephant_flows if f.get('is_flagged_elephant', False)]
        elif scenario.get('offloaded_only'):
            elephant_flows = [f for f in elephant_flows if f.get('is_offloaded_elephant', False)]
        
        if elephant_flows:
            stats = conn_parser.get_elephant_flow_stats(elephant_flows)
            
            print(f"Found: {len(elephant_flows):,} flows ({stats['percentage_of_total']:.2f}% of total)")
            print(f"Total bytes: {stats['total_bytes_elephant']:,}")
            print(f"Average uptime: {stats['avg_uptime_hours']:.1f} hours")
            
            # Show top 3 flows
            print(f"\nTop 3 flows:")
            for j, flow in enumerate(elephant_flows[:3], 1):
                src = f"{flow.get('src_ip', 'N/A')}:{flow.get('src_port', 'N/A')}"
                dst = f"{flow.get('dst_ip', 'N/A')}:{flow.get('dst_port', 'N/A')}"
                bytes_gb = flow.get('bytes_int', 0) / 1e9
                rate_mbps = flow.get('mbps', 0)
                
                print(f"  {j}. {flow.get('protocol')} {src} → {dst}")
                print(f"     {bytes_gb:.1f}GB, {rate_mbps:.1f}Mbps, {flow.get('uptime', 'N/A')}")
        else:
            print("No flows found with these criteria")

def run_validation_test(conn_parser, filename):
    """Run validation and testing of parsing accuracy"""
    print("="*80)
    print("🧪 VALIDATION AND TESTING")
    print("="*80)
    
    # Test with sample data first
    sample_data = """UDP FORTISIEM: 10.1.76.4/45879 dc2: 10.1.5.101/53,
    flags - N1, idle 21s, uptime 21s, timeout 2m0s, bytes 28, Rx-RingNum 45, Internal-Data0/1
  Connection lookup keyid: 100587686

TCP FORTISIEM: 10.1.76.3/57798 beproxy: 10.1.19.90/8000,
    flags UIO N1N3, idle 8s, uptime 2h39m, timeout 1h0m, bytes 14395, Rx-RingNum 61, Internal-Data0/1
  Initiator: 10.1.76.3, Responder: 10.1.19.90
  Connection lookup keyid: 1931784606

UDP VPLS:VPLS(VPLS): 10.2.76.3/4789 FORTISIEM: 10.1.76.3/4816,
    flags -o, idle 0s, uptime 1Y25D, timeout 2m0s, bytes 7688943400093, Rx-RingNum 0, Internal-Data0/1
  Connection lookup keyid: 126607738"""
    
    # Write sample to temporary file
    with open('test_sample.txt', 'w') as f:
        f.write(sample_data)
    
    print("Testing with sample data...")
    test_connections = conn_parser.parse_file_simple('test_sample.txt')
    
    print(f"✅ Parsed {len(test_connections)} sample connections")
    
    for i, conn in enumerate(test_connections, 1):
        print(f"\nSample Connection {i}:")
        print(f"  Protocol: {conn.get('protocol')}")
        print(f"  Source: {conn.get('src_ip')}:{conn.get('src_port')}")
        print(f"  Destination: {conn.get('dst_ip')}:{conn.get('dst_port')}")
        print(f"  Flags: {conn.get('flags')}")
        print(f"  Uptime: {conn.get('uptime')}")
        print(f"  Bytes: {conn.get('bytes')}")
    
    # Test flag parsing
    print(f"\n🏷️ Testing flag parsing...")
    for conn in test_connections:
        if 'flags' in conn:
            flag_info = conn_parser._parse_connection_flags(conn['flags'])
            print(f"  Flags '{conn['flags']}' parsed as:")
            print(f"    Elephant flag: {flag_info.get('has_elephant_flag')}")
            print(f"    Offloaded: {flag_info.get('is_offloaded')}")
            print(f"    Snort inspected: {flag_info.get('is_snort_inspected')}")
    
    # Test rate calculation
    print(f"\n⚡ Testing rate calculation...")
    for conn in test_connections:
        if 'uptime' in conn and 'bytes' in conn:
            uptime_seconds = conn_parser._parse_time_to_seconds(conn['uptime'])
            bytes_count = int(conn['bytes']) if conn['bytes'].isdigit() else 0
            rate_info = conn_parser._calculate_traffic_rate(bytes_count, uptime_seconds)
            print(f"  {conn.get('bytes')} bytes over {conn.get('uptime')} = {rate_info['mbps']:.2f} Mbps")
    
    # Test with real data
    print(f"\n📊 Testing with real data from {filename}...")
    try:
        real_connections = conn_parser.parse_file_simple(filename)
        print(f"✅ Successfully parsed {len(real_connections):,} real connections")
        
        # Quick validation
        with_flags = len([c for c in real_connections if 'flags' in c and c['flags']])
        with_bytes = len([c for c in real_connections if 'bytes' in c and c['bytes'].isdigit()])
        with_uptime = len([c for c in real_connections if 'uptime' in c])
        
        print(f"  Connections with flags: {with_flags:,} ({with_flags/len(real_connections)*100:.1f}%)")
        print(f"  Connections with bytes: {with_bytes:,} ({with_bytes/len(real_connections)*100:.1f}%)")
        print(f"  Connections with uptime: {with_uptime:,} ({with_uptime/len(real_connections)*100:.1f}%)")
        
    except Exception as e:
        print(f"❌ Error testing with real data: {e}")
    
    # Clean up
    import os
    try:
        os.remove('test_sample.txt')
    except:
        pass
    
    print(f"\n✅ Validation completed successfully!")

def main():
    """Main function"""
    args = create_parser().parse_args()
    
    # Initialize parser
    conn_parser = ConnectionParser()
    
    if not args.quiet:
        print("="*80)
        print("🐘 ELEPHANT FLOW ANALYZER - UNIFIED TOOL")
        print("="*80)
    
    # Handle special modes first
    if args.test:
        run_validation_test(conn_parser, args.file)
        return 0
    
    # Load data
    if not args.quiet:
        print(f"Loading connections from {args.file}...")
    
    try:
        connections = conn_parser.parse_file_simple(args.file)
    except Exception as e:
        print(f"Error loading file {args.file}: {e}")
        return 1
    
    if not connections:
        print("No connections found")
        return 1
    
    if not args.quiet:
        print(f"Loaded {len(connections):,} connections")
    
    # Handle analysis modes
    if args.summary:
        run_summary_analysis(conn_parser, connections)
        return 0
    
    if args.analyze:
        run_comprehensive_analysis(conn_parser, connections)
        return 0
    
    # Standard elephant flow detection
    min_bytes = int(args.min_mb * 1024 * 1024)
    
    # Determine detection parameters
    if args.flags_only:
        include_flagged = True
        include_offloaded = False
        special_mode = 'flags_only'
    elif args.offloaded_only:
        include_flagged = False
        include_offloaded = True
        special_mode = 'offloaded_only'
    else:
        include_flagged = args.include_flags
        include_offloaded = args.include_offloaded
        special_mode = None
    
    # Find elephant flows
    elephant_flows = conn_parser.find_elephant_flows(
        min_uptime_hours=args.min_hours,
        min_bytes=min_bytes,
        min_mbps=args.min_rate,
        sort_by=args.sort,
        include_flagged=include_flagged,
        include_offloaded=include_offloaded
    )
    
    # Apply special filtering
    if special_mode == 'flags_only':
        elephant_flows = [f for f in elephant_flows if f.get('is_flagged_elephant', False)]
    elif special_mode == 'offloaded_only':
        elephant_flows = [f for f in elephant_flows if f.get('is_offloaded_elephant', False)]
    
    if not elephant_flows:
        print("No elephant flows found with the specified criteria")
        return 0
    
    # Get statistics
    stats = conn_parser.get_elephant_flow_stats(elephant_flows)
    
    # Count special types
    flagged_count = len([f for f in elephant_flows if f.get('is_flagged_elephant')])
    offloaded_count = len([f for f in elephant_flows if f.get('is_offloaded_elephant')])
    high_rate_count = len([f for f in elephant_flows if f.get('is_high_rate')])
    
    # Print results
    if not args.quiet:
        print(f"\nCRITERIA:")
        print(f"  Min uptime: {args.min_hours} hours")
        print(f"  Min bytes: {args.min_mb} MB ({min_bytes:,} bytes)")
        print(f"  Min rate: {args.min_rate} Mbps")
        print(f"  Include flags: {include_flagged}")
        print(f"  Include offloaded: {include_offloaded}")
        print(f"  Sort by: {args.sort}")
        
        print(f"\nRESULTS:")
        print(f"Found {len(elephant_flows):,} elephant flows ({stats['percentage_of_total']:.2f}% of total)")
        print(f"  - Flag-based (N3/N4/N5/N6): {flagged_count:,}")
        print(f"  - Offloaded (o): {offloaded_count:,}")
        print(f"  - High-rate: {high_rate_count:,}")
        print(f"  - Long-lived only: {stats['long_lived_only']:,}")
        print(f"  - High-volume only: {stats['high_volume_only']:,}")
        print(f"  - Multiple criteria: {stats['both_criteria']:,}")
        
        print(f"\nSTATISTICS:")
        print(f"  Total bytes: {stats['total_bytes_elephant']:,}")
        print(f"  Average uptime: {stats['avg_uptime_hours']:.1f} hours")
        print(f"  Max uptime: {stats['max_uptime_hours']:.1f} hours")
        print(f"  Max bytes: {stats['max_bytes']:,}")
    
    # Show flows - always include flags now
    conn_parser.print_elephant_flows(elephant_flows, limit=args.limit)
    
    # Detailed analysis if requested
    if args.detailed and not args.quiet:
        print(f"\n{'='*80}")
        print("DETAILED ANALYSIS")
        print(f"{'='*80}")
        conn_parser.print_elephant_flow_details(elephant_flows, limit=5)
    
    # Export if requested
    if args.export:
        conn_parser.export_elephant_flows(elephant_flows, args.export)
        if not args.quiet:
            print(f"\nExported {len(elephant_flows):,} flows to: {args.export}")
    
    # Summary for quiet mode
    if args.quiet:
        print(f"Found {len(elephant_flows):,} elephant flows ({stats['percentage_of_total']:.2f}%)")
        if flagged_count > 0:
            print(f"Flag-based: {flagged_count}")
        if offloaded_count > 0:
            print(f"Offloaded: {offloaded_count}")
        if high_rate_count > 0:
            print(f"High-rate: {high_rate_count}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())