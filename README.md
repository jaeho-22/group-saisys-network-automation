# Group Saisys Network Automation System
## DEVASC Project Activity 5 - Network Programmability and Automation

A comprehensive network automation system designed for Group Saisys that enables L1 Support Engineers to safely make network configuration changes using NETCONF and YANG data models.

### Features
- **YANG Data Modeling**: RFC 6020 compliant interface configuration models
- **NETCONF Protocol**: RFC 6241 compliance with SSH transport (port 830)
- **Python Automation**: Complete orchestration system with multi-step verification
- **Microsoft Teams Integration**: Automated change notifications
- **Workflow Automation**: 6-step secure configuration change process

### Quick Start
```bash
# Install dependencies
pip install -r requirements.txt

# Configure your device
# Edit automation_scripts/network_automation.py
DEVICE_HOST = "192.168.1.1"
DEVICE_USERNAME = "admin"
DEVICE_PASSWORD = "password"

# Run demo (simulated)
python test_data/demo_automation.py

# Run main automation
python automation_scripts/network_automation.py
```

### Project Structure
```
group-saisys-network-automation/
├── automation_scripts/          # Python automation orchestration
├── netconf_client/              # NETCONF protocol implementation
├── yang_models/                 # YANG data models
├── test_data/                   # Testing and demo scripts
├── documentation/               # Comprehensive guides
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

### Dependencies
- paramiko >= 2.11.0 (SSH)
- lxml >= 4.9.0 (XML)
- requests >= 2.28.0 (Webhooks)
- urllib3, python-dateutil, python-dotenv

### Technologies
- **Protocol**: NETCONF (RFC 6241)
- **Data Model**: YANG (RFC 6020)
- **Transport**: SSH over port 830
- **Language**: Python 3.8+
- **Integration**: Microsoft Teams webhooks

### Architecture
1. **NETCONF Client**: Low-level protocol implementation
2. **Network Automation Manager**: High-level orchestration
3. **Teams Notifier**: Change notifications
4. **Configuration Management**: YAML/JSON support

### Configuration Changes
The system applies three standardized changes:
1. Interface description update
2. IPv4 address modification
3. MTU size adjustment

### Team
**Group Saisys Development Team**
- Date: December 1, 2025
- Project: DEVASC Activity 5
- Focus: Network Programmability & Automation

### Documentation
See `/documentation` for detailed architecture, design decisions, and team reflection.

### License
Internal Group Saisys Project
