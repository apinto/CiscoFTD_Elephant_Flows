#!/usr/bin/env python3
"""
Ultimate Elephant Flow Command Line Tool
Comprehensive elephant flow detection with all methods
"""

import sys
import argparse
from connection_parser import ConnectionParser

def create_parser():
    """Create command line argument parser"""
    parser = argparse.ArgumentParser(
        description='Ultimate Elephant Flow Detector for Cisco ASA',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Find N3 flagged elephant flows
  python3 ultimate_elephant_finder.py --flags-only --sort bytes

  # Find offloaded flows
  python3 ultimate_elephant_finder.py --offloaded-only --sort bytes

  # Find high-rate flows >50 Mbps
  python3 ultimate_elephant_finder.py --min-rate 50 --sort rate

  # Comprehensive analysis (all methods)
  python3 ultimate_elephant_finder.py --min-hours 1 --min-mb 100 --min-rate 1 --include-flags --include-offloaded

  # Traditional elephant flows (long-lived + high volume)
  python3 ultimate_elephant_finder.py --min-hours 24 --min-mb 1000 --sort both
        ''')
    
    parser.add_argument('--min-hours', type=float, default=0,
                       help='Minimum uptime in hours (default: 0)')
    parser.add_argument('--min-mb', type=float, default=0,
                       help='Minimum bytes in MB (default: 0)')
    parser.add_argument('--min-rate', type=float, default=0,
                       help='Minimum traffic rate in Mbps (default: 0)')
    
    parser.add_argument('--sort', choices=['uptime', 'bytes', 'rate', 'both'], default='bytes',
                       help='Sort criteria (default: bytes)')
    parser.add_argument('--limit', type=int, default=20,
                       help='Number of results to show (default: 20)')
    
    parser.add_argument('--flags-only', action='store_true',
                       help='Only show connections with elephant flags (N3, N4, N5, N6)')
    parser.add_argument('--offloaded-only', action='store_true',
                       help='Only show offloaded connections (o flag)')
    parser.add_argument('--include-flags', action='store_true',
                       help='Include flag-based elephant flows in results')
    parser.add_argument('--include-offloaded', action='store_true',
                       help='Include offloaded flows in results')
    
    parser.add_argument('--detailed', action='store_true',
                       help='Show detailed analysis of top flows')
    parser.add_argument('--export', type=str,
                       help='Export results to CSV file')
    parser.add_argument('--quiet', action='store_true',
                       help='Minimal output, just show results')
    
    return parser

def main():
    """Main function"""
    args = create_parser().parse_args()
    
    # Load parser and data
    if not args.quiet:
        print("="*80)
        print("ULTIMATE ELEPHANT FLOW DETECTOR")
        print("="*80)
        print("Loading connections...")
    
    conn_parser = ConnectionParser()
    connections = conn_parser.parse_file_simple('sh_conn_detail.txt')
    
    if not connections:
        print("Error: No connections found")
        return 1
    
    if not args.quiet:
        print(f"Loaded {len(connections):,} connections")
    
    # Determine detection parameters
    min_bytes = int(args.min_mb * 1024 * 1024)
    
    # Handle special modes
    if args.flags_only:
        include_flagged = True
        include_offloaded = False
        min_uptime_hours = 0
        min_bytes = 0
        min_mbps = 0
        # Override to ensure we only get flagged flows
        special_mode = 'flags_only'
    elif args.offloaded_only:
        include_flagged = False
        include_offloaded = True
        min_uptime_hours = 0
        min_bytes = 0
        min_mbps = 0
        special_mode = 'offloaded_only'
    else:
        include_flagged = args.include_flags
        include_offloaded = args.include_offloaded
        min_uptime_hours = args.min_hours
        min_mbps = args.min_rate
        special_mode = None
    
    # Find elephant flows
    elephant_flows = conn_parser.find_elephant_flows(
        min_uptime_hours=min_uptime_hours,
        min_bytes=min_bytes,
        min_mbps=min_mbps,
        sort_by=args.sort,
        include_flagged=include_flagged,
        include_offloaded=include_offloaded
    )
    
    # Apply special filtering if needed
    if special_mode == 'flags_only':
        # Only keep flows that actually have elephant flags
        elephant_flows = [f for f in elephant_flows if f.get('is_flagged_elephant', False)]
    elif special_mode == 'offloaded_only':
        # Only keep flows that are actually offloaded
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
        print(f"  Min uptime: {min_uptime_hours} hours")
        print(f"  Min bytes: {args.min_mb} MB ({min_bytes:,} bytes)")
        print(f"  Min rate: {min_mbps} Mbps")
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
    
    # Show flows
    show_flags = not args.quiet
    conn_parser.print_elephant_flows(elephant_flows, limit=args.limit, show_flags=show_flags)
    
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