#!/usr/bin/env python3
"""
Enhanced Elephant Flow Analyzer with Flag Analysis and Traffic Rate Detection
Focuses on Cisco ASA flags (N3, N4, N5, N6, o) and high traffic rates
"""

from connection_parser import ConnectionParser
from collections import Counter

def main():
    """Main function for enhanced elephant flow analysis"""
    parser = ConnectionParser()
    
    print("="*80)
    print("ENHANCED ELEPHANT FLOW ANALYZER")
    print("Cisco ASA Flag-Based and Rate-Based Detection")
    print("="*80)
    
    # Load data
    print("Loading and parsing connections...")
    connections = parser.parse_file_simple('sh_conn_detail.txt')
    
    if not connections:
        print("No connections found")
        return
    
    print(f"Loaded {len(connections):,} connections")
    
    # Analysis scenarios focusing on flags and rates
    scenarios = [
        {
            'name': 'ASA Flag-Based Elephant Flows (N3, N4, N5, N6)',
            'min_uptime_hours': 0,
            'min_bytes': 0,
            'min_mbps': 0,
            'sort_by': 'bytes',
            'include_flagged': True,
            'include_offloaded': False,
            'description': 'Connections explicitly marked as elephant flows by ASA/Snort'
        },
        {
            'name': 'Offloaded Elephant Flows (o flag)',
            'min_uptime_hours': 0,
            'min_bytes': 0,
            'min_mbps': 0,
            'sort_by': 'bytes',
            'include_flagged': False,
            'include_offloaded': True,
            'description': 'Connections offloaded due to elephant flow processing'
        },
        {
            'name': 'High-Rate Flows (>100 Mbps)',
            'min_uptime_hours': 0,
            'min_bytes': 0,
            'min_mbps': 100,
            'sort_by': 'rate',
            'include_flagged': True,
            'include_offloaded': True,
            'description': 'Connections with very high traffic rates regardless of duration'
        },
        {
            'name': 'Sustained High-Rate Flows (>10 Mbps, >1 hour)',
            'min_uptime_hours': 1,
            'min_bytes': 0,
            'min_mbps': 10,
            'sort_by': 'rate',
            'include_flagged': True,
            'include_offloaded': True,
            'description': 'Long-duration connections with sustained high rates'
        },
        {
            'name': 'All Flag-Based and Rate-Based Elephant Flows',
            'min_uptime_hours': 0,
            'min_bytes': 0,
            'min_mbps': 1,  # >1 Mbps
            'sort_by': 'both',
            'include_flagged': True,
            'include_offloaded': True,
            'description': 'Comprehensive elephant flow detection using all methods'
        }
    ]
    
    all_results = {}
    
    for scenario in scenarios:
        print(f"\n{'='*80}")
        print(f"SCENARIO: {scenario['name']}")
        print(f"Description: {scenario['description']}")
        print(f"Parameters: {scenario['min_uptime_hours']}h, {scenario['min_bytes']} bytes, {scenario['min_mbps']} Mbps")
        print(f"{'='*80}")
        
        # Find elephant flows with enhanced criteria
        elephant_flows = parser.find_elephant_flows(
            min_uptime_hours=scenario['min_uptime_hours'],
            min_bytes=scenario['min_bytes'],
            min_mbps=scenario['min_mbps'],
            sort_by=scenario['sort_by'],
            include_flagged=scenario['include_flagged'],
            include_offloaded=scenario['include_offloaded']
        )
        
        all_results[scenario['name']] = elephant_flows
        
        if elephant_flows:
            # Enhanced statistics
            stats = parser.get_elephant_flow_stats(elephant_flows)
            
            # Additional flag-based statistics
            flagged_count = len([f for f in elephant_flows if f.get('is_flagged_elephant')])
            offloaded_count = len([f for f in elephant_flows if f.get('is_offloaded_elephant')])
            high_rate_count = len([f for f in elephant_flows if f.get('is_high_rate')])
            
            # Rate category distribution
            rate_categories = Counter(f.get('rate_category', 'unknown') for f in elephant_flows)
            
            # Flag type distribution
            flag_types = Counter(f.get('elephant_flag_type', 'none') for f in elephant_flows if f.get('has_elephant_flag'))
            
            print(f"\nRESULTS SUMMARY:")
            print(f"Total Elephant Flows: {len(elephant_flows):,} ({stats['percentage_of_total']:.2f}% of all connections)")
            print(f"  - Flag-based (N3/N4/N5/N6): {flagged_count:,}")
            print(f"  - Offloaded (o): {offloaded_count:,}")
            print(f"  - High-rate based: {high_rate_count:,}")
            print(f"  - Long-lived: {stats['long_lived_only']:,}")
            print(f"  - High-volume: {stats['high_volume_only']:,}")
            print(f"  - Multiple criteria: {stats['both_criteria']:,}")
            
            if rate_categories:
                print(f"\nTraffic Rate Distribution:")
                for category, count in rate_categories.most_common():
                    print(f"  {category}: {count:,}")
            
            if flag_types:
                print(f"\nElephant Flag Types:")
                for flag_type, count in flag_types.most_common():
                    print(f"  {flag_type}: {count:,}")
            
            # Show top flows
            print(f"\nTOP 10 FLOWS:")
            parser.print_elephant_flows(elephant_flows, limit=10, show_flags=True)
            
            # Export results
            filename = f"enhanced_elephant_flows_{scenario['name'].lower().replace(' ', '_').replace('(', '').replace(')', '').replace(',', '').replace('>', 'gt')}.csv"
            parser.export_elephant_flows(elephant_flows, filename)
            print(f"\nExported to: {filename}")
            
        else:
            print("No elephant flows found with these criteria")
    
    # Detailed analysis of top flows
    print(f"\n{'='*80}")
    print("DETAILED ANALYSIS OF TOP ELEPHANT FLOWS")
    print(f"{'='*80}")
    
    # Get comprehensive elephant flows
    comprehensive_flows = all_results.get('All Flag-Based and Rate-Based Elephant Flows', [])
    if comprehensive_flows:
        parser.print_elephant_flow_details(comprehensive_flows, limit=5)
    
    # Flag analysis across all connections
    print(f"\n{'='*80}")
    print("OVERALL FLAG ANALYSIS")
    print(f"{'='*80}")
    
    flag_analysis = analyze_all_flags(connections)
    print_flag_analysis(flag_analysis)
    
    # High-rate connection analysis
    print(f"\n{'='*80}")
    print("HIGH-RATE CONNECTION ANALYSIS")
    print(f"{'='*80}")
    
    rate_analysis = analyze_traffic_rates(connections, parser)
    print_rate_analysis(rate_analysis)

def analyze_all_flags(connections):
    """Analyze flag distribution across all connections"""
    parser = ConnectionParser()
    
    flag_stats = {
        'total_connections': len(connections),
        'connections_with_flags': 0,
        'elephant_flagged': {'N3': 0, 'N4': 0, 'N5': 0, 'N6': 0},
        'offloaded': 0,
        'snort_inspected': 0,
        'all_flags': Counter(),
        'flag_combinations': Counter()
    }
    
    for conn in connections:
        if 'flags' in conn and conn['flags']:
            flag_stats['connections_with_flags'] += 1
            flag_info = parser._parse_connection_flags(conn['flags'])
            
            # Count specific flags
            raw_flags = flag_info.get('raw_flags', '')
            flag_stats['all_flags'][raw_flags] += 1
            
            if flag_info.get('has_elephant_flag'):
                elephant_type = flag_info.get('elephant_flag_type')
                if elephant_type in flag_stats['elephant_flagged']:
                    flag_stats['elephant_flagged'][elephant_type] += 1
            
            if flag_info.get('is_offloaded'):
                flag_stats['offloaded'] += 1
            
            if flag_info.get('is_snort_inspected'):
                flag_stats['snort_inspected'] += 1
            
            # Analyze flag combinations
            if len(raw_flags) > 1:
                flag_stats['flag_combinations'][raw_flags] += 1
    
    return flag_stats

def print_flag_analysis(flag_stats):
    """Print flag analysis results"""
    total = flag_stats['total_connections']
    with_flags = flag_stats['connections_with_flags']
    
    print(f"Total Connections: {total:,}")
    print(f"Connections with Flags: {with_flags:,} ({with_flags/total*100:.1f}%)")
    
    print(f"\nElephant Flow Flags:")
    for flag_type, count in flag_stats['elephant_flagged'].items():
        if count > 0:
            print(f"  {flag_type}: {count:,} ({count/total*100:.3f}%)")
    
    print(f"\nSpecial Flags:")
    print(f"  Offloaded (o): {flag_stats['offloaded']:,} ({flag_stats['offloaded']/total*100:.3f}%)")
    print(f"  Snort Inspected (N*): {flag_stats['snort_inspected']:,} ({flag_stats['snort_inspected']/total*100:.3f}%)")
    
    print(f"\nTop 10 Flag Combinations:")
    for flags, count in flag_stats['all_flags'].most_common(10):
        if flags:  # Skip empty flags
            print(f"  {flags}: {count:,}")

def analyze_traffic_rates(connections, parser):
    """Analyze traffic rate distribution"""
    rate_stats = {
        'total_connections': len(connections),
        'connections_with_rates': 0,
        'rate_categories': Counter(),
        'high_rate_flows': [],
        'rate_distribution': {
            'gbps': 0,      # >1 Gbps
            'hundreds_mbps': 0,  # 100-1000 Mbps
            'tens_mbps': 0,      # 10-100 Mbps
            'mbps': 0,           # 1-10 Mbps
            'kbps': 0,           # <1 Mbps
        }
    }
    
    for conn in connections:
        # Calculate rate for connections with both uptime and bytes
        if 'uptime' in conn and 'bytes' in conn and conn['bytes'].isdigit():
            uptime_seconds = parser._parse_time_to_seconds(conn['uptime'])
            bytes_count = int(conn['bytes'])
            
            if uptime_seconds > 0:
                rate_info = parser._calculate_traffic_rate(bytes_count, uptime_seconds)
                rate_stats['connections_with_rates'] += 1
                
                mbps = rate_info['mbps']
                category = rate_info['rate_category']
                rate_stats['rate_categories'][category] += 1
                
                # Categorize by rate ranges
                if mbps >= 1000:
                    rate_stats['rate_distribution']['gbps'] += 1
                elif mbps >= 100:
                    rate_stats['rate_distribution']['hundreds_mbps'] += 1
                elif mbps >= 10:
                    rate_stats['rate_distribution']['tens_mbps'] += 1
                elif mbps >= 1:
                    rate_stats['rate_distribution']['mbps'] += 1
                else:
                    rate_stats['rate_distribution']['kbps'] += 1
                
                # Collect high-rate flows
                if mbps >= 100:  # >100 Mbps
                    conn_copy = conn.copy()
                    conn_copy.update(rate_info)
                    rate_stats['high_rate_flows'].append(conn_copy)
    
    # Sort high-rate flows by rate
    rate_stats['high_rate_flows'].sort(key=lambda x: x['mbps'], reverse=True)
    
    return rate_stats

def print_rate_analysis(rate_stats):
    """Print traffic rate analysis results"""
    total = rate_stats['total_connections']
    with_rates = rate_stats['connections_with_rates']
    
    print(f"Total Connections: {total:,}")
    print(f"Connections with Calculable Rates: {with_rates:,} ({with_rates/total*100:.1f}%)")
    
    print(f"\nRate Distribution:")
    for category, count in rate_stats['rate_categories'].most_common():
        print(f"  {category}: {count:,} ({count/with_rates*100:.1f}%)")
    
    print(f"\nRate Ranges:")
    for range_name, count in rate_stats['rate_distribution'].items():
        if count > 0:
            print(f"  {range_name}: {count:,} ({count/with_rates*100:.2f}%)")
    
    high_rate_flows = rate_stats['high_rate_flows']
    if high_rate_flows:
        print(f"\nTop 5 Highest Rate Flows (>100 Mbps):")
        for i, flow in enumerate(high_rate_flows[:5]):
            mbps = flow.get('mbps', 0)
            src = f"{flow.get('src_ip', 'N/A')}:{flow.get('src_port', 'N/A')}"
            dst = f"{flow.get('dst_ip', 'N/A')}:{flow.get('dst_port', 'N/A')}"
            
            if mbps >= 1000:
                rate_str = f"{mbps/1000:.1f} Gbps"
            else:
                rate_str = f"{mbps:.1f} Mbps"
            
            print(f"  {i+1}. {flow.get('protocol', 'N/A')} {src} -> {dst}: {rate_str}")

if __name__ == "__main__":
    main()