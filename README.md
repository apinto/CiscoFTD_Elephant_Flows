# Elephant Flow Detection System - Unified Tool

## 🎯 Overview

A comprehensive elephant flow detection system for Cisco ASA `show conn detail` output that consolidates multiple detection methods into a single powerful tool. The system analyzes network connections using traditional heuristics, Cisco ASA native flags, and traffic rate analysis to identify high-impact flows.

## � Quick Start

```bash
# Get help and see all options
python3 elephant_flow_analyzer.py --help

# Executive summary with key insights
python3 elephant_flow_analyzer.py --summary

# Find ASA-flagged elephant flows
python3 elephant_flow_analyzer.py --flags-only --limit 10

# Find offloaded high-volume flows
python3 elephant_flow_analyzer.py --offloaded-only --limit 5

# Comprehensive multi-scenario analysis
python3 elephant_flow_analyzer.py --analyze
```

## 🔍 Detection Methods

### 1. **Cisco ASA Flag Analysis** ⭐ (Recommended)
   - **N3**: Explicit elephant-flow flag (ASA-identified problem flows)
   - **N4**: Elephant-flow bypassed
   - **N5**: Elephant-flow throttled  
   - **N6**: Elephant-flow exempted
   - **o**: Offloaded flag (high-volume flows bypassing inspection)

### 2. **Traffic Rate Analysis** ⭐
   - Real-time bandwidth calculation (Mbps/Gbps)
   - Rate categories from very_low to extremely_high
   - High-rate detection regardless of connection duration

### 3. **Traditional Metrics**
   - Uptime-based detection (long-lived connections)
   - Volume-based detection (high byte transfers)
   - Combined score analysis for comprehensive assessment

## 🛠️ Unified Tool Architecture

### **`elephant_flow_analyzer.py`** - Single Comprehensive Tool
- **All-in-one solution** combining functionality from multiple previous tools
- **Multi-criteria detection** with flexible parameters
- **Multiple analysis modes** (summary, detailed, comprehensive)
- **Export capabilities** to CSV format
- **Command-line interface** with extensive options

### **`connection_parser.py`** - Core Parsing Engine
- Main class: `ConnectionParser`
- Parses Cisco ASA connection data using TextFSM or simple string methods
- Comprehensive flag analysis and traffic rate calculations
- Export capabilities to CSV and JSON

## 📈 Comprehensive Usage Examples

### 🔍 **Detection Modes**

#### **1. ASA Flag-Based Detection** (Recommended)
```bash
# Find ASA-flagged elephant flows (N3, N4, N5, N6)
python3 elephant_flow_analyzer.py --flags-only --limit 20

# Detailed analysis of N3 flagged flows
python3 elephant_flow_analyzer.py --flags-only --detailed --limit 5

# Export N3 flagged flows to CSV for further analysis
python3 elephant_flow_analyzer.py --flags-only --export n3_elephant_flows.csv
```

#### **2. Offloaded Flow Detection**
```bash
# Find offloaded flows (high-volume flows bypassing inspection)
python3 elephant_flow_analyzer.py --offloaded-only --limit 10

# Detailed analysis of offloaded flows
python3 elephant_flow_analyzer.py --offloaded-only --detailed --limit 3

# Export offloaded flows sorted by traffic volume
python3 elephant_flow_analyzer.py --offloaded-only --sort bytes --export offloaded_flows.csv
```

#### **3. High-Rate Flow Detection**
```bash
# Find flows above 50 Mbps
python3 elephant_flow_analyzer.py --min-rate 50 --sort rate --limit 10

# Find extremely high-rate flows (500+ Mbps)
python3 elephant_flow_analyzer.py --min-rate 500 --sort rate

# High-rate flows with detailed analysis
python3 elephant_flow_analyzer.py --min-rate 100 --detailed --limit 5
```

#### **4. Traditional Volume/Time-Based Detection**
```bash
# Long-lived connections (48+ hours)
python3 elephant_flow_analyzer.py --min-hours 48 --sort uptime --limit 15

# High-volume flows (5+ GB)
python3 elephant_flow_analyzer.py --min-mb 5000 --sort bytes --limit 10

# Combined criteria: 24h uptime + 1GB volume + 10 Mbps rate
python3 elephant_flow_analyzer.py --min-hours 24 --min-mb 1000 --min-rate 10 --sort both
```

### 📊 **Analysis Modes**

#### **Executive Summary** (Quick Overview)
```bash
# Comprehensive executive summary with key insights
python3 elephant_flow_analyzer.py --summary

# Output includes:
# - Total connection statistics
# - N3 flagged flow counts and traffic impact
# - Offloaded flow analysis
# - Top flows by volume, rate, and uptime
# - Actionable insights and recommendations
```

#### **Comprehensive Analysis** (Deep Dive)
```bash
# Multi-scenario analysis across different criteria
python3 elephant_flow_analyzer.py --analyze

# Analyzes 4 scenarios:
# 1. ASA N3 Flagged Flows
# 2. Offloaded Flows  
# 3. High-Rate Flows (>100 Mbps)
# 4. Traditional Elephant Flows (24h + 1GB)
```

#### **Validation Testing**
```bash
# Test parsing accuracy and detection methods
python3 elephant_flow_analyzer.py --test

# Validates:
# - File parsing success rate
# - Flag detection accuracy
# - Rate calculation verification
# - Sample data analysis
```

### 🔧 **Customization Options**

#### **Filtering Parameters**
```bash
# Custom minimum thresholds
python3 elephant_flow_analyzer.py --min-hours 72 --min-mb 10000 --min-rate 25

# Include both flag-based and traditional detection
python3 elephant_flow_analyzer.py --min-hours 6 --min-mb 500 --include-flags --include-offloaded
```

#### **Sorting and Output Control**
```bash
# Sort by different criteria
python3 elephant_flow_analyzer.py --flags-only --sort uptime --limit 10    # Longest running
python3 elephant_flow_analyzer.py --flags-only --sort bytes --limit 10     # Highest volume
python3 elephant_flow_analyzer.py --flags-only --sort rate --limit 10      # Highest rate
python3 elephant_flow_analyzer.py --flags-only --sort both --limit 10      # Combined score

# Output control
python3 elephant_flow_analyzer.py --flags-only --quiet                     # Minimal output
python3 elephant_flow_analyzer.py --flags-only --detailed                  # Full details
python3 elephant_flow_analyzer.py --flags-only --limit 50                  # Show more results
```

### 📁 **Export and Automation**

#### **CSV Export**
```bash
# Export with different criteria
python3 elephant_flow_analyzer.py --flags-only --export flagged_flows.csv
python3 elephant_flow_analyzer.py --offloaded-only --export offloaded_flows.csv
python3 elephant_flow_analyzer.py --min-rate 100 --export high_rate_flows.csv

# Automated export for monitoring
python3 elephant_flow_analyzer.py --min-mb 1000 --quiet --export daily_elephants.csv
```

#### **Custom Data Files**
```bash
# Specify different input file
python3 elephant_flow_analyzer.py --file /path/to/different_conn_data.txt --summary

# Process multiple files (use in scripts)
for file in *.txt; do
    python3 elephant_flow_analyzer.py --file "$file" --summary > "${file%.txt}_summary.txt"
done
```

### 🎯 **Common Use Cases**

#### **Network Troubleshooting**
```bash
# Find problematic flows flagged by ASA
python3 elephant_flow_analyzer.py --flags-only --detailed

# Identify bandwidth hogs
python3 elephant_flow_analyzer.py --min-rate 50 --sort rate --limit 20

# Long-running suspicious connections  
python3 elephant_flow_analyzer.py --min-hours 168 --sort uptime --detailed  # 1 week+
```

#### **Capacity Planning**
```bash
# Traffic volume analysis
## 🔧 Installation and Requirements

### **Prerequisites**
```bash
# Python 3.6 or higher
python3 --version

# Required Python packages
pip install textfsm

# Optional: Virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows
pip install textfsm
```

### **Quick Setup**
```bash
# Clone or download the tool
git clone <repository_url>
cd elephant_flow_analyzer

# Install dependencies
pip install textfsm

# Test the installation
python3 elephant_flow_analyzer.py --help
```

### **Data Input Requirements**
- Cisco ASA `show conn detail` output in text format
- Default file: `sh_conn_detail.txt`
- Custom files supported via `--file` parameter

## 📋 Command Reference

### **All Available Options**
```bash
python3 elephant_flow_analyzer.py [OPTIONS]

Detection Criteria:
  --min-hours HOURS      Minimum connection uptime in hours (default: 0)
  --min-mb MB           Minimum traffic volume in MB (default: 0)  
  --min-rate MBPS       Minimum traffic rate in Mbps (default: 0)

Filter Types:
  --flags-only          Show only ASA N3/N4/N5/N6 flagged flows
  --offloaded-only      Show only offloaded flows (o flag)
  --include-flags       Include flagged flows in results
  --include-offloaded   Include offloaded flows in results

Output Options:
  --sort {uptime,bytes,rate,both}    Sort criteria (default: bytes)
  --limit LIMIT         Number of results to show (default: 20)
  --export FILE         Export results to CSV file
  --quiet              Minimal output, just show results
  --detailed           Show detailed analysis of top flows

Analysis Modes:
  --summary            Generate executive summary with key insights
  --analyze            Run comprehensive analysis with multiple scenarios  
  --test               Validate parsing and test detection methods

Data Input:
  --file FILE          Input file path (default: sh_conn_detail.txt)
```

## 🔍 Technical Details

### **Flag Analysis**
The tool recognizes and analyzes Cisco ASA connection flags:

#### **Elephant Flow Flags**
- **N3**: Elephant-flow (primary detection flag)
- **N4**: Elephant-flow bypassed  
- **N5**: Elephant-flow throttled
- **N6**: Elephant-flow exempted

#### **Special Processing Flags**
- **o**: Offloaded (high-volume traffic bypassing inspection)
- **N1**: Preserve-connection enabled
- **N2**: Preserve-connection in effect

#### **Connection State Flags**
- **U**: Connection up
- **I**: Initiator data
- **O**: Outbound data (responder data)

### **Traffic Rate Calculation**
```python
# Rate calculation formula (actual implementation)
bytes_per_second = bytes_count / uptime_seconds
mbps = (bytes_per_second * 8) / (1024 * 1024)  # Binary Mbps conversion

# Rate categories
very_low:      < 0.1 Mbps
low:          0.1 - 1 Mbps  
medium:         1 - 10 Mbps
high:          10 - 100 Mbps
very_high:    100 - 1000 Mbps
extremely_high: > 1000 Mbps
```

### **Detection Algorithms**

#### **ASA Flag-Based Detection** (Recommended)
- **Highest Priority**: Flows explicitly flagged by ASA as elephant flows
- **Most Reliable**: Based on ASA's real-time analysis
- **Best for**: Immediate identification of problematic flows

#### **Rate-Based Detection**
- **Real-time Focus**: High bandwidth consumption regardless of duration
- **Good for**: Identifying current network bottlenecks
- **Threshold**: Configurable Mbps minimum

#### **Traditional Heuristics**
- **Volume + Time**: Long-lived connections with high data transfer
- **Combined Score**: Weighted algorithm considering multiple factors
- **Good for**: Historical analysis and trend identification

### **Output Formats**

#### **Table Format**
```
#   Protocol Source                    Destination               Uptime          Bytes           Rate         Flags               
-----------------------------------------------------------------------------------------------------------------------------
1   UDP      10.10.12.40:40119         10.1.39.8:5247            390.0d          1.4TB           325.0Kbps    N2*N3*              
2   TCP      10.39.23.13:14250         10.39.22.13:52336         80.1d           131.8GB         145.3Kbps    UIO N1*N3*          
```

#### **CSV Export Fields**
- Connection identifiers (src/dst IP/port, protocol)
- Traffic metrics (bytes, uptime, rate)
- Flag analysis (raw flags, special flags, elephant types)
- ASA metadata (interfaces, timeout, connection ID)
- Calculated fields (rates, categories, scores)

## 🎯 Advanced Usage Patterns

### **Automated Monitoring**
```bash
#!/bin/bash
# Daily elephant flow monitoring script

DATE=$(date +%Y%m%d)
OUTPUT_DIR="/var/log/elephant_flows"

# Create daily summary
python3 elephant_flow_analyzer.py --summary > "$OUTPUT_DIR/summary_$DATE.txt"

# Export problematic flows
python3 elephant_flow_analyzer.py --flags-only --export "$OUTPUT_DIR/flagged_$DATE.csv"
python3 elephant_flow_analyzer.py --min-rate 100 --export "$OUTPUT_DIR/highrate_$DATE.csv"

# Alert on high counts
FLAGGED_COUNT=$(python3 elephant_flow_analyzer.py --flags-only --quiet | grep "Found" | awk '{print $2}')
if [ "$FLAGGED_COUNT" -gt 100 ]; then
    echo "High elephant flow count: $FLAGGED_COUNT" | mail -s "Elephant Flow Alert" admin@company.com
fi
```

### **Performance Optimization Workflow**
```bash
# 1. Identify current state
python3 elephant_flow_analyzer.py --summary

# 2. Find optimization candidates  
python3 elephant_flow_analyzer.py --min-mb 1000 --min-rate 5 --export candidates.csv

# 3. Analyze current offloaded flows
python3 elephant_flow_analyzer.py --offloaded-only --detailed

# 4. Comprehensive analysis for planning
python3 elephant_flow_analyzer.py --analyze > optimization_report.txt
```

### **Security Analysis Pipeline**
```bash
# 1. ASA-flagged flows (immediate attention)
python3 elephant_flow_analyzer.py --flags-only --export security_flagged.csv

# 2. Unusual long-lived connections
python3 elephant_flow_analyzer.py --min-hours 168 --export long_lived.csv  # 1 week+

# 3. High-rate short-duration flows (potential attacks)
python3 elephant_flow_analyzer.py --min-rate 500 --export high_rate_short.csv

# 4. Generate comprehensive security report
python3 elephant_flow_analyzer.py --analyze > security_analysis.txt
```

## 📊 Interpreting Results

### **Executive Summary Insights**
- **N3 Flagged Flows**: Immediate attention required - ASA-identified problem flows
- **Offloaded Flows**: High-volume traffic bypassing inspection (often legitimate)
- **Traffic Volume Impact**: Percentage of total network traffic from elephant flows
- **Top Flows**: Highest impact connections by volume, rate, and duration

### **Flag Interpretation Guide**
- **`*N3*` in flags**: Critical - ASA detected elephant flow behavior
- **`*o*` in flags**: Info - High-volume flow offloaded for performance
- **`UIO N1*N3*`**: TCP connection with data transfer, preserve-connection, and elephant detection
- **`N2*N3*`**: Connection preservation active plus elephant detection

### **When to Investigate**
1. **High N3 flagged flow counts** (>1% of total connections)
2. **Individual flows >10GB or >50 Mbps** sustained rate
3. **Long-lived flows >1 week** (potential security risk)
4. **Sudden changes** in elephant flow patterns

## 🚨 Troubleshooting

### **Common Issues**

#### **No connections found**
```bash
# Check file exists and has data
ls -la sh_conn_detail.txt
head -20 sh_conn_detail.txt

# Try different file
python3 elephant_flow_analyzer.py --file your_file.txt --test
```

#### **Parsing errors**
```bash
# Validate with test mode
python3 elephant_flow_analyzer.py --test

# Check file format
grep -i "TCP\|UDP" sh_conn_detail.txt | head -5
```

#### **No elephant flows detected**
```bash
# Lower thresholds
python3 elephant_flow_analyzer.py --min-hours 1 --min-mb 100

# Check for ASA flagged flows
python3 elephant_flow_analyzer.py --flags-only

# Use summary mode for overview
python3 elephant_flow_analyzer.py --summary
```

### **Performance Optimization**
- Use `--quiet` mode for faster processing
- Limit results with `--limit` for large datasets
- Export to CSV for analysis in external tools

## 📝 License and Support

This tool is designed for network analysis and optimization. For support or questions, refer to the documentation or contact your network engineering team.

**Note**: Always review elephant flow analysis results with network context and business requirements in mind. Not all high-volume or long-lived flows are problematic.
```

#### **Security Analysis**
```bash
# ASA-flagged flows (potential security issues)
python3 elephant_flow_analyzer.py --flags-only --export security_review.csv

# Unusual long-lived connections
python3 elephant_flow_analyzer.py --min-hours 72 --detailed

# Comprehensive security review
python3 elephant_flow_analyzer.py --analyze > security_analysis.txt
```

#### **Performance Optimization**
```bash
# Identify offload candidates
python3 elephant_flow_analyzer.py --min-mb 1000 --min-rate 10 --export offload_candidates.csv

# Current offloaded flows analysis
python3 elephant_flow_analyzer.py --offloaded-only --detailed

# Rate-based optimization targets
python3 elephant_flow_analyzer.py --min-rate 25 --sort rate --export optimization_targets.csv
```

```bash
# Generate executive summary with key insights
python3 elephant_flow_analyzer.py --summary

# Comprehensive analysis with multiple scenarios
python3 elephant_flow_analyzer.py --analyze

# Validate parsing and test specific detection methods
python3 elephant_flow_analyzer.py --test
```

#### Advanced Usage Examples

```bash
# Monitor for new high-rate flows
python3 elephant_flow_analyzer.py --min-rate 100 --sort rate --limit 10 --quiet

# Find sustained high-rate connections
python3 elephant_flow_analyzer.py --min-hours 2 --min-rate 10 --sort both

# Export all elephant flows with comprehensive criteria
python3 elephant_flow_analyzer.py --min-hours 1 --min-mb 50 --min-rate 1 \
  --include-flags --include-offloaded --export all_elephant_flows.csv

# Quick check for ASA-identified problem flows
python3 elephant_flow_analyzer.py --flags-only --limit 5 --quiet
```

### 🔧 Key Features

- **Multi-criteria detection**: Uptime, volume, rate, and flags
- **Flexible sorting**: By uptime, bytes, rate, or combined score
- **Traffic rate calculation**: Real-time Mbps with categorization
- **Flag parsing**: Complete Cisco ASA flag interpretation
- **Export capabilities**: CSV export for further analysis
- **Performance optimized**: Handles 391K+ connections efficiently

### 🎯 Benefits Over Traditional Methods

1. **ASA Native Detection**: Uses actual firewall flags (N3, o) instead of just heuristics
2. **Rate-Based Detection**: Identifies short-duration but high-impact flows
3. **Real-time Awareness**: Distinguishes between sustained vs. burst traffic
4. **Comprehensive Coverage**: Multiple detection methods catch different elephant flow types
5. **Operational Ready**: Command-line tools for network operations teams

### 📋 Output Files

The tools generate various output files for analysis and integration:

- **CSV Exports**
  - `n3_flagged_elephant_flows.csv` - ASA-flagged elephant flows
  - `offloaded_elephant_flows.csv` - Offloaded connections  
  - `high_rate_elephant_flows.csv` - High bandwidth flows
  - `connections_simple.csv` - All parsed connection data
  - Custom export files based on criteria

- **JSON Reports**
  - `connection_stats_simple.json` - Summary statistics
  - `connection_stats.json` - Detailed analysis results

- **Analysis Reports**
  - Console output with formatted tables
  - Executive summaries with key insights
  - Detailed flow analysis with flag interpretation

### 🔧 Command Line Options

The `elephant_flow_analyzer.py` unified tool supports comprehensive options:

```
--min-hours HOURS      Minimum uptime in hours (default: 0)
--min-mb MEGABYTES     Minimum bytes in MB (default: 0) 
--min-rate MBPS        Minimum traffic rate in Mbps (default: 0)
--sort {uptime,bytes,rate,both}  Sort criteria (default: bytes)
--limit NUMBER         Number of results to show (default: 20)
--flags-only           Only show connections with elephant flags (N3,N4,N5,N6)
--offloaded-only       Only show offloaded connections (o flag)
--include-flags        Include flag-based elephant flows in results
--include-offloaded    Include offloaded flows in results  
--detailed             Show detailed analysis of top flows
--export FILENAME      Export results to CSV file
--quiet               Minimal output for scripting
```

### 🚀 Use Cases

This system is designed for:

- **Network Monitoring**: Identify bandwidth-intensive applications and connections
- **Security Analysis**: Detect unusual long-running or high-volume connections  
- **Capacity Planning**: Understand traffic patterns and network growth trends
- **Performance Optimization**: Identify connections causing network strain or bottlenecks
- **Compliance Reporting**: Document high-volume data transfers for audit purposes
- **Troubleshooting**: Analyze connection patterns during network issues
- **Automation**: Integration with monitoring systems using quiet mode and CSV exports

### 🏗️ System Requirements

- **Python 3.6+**
- **Required Libraries**: `textfsm`, `csv`, `json`, `collections`, `datetime`, `re`, `os`
- **Input**: Cisco ASA `show conn detail` output file
- **Memory**: Sufficient for processing large connection tables (tested with 391K+ connections)
- **Storage**: Space for CSV exports and analysis results

### 📚 Installation and Setup

1. **Install Dependencies**
   ```bash
   pip install textfsm
   ```

2. **Prepare Data**
   - Save `show conn detail` output to a text file (e.g., `sh_conn_detail.txt`)
   - Ensure the file is in the same directory as the script

3. **Run Analysis**
   ```bash
   # Quick start - find ASA-flagged elephant flows
   python3 elephant_flow_analyzer.py --flags-only
   
   # Generate comprehensive summary
   python3 elephant_flow_analyzer.py --summary
   ```

This unified elephant flow detection system provides network operations teams with comprehensive analysis capabilities for Cisco ASA connection data, combining traditional detection methods with ASA-native intelligence for unprecedented accuracy and operational value.

---

## ⚠️ **DISCLAIMER**

**USE AT YOUR OWN RISK**

This software is provided "AS IS" without warranty of any kind. The authors and contributors make no representations or warranties regarding the accuracy, reliability, or suitability of this tool for any purpose. 

**Important Considerations:**

- **Network Impact**: This tool analyzes network connection data but does not directly modify network configurations. However, decisions made based on its output could impact network operations.

- **Data Sensitivity**: Connection data may contain sensitive network information. Ensure proper handling and storage of exported data according to your organization's security policies.

- **Analysis Accuracy**: While this tool has been extensively tested, network analysis results should always be validated against multiple sources and interpreted by qualified network professionals.

- **Production Use**: Test thoroughly in non-production environments before using in production networks. Understand the tool's behavior with your specific data formats and network configurations.

- **Compliance**: Ensure usage complies with your organization's policies, regulatory requirements, and applicable laws regarding network monitoring and data analysis.

**The user assumes full responsibility for:**
- Proper tool configuration and usage
- Validation of analysis results
- Network changes made based on tool output
- Data security and compliance requirements
- Any direct or indirect consequences of using this tool

**Recommended Best Practices:**
- Always cross-validate results with other network analysis tools
- Test in lab environments before production use
- Have qualified network engineers review analysis results
- Maintain backups of configuration before making network changes
- Follow your organization's change management procedures

By using this tool, you acknowledge that you have read, understood, and accept these terms and limitations.