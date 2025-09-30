#!/usr/bin/env python3
"""
Cisco ASA Connection Parser
Parses 'show conn detail' output and extracts connection information
"""

import textfsm
import csv
import json
from collections import defaultdict, Counter
from datetime import datetime
import re


class ConnectionParser:
    def __init__(self, template_file='connection_template.textfsm'):
        """Initialize the parser with TextFSM template"""
        self.template_file = template_file
        self.connections = []
        self.stats = {}
        
    def parse_file(self, filename):
        """Parse the connection file using TextFSM"""
        print(f"Parsing file: {filename}")
        
        # Read the template
        with open(self.template_file, 'r') as template:
            fsm = textfsm.TextFSM(template)
        
        # Read and parse the data file
        with open(filename, 'r', encoding='utf-8', errors='ignore') as data_file:
            content = data_file.read()
            
        # Parse the content
        parsed_data = fsm.ParseText(content)
        
        # Convert to list of dictionaries
        headers = fsm.header
        self.connections = []
        
        for row in parsed_data:
            connection = dict(zip(headers, row))
            # Clean up empty values
            connection = {k: v for k, v in connection.items() if v}
            self.connections.append(connection)
        
        print(f"Parsed {len(self.connections)} connections")
        return self.connections
    
    def parse_file_simple(self, filename):
        """Alternative parsing method using string operations"""
        print(f"Parsing file with simple method: {filename}")
        
        connections = []
        current_connection = {}
        
        with open(filename, 'r', encoding='utf-8', errors='ignore') as file:
            for line in file:
                line = line.strip()
                
                # Skip empty lines
                if not line:
                    continue
                
                # Main connection line (starts with protocol)
                if re.match(r'^(TCP|UDP|ICMP)', line):
                    # Save previous connection if exists
                    if current_connection:
                        connections.append(current_connection)
                    
                    # Parse new connection
                    current_connection = self._parse_connection_line(line)
                
                # Flags line
                elif line.startswith('flags'):
                    flags_info = self._parse_flags_line(line)
                    current_connection.update(flags_info)
                
                # Initiator/Responder line
                elif 'Initiator:' in line and 'Responder:' in line:
                    init_resp = self._parse_initiator_responder(line)
                    current_connection.update(init_resp)
                
                # Connection lookup keyid
                elif 'Connection lookup keyid:' in line:
                    keyid = line.split(':')[-1].strip()
                    current_connection['keyid'] = keyid
        
        # Don't forget the last connection
        if current_connection:
            connections.append(current_connection)
        
        self.connections = connections
        print(f"Parsed {len(self.connections)} connections")
        return connections
    
    def _parse_connection_line(self, line):
        """Parse the main connection line"""
        # Example: "UDP FORTISIEM: 10.1.76.4/45879 dc2: 10.1.5.101/53,"
        parts = line.split()
        
        connection = {}
        connection['protocol'] = parts[0]
        
        # Find source and destination
        for i, part in enumerate(parts):
            if ':' in part and '/' in parts[i+1] if i+1 < len(parts) else False:
                # Source interface and IP/port
                connection['src_interface'] = part.rstrip(':')
                src_ip_port = parts[i+1].rstrip(',')
                if '/' in src_ip_port:
                    connection['src_ip'], connection['src_port'] = src_ip_port.split('/')
                
                # Destination interface and IP/port
                if i+2 < len(parts):
                    connection['dst_interface'] = parts[i+2].rstrip(':')
                if i+3 < len(parts):
                    dst_ip_port = parts[i+3].rstrip(',')
                    if '/' in dst_ip_port:
                        connection['dst_ip'], connection['dst_port'] = dst_ip_port.split('/')
                break
        
        return connection
    
    def _parse_flags_line(self, line):
        """Parse the flags line"""
        # Example: "flags - N1, idle 21s, uptime 21s, timeout 2m0s, bytes 28, Rx-RingNum 45, Internal-Data0/1"
        info = {}
        
        # Extract flags
        if 'flags' in line:
            flags_part = line.split('flags')[1].split(',')[0].strip()
            info['flags'] = flags_part.replace('- ', '').replace('-', '')
        
        # Extract other information using regex
        patterns = {
            'idle': r'idle\s+(\S+)',
            'uptime': r'uptime\s+(\S+)',
            'timeout': r'timeout\s+(\S+)',
            'bytes': r'bytes\s+(\d+)',
            'rx_ring_num': r'Rx-RingNum\s+(\d+)',
            'internal_data': r'(Internal-Data\S+)'
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, line)
            if match:
                info[key] = match.group(1)
        
        return info
    
    def _parse_initiator_responder(self, line):
        """Parse initiator and responder IPs"""
        # Example: "Initiator: 10.1.76.3, Responder: 10.1.19.90"
        info = {}
        
        init_match = re.search(r'Initiator:\s+(\d+\.\d+\.\d+\.\d+)', line)
        resp_match = re.search(r'Responder:\s+(\d+\.\d+\.\d+\.\d+)', line)
        
        if init_match:
            info['initiator_ip'] = init_match.group(1)
        if resp_match:
            info['responder_ip'] = resp_match.group(1)
        
        return info
    
    def _parse_time_to_seconds(self, time_str):
        """Convert time string to seconds for comparison"""
        if not time_str:
            return 0
        
        # Remove trailing comma if present
        time_str = time_str.rstrip(',')
        
        # Parse different time formats
        # Examples: 21s, 1m55s, 2h39m, 1Y25D, etc.
        total_seconds = 0
        
        # Year pattern (1Y)
        year_match = re.search(r'(\d+)Y', time_str)
        if year_match:
            total_seconds += int(year_match.group(1)) * 365 * 24 * 3600
        
        # Day pattern (25D)
        day_match = re.search(r'(\d+)D', time_str)
        if day_match:
            total_seconds += int(day_match.group(1)) * 24 * 3600
        
        # Hour pattern (2h)
        hour_match = re.search(r'(\d+)h', time_str)
        if hour_match:
            total_seconds += int(hour_match.group(1)) * 3600
        
        # Minute pattern (39m)
        minute_match = re.search(r'(\d+)m', time_str)
        if minute_match:
            total_seconds += int(minute_match.group(1)) * 60
        
        # Second pattern (55s)
        second_match = re.search(r'(\d+)s', time_str)
        if second_match:
            total_seconds += int(second_match.group(1))
        
        return total_seconds
    
    def _parse_connection_flags(self, flags_str):
        """Parse and categorize connection flags"""
        if not flags_str:
            return {}
        
        # Clean up flags string
        flags = flags_str.replace('-', '').strip()
        
        flag_info = {
            'raw_flags': flags,
            'has_elephant_flag': False,
            'elephant_flag_type': None,
            'is_offloaded': False,
            'is_snort_inspected': False,
            'snort_flags': [],
            'tcp_state_flags': [],
            'protocol_flags': [],
            'special_flags': []
        }
        
        # Check for Snort inspection flags (N1-N6)
        snort_patterns = {
            'N1': 'preserve-connection enabled',
            'N2': 'preserve-connection in effect', 
            'N3': 'elephant-flow',
            'N4': 'elephant-flow bypassed',
            'N5': 'elephant-flow throttled',
            'N6': 'elephant-flow exempted'
        }
        
        for pattern, description in snort_patterns.items():
            if pattern in flags:
                flag_info['snort_flags'].append({'flag': pattern, 'description': description})
                flag_info['is_snort_inspected'] = True
                
                # Mark elephant flow flags
                if pattern in ['N3', 'N4', 'N5', 'N6']:
                    flag_info['has_elephant_flag'] = True
                    flag_info['elephant_flag_type'] = pattern
        
        # Check for offloaded flag
        if 'o' in flags:
            flag_info['is_offloaded'] = True
            flag_info['special_flags'].append({'flag': 'o', 'description': 'offloaded'})
        
        # TCP state flags
        tcp_flags = {
            'U': 'up', 'F': 'initiator FIN', 'f': 'responder FIN',
            'R': 'initiator acknowledged FIN', 'r': 'responder acknowledged FIN',
            'A': 'awaiting responder ACK to SYN', 'a': 'awaiting initiator ACK to SYN',
            'I': 'initiator data', 'O': 'responder data', 'i': 'incomplete'
        }
        
        for flag_char, description in tcp_flags.items():
            if flag_char in flags:
                flag_info['tcp_state_flags'].append({'flag': flag_char, 'description': description})
        
        # Protocol and special flags
        protocol_flags = {
            'T': 'SIP', 't': 'SIP transient', 'H': 'H.323', 'h': 'H.225.0',
            'M': 'SMTP data', 'm': 'SIP media', 'D': 'DNS', 'Q': 'QUIC',
            'G': 'group', 'g': 'MGCP', 'J': 'GTP', 'j': 'GTP data',
            'k': 'Skinny media', 'L': 'decap tunnel', 'q': 'SQL*Net data',
            'B': 'TCP probe for server certificate', 'b': 'TCP state-bypass or nailed',
            'C': 'CTIQBE media', 'c': 'cluster centralized', 'd': 'dump',
            'E': 'outside back connection', 'e': 'semi-distributed',
            'K': 'GTP t3-response', 'n': 'GUP', 'P': 'inside back connection',
            'p': 'passenger flow', 'V': 'VPN orphan', 'v': 'M3UA',
            'W': 'WAAS', 'w': 'secondary domain backup',
            'X': 'inspected by service module', 'x': 'per session',
            'Y': 'director stub flow', 'y': 'backup stub flow',
            'Z': 'Scansafe redirection', 'z': 'forwarding stub flow'
        }
        
        for flag_char, description in protocol_flags.items():
            if flag_char in flags:
                flag_info['protocol_flags'].append({'flag': flag_char, 'description': description})
        
        # Special patterns
        if 'Z1' in flags:
            flag_info['special_flags'].append({'flag': 'Z1', 'description': 'zero-trust flow'})
        
        return flag_info
    
    def _calculate_traffic_rate(self, bytes_count, uptime_seconds):
        """Calculate various traffic rates"""
        if uptime_seconds <= 0:
            return {
                'bytes_per_second': 0,
                'bytes_per_minute': 0,
                'bytes_per_hour': 0,
                'mbps': 0,
                'rate_category': 'unknown'
            }
        
        bytes_per_second = bytes_count / uptime_seconds
        bytes_per_minute = bytes_per_second * 60
        bytes_per_hour = bytes_per_second * 3600
        
        # Convert to Mbps (megabits per second)
        mbps = (bytes_per_second * 8) / (1024 * 1024)
        
        # Categorize traffic rate
        if mbps >= 1000:
            rate_category = 'extremely_high'  # >1 Gbps
        elif mbps >= 100:
            rate_category = 'very_high'       # >100 Mbps
        elif mbps >= 10:
            rate_category = 'high'            # >10 Mbps
        elif mbps >= 1:
            rate_category = 'medium'          # >1 Mbps
        elif mbps >= 0.1:
            rate_category = 'low'             # >100 Kbps
        else:
            rate_category = 'very_low'        # <100 Kbps
        
        return {
            'bytes_per_second': bytes_per_second,
            'bytes_per_minute': bytes_per_minute,
            'bytes_per_hour': bytes_per_hour,
            'mbps': mbps,
            'rate_category': rate_category
        }
    
    def find_elephant_flows(self, min_uptime_hours=1, min_bytes=1000000, min_mbps=0, 
                           sort_by='bytes', include_flagged=True, include_offloaded=True):
        """
        Enhanced elephant flow detection with flag analysis and traffic rates
        
        Args:
            min_uptime_hours (float): Minimum uptime in hours
            min_bytes (int): Minimum bytes transferred
            min_mbps (float): Minimum traffic rate in Mbps
            sort_by (str): Sort by 'uptime', 'bytes', 'rate', or 'both'
            include_flagged (bool): Include connections with elephant flags (N3, N4, N5, N6)
            include_offloaded (bool): Include offloaded connections (o flag)
        
        Returns:
            list: List of elephant flows with enhanced analysis
        """
        if not self.connections:
            print("No connections to analyze")
            return []
        
        elephant_flows = []
        min_uptime_seconds = min_uptime_hours * 3600
        
        for conn in self.connections:
            # Parse uptime
            uptime_seconds = 0
            if 'uptime' in conn:
                uptime_seconds = self._parse_time_to_seconds(conn['uptime'])
            
            # Parse bytes
            bytes_count = 0
            if 'bytes' in conn and conn['bytes'].isdigit():
                bytes_count = int(conn['bytes'])
            
            # Parse flags
            flag_info = {}
            if 'flags' in conn:
                flag_info = self._parse_connection_flags(conn['flags'])
            
            # Calculate traffic rate
            rate_info = self._calculate_traffic_rate(bytes_count, uptime_seconds)
            
            # Determine if it's an elephant flow based on multiple criteria
            is_long_lived = uptime_seconds >= min_uptime_seconds
            is_high_volume = bytes_count >= min_bytes
            is_high_rate = rate_info['mbps'] >= min_mbps
            is_flagged_elephant = flag_info.get('has_elephant_flag', False) and include_flagged
            is_offloaded_elephant = flag_info.get('is_offloaded', False) and include_offloaded
            
            # Check if it qualifies as elephant flow
            qualifies = (is_long_lived or is_high_volume or is_high_rate or 
                        is_flagged_elephant or is_offloaded_elephant)
            
            if qualifies:
                # Create enhanced connection record
                conn_copy = conn.copy()
                conn_copy['uptime_seconds'] = uptime_seconds
                conn_copy['uptime_hours'] = uptime_seconds / 3600
                conn_copy['bytes_int'] = bytes_count
                conn_copy['is_long_lived'] = is_long_lived
                conn_copy['is_high_volume'] = is_high_volume
                conn_copy['is_high_rate'] = is_high_rate
                conn_copy['is_flagged_elephant'] = is_flagged_elephant
                conn_copy['is_offloaded_elephant'] = is_offloaded_elephant
                
                # Add flag and rate information
                conn_copy.update(flag_info)
                conn_copy.update(rate_info)
                
                # Calculate combined score with rate component
                uptime_score = uptime_seconds / 3600  # hours
                bytes_score = bytes_count / 1000000   # MB
                rate_score = rate_info['mbps']        # Mbps
                conn_copy['combined_score'] = uptime_score + bytes_score + (rate_score * 10)
                
                # Determine elephant flow type
                flow_types = []
                if is_long_lived: flow_types.append('Long-lived')
                if is_high_volume: flow_types.append('High-volume')
                if is_high_rate: flow_types.append('High-rate')
                if is_flagged_elephant: 
                    elephant_type = flag_info.get('elephant_flag_type', 'N?')
                    flow_types.append(f'Flagged-{elephant_type}')
                if is_offloaded_elephant: flow_types.append('Offloaded')
                
                conn_copy['elephant_flow_type'] = ' + '.join(flow_types)
                
                elephant_flows.append(conn_copy)
        
        # Sort by specified criteria
        if sort_by == 'uptime':
            elephant_flows.sort(key=lambda x: x['uptime_seconds'], reverse=True)
        elif sort_by == 'bytes':
            elephant_flows.sort(key=lambda x: x['bytes_int'], reverse=True)
        elif sort_by == 'rate':
            elephant_flows.sort(key=lambda x: x['mbps'], reverse=True)
        elif sort_by == 'both':
            elephant_flows.sort(key=lambda x: x['combined_score'], reverse=True)
        else:
            print(f"Invalid sort_by parameter: {sort_by}. Using 'bytes' as default.")
            elephant_flows.sort(key=lambda x: x['bytes_int'], reverse=True)
        
        return elephant_flows
    
    def print_elephant_flows(self, elephant_flows, limit=20):
        """Print elephant flows in a formatted table with enhanced information"""
        if not elephant_flows:
            print("No elephant flows found")
            return
        
        print(f"\n{'='*130}")
        print(f"ENHANCED ELEPHANT FLOWS ANALYSIS - Top {min(limit, len(elephant_flows))} flows")
        print(f"{'='*130}")
        
        # Header - Always show flags, remove redundant type column
        print(f"{'#':<3} {'Protocol':<8} {'Source':<25} {'Destination':<25} {'Uptime':<15} {'Bytes':<15} {'Rate':<12} {'Flags':<20}")
        print(f"{'-'*125}")
        
        for i, flow in enumerate(elephant_flows[:limit]):
            # Format uptime
            uptime_hours = flow.get('uptime_hours', 0)
            if uptime_hours >= 24:
                uptime_str = f"{uptime_hours/24:.1f}d"
            elif uptime_hours >= 1:
                uptime_str = f"{uptime_hours:.1f}h"
            else:
                uptime_str = flow.get('uptime', 'N/A')
            
            # Format bytes
            bytes_count = flow.get('bytes_int', 0)
            if bytes_count >= 1e12:
                bytes_str = f"{bytes_count/1e12:.1f}TB"
            elif bytes_count >= 1e9:
                bytes_str = f"{bytes_count/1e9:.1f}GB"
            elif bytes_count >= 1e6:
                bytes_str = f"{bytes_count/1e6:.1f}MB"
            elif bytes_count >= 1e3:
                bytes_str = f"{bytes_count/1e3:.1f}KB"
            else:
                bytes_str = f"{bytes_count}B"
            
            # Format traffic rate
            mbps = flow.get('mbps', 0)
            if mbps >= 1000:
                rate_str = f"{mbps/1000:.1f}Gbps"
            elif mbps >= 1:
                rate_str = f"{mbps:.1f}Mbps"
            elif mbps >= 0.001:
                rate_str = f"{mbps*1000:.1f}Kbps"
            else:
                rate_str = f"{mbps*1000000:.0f}bps"
            
            # Format source and destination
            src = f"{flow.get('src_ip', 'N/A')}:{flow.get('src_port', 'N/A')}"
            dst = f"{flow.get('dst_ip', 'N/A')}:{flow.get('dst_port', 'N/A')}"
            
            # Format flags - Enhanced display showing all flags
            flags_str = "N/A"
            if 'raw_flags' in flow and flow['raw_flags']:
                raw_flags = flow['raw_flags']
                
                # Highlight special flags within the complete flag set
                if flow.get('has_elephant_flag'):
                    elephant_type = flow.get('elephant_flag_type', '')
                    # Highlight the elephant flag but keep all other flags
                    flags_str = raw_flags.replace(elephant_type, f"*{elephant_type}*")[:18]
                elif flow.get('is_offloaded') and 'o' in raw_flags:
                    # Highlight the offloaded flag but keep all other flags  
                    flags_str = raw_flags.replace('o', '*o*')[:18]
                else:
                    # Show actual flags for better visibility
                    flags_str = raw_flags[:18]
            elif 'flags' in flow and flow['flags']:
                flags_str = flow['flags'][:18]
            
            # Always show flags, no more redundant type column
            print(f"{i+1:<3} {flow.get('protocol', 'N/A'):<8} {src:<25} {dst:<25} {uptime_str:<15} {bytes_str:<15} {rate_str:<12} {flags_str:<20}")
    
    def print_elephant_flow_details(self, elephant_flows, limit=5):
        """Print detailed information about top elephant flows"""
        if not elephant_flows:
            print("No elephant flows found")
            return
        
        print(f"\n{'='*100}")
        print(f"DETAILED ELEPHANT FLOW ANALYSIS - Top {min(limit, len(elephant_flows))} flows")
        print(f"{'='*100}")
        
        for i, flow in enumerate(elephant_flows[:limit]):
            print(f"\n--- Flow #{i+1} ---")
            print(f"Protocol: {flow.get('protocol', 'N/A')}")
            print(f"Source: {flow.get('src_interface', 'N/A')} - {flow.get('src_ip', 'N/A')}:{flow.get('src_port', 'N/A')}")
            print(f"Destination: {flow.get('dst_interface', 'N/A')} - {flow.get('dst_ip', 'N/A')}:{flow.get('dst_port', 'N/A')}")
            
            # Time information
            uptime_hours = flow.get('uptime_hours', 0)
            uptime_days = uptime_hours / 24
            print(f"Uptime: {flow.get('uptime', 'N/A')} ({uptime_hours:.1f} hours, {uptime_days:.1f} days)")
            
            # Traffic information
            bytes_count = flow.get('bytes_int', 0)
            print(f"Bytes: {bytes_count:,} ({bytes_count/1e9:.2f} GB)")
            
            # Rate information
            print(f"Traffic Rate: {flow.get('mbps', 0):.2f} Mbps ({flow.get('rate_category', 'unknown')})")
            print(f"  - Bytes/sec: {flow.get('bytes_per_second', 0):,.0f}")
            print(f"  - Bytes/min: {flow.get('bytes_per_minute', 0):,.0f}")
            print(f"  - Bytes/hour: {flow.get('bytes_per_hour', 0):,.0f}")
            
            # Flag analysis
            print(f"Flags: {flow.get('raw_flags', 'N/A')}")
            if flow.get('has_elephant_flag'):
                print(f"  ⚠️  ELEPHANT FLAG DETECTED: {flow.get('elephant_flag_type')} - {flow.get('elephant_flow_type')}")
            if flow.get('is_offloaded'):
                print(f"  🔄 OFFLOADED CONNECTION")
            if flow.get('is_snort_inspected'):
                print(f"  🔍 SNORT INSPECTED")
                for snort_flag in flow.get('snort_flags', []):
                    print(f"     - {snort_flag['flag']}: {snort_flag['description']}")
            
            # Classification
            classifications = []
            if flow.get('is_long_lived'): classifications.append('Long-lived')
            if flow.get('is_high_volume'): classifications.append('High-volume') 
            if flow.get('is_high_rate'): classifications.append('High-rate')
            if flow.get('is_flagged_elephant'): classifications.append('Flag-based')
            if flow.get('is_offloaded_elephant'): classifications.append('Offloaded')
            
            print(f"Classification: {', '.join(classifications)}")
            print(f"Combined Score: {flow.get('combined_score', 0):.2f}")
            
            # Connection details
            if 'keyid' in flow:
                print(f"Connection KeyID: {flow['keyid']}")
            if 'initiator_ip' in flow:
                print(f"Initiator: {flow['initiator_ip']}")
            if 'responder_ip' in flow:
                print(f"Responder: {flow['responder_ip']}")
                
            print("-" * 80)
    
    def export_elephant_flows(self, elephant_flows, filename='elephant_flows.csv'):
        """Export elephant flows to CSV"""
        if not elephant_flows:
            print("No elephant flows to export")
            return
        
        # Get all unique keys
        all_keys = set()
        for flow in elephant_flows:
            all_keys.update(flow.keys())
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=sorted(all_keys))
            writer.writeheader()
            writer.writerows(elephant_flows)
        
        print(f"Exported {len(elephant_flows)} elephant flows to {filename}")
    
    def get_elephant_flow_stats(self, elephant_flows):
        """Get statistics about elephant flows"""
        if not elephant_flows:
            return {}
        
        stats = {
            'total_elephant_flows': len(elephant_flows),
            'percentage_of_total': (len(elephant_flows) / len(self.connections)) * 100,
            'long_lived_only': len([f for f in elephant_flows if f.get('is_long_lived') and not f.get('is_high_volume')]),
            'high_volume_only': len([f for f in elephant_flows if f.get('is_high_volume') and not f.get('is_long_lived')]),
            'both_criteria': len([f for f in elephant_flows if f.get('is_long_lived') and f.get('is_high_volume')]),
            'total_bytes_elephant': sum(f.get('bytes_int', 0) for f in elephant_flows),
            'avg_uptime_hours': sum(f.get('uptime_hours', 0) for f in elephant_flows) / len(elephant_flows),
            'avg_bytes': sum(f.get('bytes_int', 0) for f in elephant_flows) / len(elephant_flows),
            'max_uptime_hours': max(f.get('uptime_hours', 0) for f in elephant_flows),
            'max_bytes': max(f.get('bytes_int', 0) for f in elephant_flows),
            'protocols': Counter(f.get('protocol') for f in elephant_flows),
            'top_source_ips': Counter(f.get('src_ip') for f in elephant_flows),
            'top_dest_ips': Counter(f.get('dst_ip') for f in elephant_flows),
        }
        
        return stats
    
    def analyze_connections(self):
        """Analyze the parsed connections and generate statistics"""
        if not self.connections:
            print("No connections to analyze")
            return
        
        stats = {
            'total_connections': len(self.connections),
            'protocols': Counter(),
            'source_interfaces': Counter(),
            'destination_interfaces': Counter(),
            'top_source_ips': Counter(),
            'top_destination_ips': Counter(),
            'top_ports': Counter(),
            'flags_summary': Counter(),
            'byte_statistics': {
                'total_bytes': 0,
                'max_bytes': 0,
                'min_bytes': float('inf'),
                'avg_bytes': 0
            }
        }
        
        total_bytes = 0
        byte_values = []
        
        for conn in self.connections:
            # Protocol statistics
            if 'protocol' in conn:
                stats['protocols'][conn['protocol']] += 1
            
            # Interface statistics
            if 'src_interface' in conn:
                stats['source_interfaces'][conn['src_interface']] += 1
            if 'dst_interface' in conn:
                stats['destination_interfaces'][conn['dst_interface']] += 1
            
            # IP statistics
            if 'src_ip' in conn:
                stats['top_source_ips'][conn['src_ip']] += 1
            if 'dst_ip' in conn:
                stats['top_destination_ips'][conn['dst_ip']] += 1
            
            # Port statistics
            if 'dst_port' in conn:
                stats['top_ports'][conn['dst_port']] += 1
            
            # Flags statistics
            if 'flags' in conn:
                stats['flags_summary'][conn['flags']] += 1
            
            # Byte statistics
            if 'bytes' in conn and conn['bytes'].isdigit():
                bytes_val = int(conn['bytes'])
                byte_values.append(bytes_val)
                total_bytes += bytes_val
                stats['byte_statistics']['max_bytes'] = max(stats['byte_statistics']['max_bytes'], bytes_val)
                stats['byte_statistics']['min_bytes'] = min(stats['byte_statistics']['min_bytes'], bytes_val)
        
        # Calculate average bytes
        if byte_values:
            stats['byte_statistics']['total_bytes'] = total_bytes
            stats['byte_statistics']['avg_bytes'] = total_bytes / len(byte_values)
        else:
            stats['byte_statistics']['min_bytes'] = 0
        
        self.stats = stats
        return stats
    
    def export_to_csv(self, filename='connections.csv'):
        """Export parsed connections to CSV"""
        if not self.connections:
            print("No connections to export")
            return
        
        # Get all unique keys
        all_keys = set()
        for conn in self.connections:
            all_keys.update(conn.keys())
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=sorted(all_keys))
            writer.writeheader()
            writer.writerows(self.connections)
        
        print(f"Exported {len(self.connections)} connections to {filename}")
    
    def export_stats_to_json(self, filename='connection_stats.json'):
        """Export statistics to JSON"""
        if not self.stats:
            self.analyze_connections()
        
        # Convert Counter objects to regular dicts for JSON serialization
        json_stats = {}
        for key, value in self.stats.items():
            if isinstance(value, Counter):
                json_stats[key] = dict(value.most_common())
            else:
                json_stats[key] = value
        
        with open(filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(json_stats, jsonfile, indent=2, default=str)
        
        print(f"Exported statistics to {filename}")
    
    def print_summary(self):
        """Print a summary of the analysis"""
        if not self.stats:
            self.analyze_connections()
        
        print("\n" + "="*60)
        print("CONNECTION ANALYSIS SUMMARY")
        print("="*60)
        
        print(f"\nTotal Connections: {self.stats['total_connections']:,}")
        
        print(f"\nProtocol Distribution:")
        for protocol, count in self.stats['protocols'].most_common():
            percentage = (count / self.stats['total_connections']) * 100
            print(f"  {protocol}: {count:,} ({percentage:.1f}%)")
        
        print(f"\nTop 5 Source Interfaces:")
        for interface, count in self.stats['source_interfaces'].most_common(5):
            print(f"  {interface}: {count:,}")
        
        print(f"\nTop 5 Destination Interfaces:")
        for interface, count in self.stats['destination_interfaces'].most_common(5):
            print(f"  {interface}: {count:,}")
        
        print(f"\nTop 5 Source IPs:")
        for ip, count in self.stats['top_source_ips'].most_common(5):
            print(f"  {ip}: {count:,}")
        
        print(f"\nTop 5 Destination IPs:")
        for ip, count in self.stats['top_destination_ips'].most_common(5):
            print(f"  {ip}: {count:,}")
        
        print(f"\nTop 5 Destination Ports:")
        for port, count in self.stats['top_ports'].most_common(5):
            print(f"  {port}: {count:,}")
        
        byte_stats = self.stats['byte_statistics']
        print(f"\nByte Statistics:")
        print(f"  Total Bytes: {byte_stats['total_bytes']:,}")
        print(f"  Average Bytes per Connection: {byte_stats['avg_bytes']:.2f}")
        print(f"  Max Bytes: {byte_stats['max_bytes']:,}")
        print(f"  Min Bytes: {byte_stats['min_bytes']:,}")
        
        print(f"\nTop 5 Flag Combinations:")
        for flags, count in self.stats['flags_summary'].most_common(5):
            print(f"  {flags}: {count:,}")


def main():
    """Main function to run the parser"""
    parser = ConnectionParser()
    
    # Try TextFSM first, fall back to simple parsing
    try:
        connections = parser.parse_file('sh_conn_detail.txt')
    except Exception as e:
        print(f"TextFSM parsing failed: {e}")
        print("Falling back to simple parsing method...")
        connections = parser.parse_file_simple('sh_conn_detail.txt')
    
    if connections:
        # Analyze the data
        parser.analyze_connections()
        
        # Print summary
        parser.print_summary()
        
        # Export data
        parser.export_to_csv()
        parser.export_stats_to_json()
        
        print(f"\n\nFiles created:")
        print(f"  - connections.csv (detailed connection data)")
        print(f"  - connection_stats.json (summary statistics)")


if __name__ == "__main__":
    main()