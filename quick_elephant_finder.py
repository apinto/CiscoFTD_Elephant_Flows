#!/usr/bin/env python3
"""
Quick Elephant Flow Finder
Simple command-line tool to find elephant flows with custom parameters
"""

import sys
from connection_parser import ConnectionParser

def print_usage():
    """Print usage information"""
    print("Usage: python3 quick_elephant_finder.py [min_hours] [min_mb] [sort_by] [limit]")
    print()
    print("Parameters:")
    print("  min_hours: Minimum uptime in hours (default: 1)")
    print("  min_mb:    Minimum bytes in MB (default: 100)")
    print("  sort_by:   Sort by 'uptime', 'bytes', or 'both' (default: 'bytes')")
    print("  limit:     Number of results to show (default: 20)")
    print()
    print("Examples:")
    print("  python3 quick_elephant_finder.py 24 1000 bytes 10")
    print("  python3 quick_elephant_finder.py 0 500 bytes 15")
    print("  python3 quick_elephant_finder.py 12 0 uptime 25")

def main():
    """Main function"""
    # Default parameters
    min_hours = 1
    min_mb = 100
    sort_by = 'bytes'
    limit = 20
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h', '--help', 'help']:
            print_usage()
            return
        
        try:
            if len(sys.argv) > 1:
                min_hours = float(sys.argv[1])
            if len(sys.argv) > 2:
                min_mb = float(sys.argv[2])
            if len(sys.argv) > 3:
                sort_by = sys.argv[3].lower()
            if len(sys.argv) > 4:
                limit = int(sys.argv[4])
        except ValueError:
            print("Error: Invalid parameters")
            print_usage()
            return
    
    # Validate sort_by parameter
    if sort_by not in ['uptime', 'bytes', 'both']:
        print(f"Error: Invalid sort_by parameter '{sort_by}'. Use 'uptime', 'bytes', or 'both'")
        return
    
    # Convert MB to bytes
    min_bytes = int(min_mb * 1024 * 1024)
    
    print("="*80)
    print("QUICK ELEPHANT FLOW FINDER")
    print("="*80)
    print(f"Parameters:")
    print(f"  Min uptime: {min_hours} hours")
    print(f"  Min bytes: {min_mb} MB ({min_bytes:,} bytes)")
    print(f"  Sort by: {sort_by}")
    print(f"  Show top: {limit} results")
    print()
    
    # Load and parse data
    print("Loading connections...")
    parser = ConnectionParser()
    connections = parser.parse_file_simple('sh_conn_detail.txt')
    
    if not connections:
        print("Error: No connections found")
        return
    
    print(f"Loaded {len(connections):,} connections")
    
    # Find elephant flows
    print("Searching for elephant flows...")
    elephant_flows = parser.find_elephant_flows(
        min_uptime_hours=min_hours,
        min_bytes=min_bytes,
        sort_by=sort_by
    )
    
    if elephant_flows:
        # Get and print statistics
        stats = parser.get_elephant_flow_stats(elephant_flows)
        
        print(f"\nRESULTS:")
        print(f"Found {len(elephant_flows):,} elephant flows ({stats['percentage_of_total']:.2f}% of total)")
        print(f"  - Long-lived only: {stats['long_lived_only']:,}")
        print(f"  - High-volume only: {stats['high_volume_only']:,}")
        print(f"  - Both criteria: {stats['both_criteria']:,}")
        print(f"  - Total bytes: {stats['total_bytes_elephant']:,}")
        print(f"  - Average uptime: {stats['avg_uptime_hours']:.1f} hours")
        print(f"  - Max uptime: {stats['max_uptime_hours']:.1f} hours")
        print(f"  - Max bytes: {stats['max_bytes']:,}")
        
        # Show top elephant flows
        parser.print_elephant_flows(elephant_flows, limit=limit)
        
        # Export results
        filename = f"elephant_flows_{min_hours}h_{min_mb}mb_{sort_by}.csv"
        parser.export_elephant_flows(elephant_flows, filename)
        
        print(f"\nResults exported to: {filename}")
    else:
        print("No elephant flows found with the specified criteria")
        print("Try reducing the thresholds or use 0 for no limit")

if __name__ == "__main__":
    main()