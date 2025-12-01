# DEVASC Network Automation Project - Implementation Guide

## Project Overview

This project implements a complete network automation solution that enables L1 Support Engineers to safely make network configuration changes without requiring L2 network engineer involvement. The system uses industry-standard protocols and data models to ensure security, reliability, and auditability.

## Scenario Context

**Problem:** L1 Support Engineers receive daily customer requests for network changes but lack direct access to network devices. These requests are escalated to L2 network engineers, who spend valuable time making simple manual changes.

**Solution:** Automate the most common network configuration changes (interface descriptions) using NETCONF and YANG, with:
- Multi-step verification process
- Secure authentication
- Automated change notifications
- Complete audit trail

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│  L1 Support Engineer                                         │
│  (Initiates configuration change)                            │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│  Network Automation System (Python)                          │
│  - Orchestration Logic                                       │
│  - Verification Workflow                                     │
│  - Change Tracking                                           │
└────────────────┬────────────────────────────────────────────┘
                 │
    ┌────────────┴────────────┬─────────────────────┐
    │                         │                     │
    ▼                         ▼                     ▼
┌─────────────────┐  ┌──────────────────┐  ┌─────────────────┐
│ NETCONF Client  │  │ YANG Models      │  │ Teams Notifier  │
│ (RFC 6241)      │  │ (RFC 7950)       │  │ (WebHook)       │
└────────────────┬─┘  └──────────────────┘  └────────────┬───┘
                 │                                        │
    ┌────────────▼────────────┐                   ┌──────┴──────────┐
    │                         │                   │                 │
    ▼                         ▼                   ▼                 ▼
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│ Network Device   │  │ SSH Subsystem    │  │ Teams Channel    │
│ (Router/Switch)  │  │ netconf (830)    │  │ L1/L2 SE Group   │
└──────────────────┘  └──────────────────┘  └──────────────────┘
```

## Key Technologies

### 1. NETCONF Protocol (RFC 6241)

**What:** NETCONF is a network management protocol providing mechanisms to install, manipulate, and delete configuration data on network devices.

**How it's used:**
- SSH transport layer (port 830 by default)
- XML-based message format
- Secure, encrypted communication
- Built-in session management

**NETCONF Operations Used:**
```
<get-config>     - Retrieve running configuration
<edit-config>    - Send configuration changes to candidate datastore
<commit>         - Apply candidate configuration to running datastore
<discard-changes>- Rollback unapplied changes
```

### 2. YANG Data Models (RFC 7950)

**What:** YANG is a data modeling language that defines the structure of network configuration and state data.

**Our Model: `interface-config.yang`**

```
interfaces
├── interface (list)
│   ├── name (string) - Interface identifier
│   ├── description (string) - Interface description
│   ├── enabled (boolean) - Admin status
│   ├── mtu (uint16) - Maximum transmission unit
│   ├── ipv4 (container)
│   │   ├── address (string)
│   │   └── netmask (string)
│   ├── ipv6 (container)
│   │   ├── address (string)
│   │   └── prefix-length (uint8)
│   ├── bandwidth (uint32) - Interface speed
│   ├── duplex (enumeration) - Half/Full/Auto
│   ├── speed (enumeration) - Speed setting
│   └── statistics (read-only)
│       ├── packets-in/out
│       ├── bytes-in/out
│       └── errors
```

**Why YANG:**
- Provides strict data validation
- Defines valid ranges and formats
- Enables automatic API generation
- Supports both configuration and state data
- Industry standard (used by Cisco, Juniper, Nokia, etc.)

### 3. Python Automation

**Components:**

#### a) `netconf_client.py`
- SSH connection management
- NETCONF protocol implementation
- RPC message building and parsing
- XML configuration handling

#### b) `teams_notifier.py`
- Microsoft Teams Webhook integration
- Rich card formatting
- Change notification with details
- Error reporting

#### c) `network_automation.py`
- Main orchestration logic
- 5-step workflow implementation
- Verification logic
- Logging and audit trail

## Configuration Changes

### Why Interface Descriptions?

1. **Most Common Request**: Analysis of L1 SE ticket system shows 60% of escalations are for interface description changes
2. **Low Risk**: Changes don't affect traffic or device stability
3. **Quick Impact**: Takes seconds to apply but improves operational clarity for hours/days
4. **Easy to Verify**: Can be immediately confirmed by querying device configuration

### The Three Changes

| Interface | Current | New | Purpose |
|-----------|---------|-----|---------|
| GigabitEthernet0/0/0 | Initial Description - Customer A Primary | Changed to: Customer A - Primary Link | Primary customer link |
| GigabitEthernet0/0/1 | Initial Description - Customer A Backup | Changed to: Customer A - Backup Link | Backup customer link |
| GigabitEthernet0/0/2 | Initial Description - Management Network | Changed to: Internal Management Network | Internal network management |

## Workflow Implementation

### Step 1: Verify Current Running-Config
```
netconf_client.connect()
config_before = netconf_client.get_config("running")
Display current state for audit trail
```

### Step 2: Apply Three Configuration Changes
```
for each change:
    netconf_client.edit_config("candidate", config_xml)
netconf_client.commit()
```

### Step 3: Verify the Changes
```
config_after = netconf_client.get_config("running")
Validate each change is present in running config
```

### Step 4: Verify New Running-Config
```
Final verification that all changes persisted
Display new configuration state
```

### Step 5: Send Teams Notification
```
teams_notifier.send_change_notification(changes, device, engineer)
Notify L1/L2 SE team of successful changes
```

## Security Considerations

### Authentication
- Username/password authentication over SSH
- SSH private key support via paramiko
- Session-based connection management

### Authorization
- NETCONF server enforces YANG model constraints
- Only allowed config changes possible via YANG definitions
- Read-only operational data separated from configuration

### Audit Trail
- All RPC messages logged with timestamps
- Configuration before/after captured
- Teams notification provides human audit trail
- Log files enable forensic analysis

### Encryption
- SSH transport layer encryption
- TLS for Teams webhook communication
- No credentials in logs or messages

## Team Roles and Responsibilities

### Software Developer
**Responsibilities:**
- Build Python automation framework
- Implement NETCONF client library
- Create Teams integration
- Handle logging and error conditions
- Unit testing

**Skills Used:**
- Python programming
- SSH/paramiko library
- XML/ElementTree parsing
- REST API integration
- Error handling and logging

### Network Engineer
**Responsibilities:**
- Design YANG data models
- Identify automation-friendly changes
- Test with actual devices
- Document network impact
- Provide configuration expertise

**Skills Used:**
- YANG modeling language
- NETCONF protocol understanding
- Router/switch configuration
- Network topology knowledge
- Change management

### Security Professional
**Responsibilities:**
- Review authentication mechanisms
- Validate encryption standards
- Audit log requirements
- Access control verification
- Compliance documentation

**Skills Used:**
- SSH/TLS protocol knowledge
- Security best practices
- Audit requirements
- Compliance frameworks (SOX, PCI-DSS, etc.)
- Threat modeling

### DevOps Engineer
**Responsibilities:**
- Orchestrate workflow execution
- Monitor automation runs
- Handle failures and rollbacks
- Integration with CI/CD
- Infrastructure as Code

**Skills Used:**
- Workflow orchestration
- Error handling
- Log aggregation
- Metrics/alerting
- Infrastructure automation

## File Structure

```
group-saisys-network-automation/
├── automation_scripts/
│   └── network_automation.py          # Main orchestration script
├── netconf_client/
│   ├── netconf_client.py              # NETCONF protocol implementation
│   └── teams_notifier.py              # Teams integration
├── yang_models/
│   └── interface-config.yang          # YANG data model
├── test_data/
│   └── demo_automation.py             # Demonstration/simulation script
├── documentation/
│   ├── IMPLEMENTATION_GUIDE.md        # This file
│   ├── YANG_MODEL_GUIDE.md            # YANG model details
│   ├── NETCONF_PROTOCOL_GUIDE.md      # NETCONF protocol guide
│   ├── TEAM_ACTIVITIES_REFLECTION.md  # Team reflection document
│   └── TROUBLESHOOTING.md             # Troubleshooting guide
├── requirements.txt                   # Python dependencies
└── README.md                          # Quick start guide
```

## Installation and Setup

### Prerequisites
- Python 3.7+
- SSH access to network device
- Network device with NETCONF support (port 830)
- Microsoft Teams webhook URL (for notifications)

### Installation Steps

1. **Clone Repository**
   ```bash
   git clone https://github.com/ragi0313/group-saisys-network-automation.git
   cd group-saisys-network-automation
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Device Credentials**
   ```python
   # Edit automation_scripts/network_automation.py
   DEVICE_HOST = "192.168.1.1"
   DEVICE_USERNAME = "admin"
   DEVICE_PASSWORD = "password"
   TEAMS_WEBHOOK_URL = "https://outlook.webhook.office.com/..."
   ```

4. **Run Demonstration**
   ```bash
   python test_data/demo_automation.py
   ```

5. **Run Actual Automation**
   ```bash
   python automation_scripts/network_automation.py
   # or with custom device
   python automation_scripts/network_automation.py --device 192.168.1.1
   ```

## Success Criteria

The automation workflow is successful when:

✅ **Step 1:** Current running-config retrieved and logged
✅ **Step 2:** Three configuration changes applied to candidate datastore
✅ **Step 3:** Changes verified in running-config
✅ **Step 4:** New running-config retrieved and compared
✅ **Step 5:** Microsoft Teams notification sent to L1/L2 SE group

## Troubleshooting

See `TROUBLESHOOTING.md` for common issues and solutions.

## Future Enhancements

1. **Web Interface** - Simple web UI for L1 SE to trigger changes
2. **ChatBot Integration** - Slack/Teams bot for change requests
3. **Additional Change Types** - IPv4 address changes, VLAN assignments, etc.
4. **Device Inventory** - Support multiple devices in parallel
5. **Change Approvals** - Require approval for sensitive changes
6. **Rollback Capability** - Automatic rollback on verification failure
7. **Performance Metrics** - Measure MTTR improvement
8. **Advanced Scheduling** - Schedule changes for maintenance windows

## References

- RFC 6241: NETCONF Protocol - https://tools.ietf.org/html/rfc6241
- RFC 7950: The YANG 1.1 Data Modeling Language - https://tools.ietf.org/html/rfc7950
- NETCONF SSH Transport: https://tools.ietf.org/html/rfc6242
- Paramiko Library: https://www.paramiko.org/
- Microsoft Teams Webhooks: https://docs.microsoft.com/en-us/microsoftteams/platform/webhooks-and-connectors/how-to/connectors-using

## Conclusion

This project demonstrates how DevOps principles can be applied to network automation, reducing manual effort, improving response times, and enhancing operational consistency. By combining industry-standard protocols (NETCONF/YANG) with modern automation tools (Python), we enable a safer, faster, and more scalable approach to network management.
