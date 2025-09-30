#!/usr/bin/env python3
"""
Elephant Flow Detection Script
Finds long-lived and high-volume connections in Cisco ASA data
"""

from connection_parser import ConnectionParser

def main():
    """Main function to find and analyze elephant flows"""
    parser = ConnectionParser()
    
    print("Loading and parsing connections...")
    connections = parser.parse_file_simple('sh_conn_detail.txt')
    
    if not connections:
        print("No connections found")
        return
    
    print(f"Loaded {len(connections)} connections")
    
    # Different elephant flow criteria to test
    test_scenarios = [
        {
            'name': 'High Volume (>100MB)',
            'min_uptime_hours': 0,  # No minimum uptime
            'min_bytes': 100 * 1024 * 1024,  # 100MB
            'sort_by': 'bytes'
        },
        {
            'name': 'Long-lived (>24 hours)',
            'min_uptime_hours': 24,  # 24 hours
            'min_bytes': 0,  # No minimum bytes
            'sort_by': 'uptime'
        },
        {
            'name': 'Combined Elephant Flows (>1 hour AND >10MB)',
            'min_uptime_hours': 1,  # 1 hour
            'min_bytes': 10 * 1024 * 1024,  # 10MB
            'sort_by': 'both'
        },
        {
            'name': 'Massive Flows (>1GB)',
            'min_uptime_hours': 0,
            'min_bytes': 1024 * 1024 * 1024,  # 1GB
            'sort_by': 'bytes'
        }
    ]
    
    for scenario in test_scenarios:
        print(f"\n{'='*80}")
        print(f"SCENARIO: {scenario['name']}")
        print(f"Min Uptime: {scenario['min_uptime_hours']} hours")
        print(f"Min Bytes: {scenario['min_bytes']:,} bytes")
        print(f"Sort by: {scenario['sort_by']}")
        print(f"{'='*80}")
        
        # Find elephant flows
        elephant_flows = parser.find_elephant_flows(
            min_uptime_hours=scenario['min_uptime_hours'],
            min_bytes=scenario['min_bytes'],
            sort_by=scenario['sort_by']
        )
        
        if elephant_flows:
            # Get statistics
            stats = parser.get_elephant_flow_stats(elephant_flows)
            
            print(f"\nFound {len(elephant_flows)} elephant flows ({stats['percentage_of_total']:.2f}% of total)")
            print(f"  - Long-lived only: {stats['long_lived_only']}")
            print(f"  - High-volume only: {stats['high_volume_only']}")
            print(f"  - Both criteria: {stats['both_criteria']}")
            print(f"  - Total bytes in elephant flows: {stats['total_bytes_elephant']:,}")
            print(f"  - Average uptime: {stats['avg_uptime_hours']:.2f} hours")
            print(f"  - Average bytes: {stats['avg_bytes']:,.0f}")
            print(f"  - Max uptime: {stats['max_uptime_hours']:.2f} hours")
            print(f"  - Max bytes: {stats['max_bytes']:,}")
            
            # Show top protocols
            print(f"\nTop protocols in elephant flows:")
            for protocol, count in stats['protocols'].most_common(3):
                print(f"  {protocol}: {count}")
            
            # Print top flows
            parser.print_elephant_flows(elephant_flows, limit=10)
            
            # Export to file
            filename = f"elephant_flows_{scenario['name'].lower().replace(' ', '_').replace('(', '').replace(')', '').replace('>', 'gt')}.csv"
            parser.export_elephant_flows(elephant_flows, filename)
        else:
            print("No elephant flows found with these criteria")
    
    # Interactive mode
    print(f"\n{'='*80}")
    print("INTERACTIVE MODE")
    print(f"{'='*80}")
    print("You can now customize the elephant flow detection:")
    
    try:
        uptime_hours = float(input("Enter minimum uptime in hours (0 for no limit): "))
        bytes_mb = float(input("Enter minimum bytes in MB (0 for no limit): "))
        sort_option = input("Sort by (uptime/bytes/both): ").lower()
        
        if sort_option not in ['uptime', 'bytes', 'both']:
            sort_option = 'bytes'
        
        min_bytes = int(bytes_mb * 1024 * 1024)
        
        print(f"\nSearching for elephant flows...")
        print(f"Min uptime: {uptime_hours} hours")
        print(f"Min bytes: {bytes_mb} MB ({min_bytes:,} bytes)")
        print(f"Sort by: {sort_option}")
        
        elephant_flows = parser.find_elephant_flows(
            min_uptime_hours=uptime_hours,
            min_bytes=min_bytes,
            sort_by=sort_option
        )
        
        if elephant_flows:
            stats = parser.get_elephant_flow_stats(elephant_flows)
            
            print(f"\nFound {len(elephant_flows)} elephant flows ({stats['percentage_of_total']:.2f}% of total)")
            
            # Show detailed results
            parser.print_elephant_flows(elephant_flows, limit=20)
            
            # Export
            parser.export_elephant_flows(elephant_flows, 'custom_elephant_flows.csv')
        else:
            print("No elephant flows found with these criteria")
            
    except (ValueError, KeyboardInterrupt):
        print("\nSkipping interactive mode")


if __name__ == "__main__":
    main()