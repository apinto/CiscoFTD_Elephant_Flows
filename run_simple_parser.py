#!/usr/bin/env python3
"""
Run the parser with the simple method on the full dataset
"""

from connection_parser import ConnectionParser

def main():
    """Main function to run the parser with simple method"""
    parser = ConnectionParser()
    
    print("Using simple parsing method...")
    connections = parser.parse_file_simple('sh_conn_detail.txt')
    
    if connections:
        # Analyze the data
        parser.analyze_connections()
        
        # Print summary
        parser.print_summary()
        
        # Export data
        parser.export_to_csv('connections_simple.csv')
        parser.export_stats_to_json('connection_stats_simple.json')
        
        print(f"\n\nFiles created:")
        print(f"  - connections_simple.csv (detailed connection data)")
        print(f"  - connection_stats_simple.json (summary statistics)")
        
        # Show first few connections as sample
        print(f"\nFirst 3 connections (sample):")
        for i, conn in enumerate(connections[:3]):
            print(f"\nConnection {i+1}:")
            for key, value in conn.items():
                print(f"  {key}: {value}")


if __name__ == "__main__":
    main()