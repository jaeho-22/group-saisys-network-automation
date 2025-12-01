# YANG Data Model Documentation

## Overview

This document provides detailed documentation of the YANG data model used for interface configuration in the Group Saisys Network Automation system.

**Model Name:** `interface-config`
**Namespace:** `http://example.com/ns/interface-config`
**Version:** 1.0
**Date:** 2024-12-01

## YANG Language Basics

YANG (RFC 7950) is a hierarchical data modeling language used to define the structure of configuration and state data in network devices.

### Basic Concepts

#### 1. Container
A container is a grouping of data nodes. It represents a category or section.

```yang
container interfaces {
    description "Interface configuration container";
    
    // Child nodes...
}
```

#### 2. List
A list represents multiple instances of the same data structure. Lists require a key for unique identification.

```yang
list interface {
    key "name";  // Interface name is the unique identifier
    description "List of network interfaces";
    
    // List entries...
}
```

#### 3. Leaf
A leaf is a terminal node that contains a single data value.

```yang
leaf name {
    type string;
    description "Interface name";
}
```

#### 4. Leaf-List
A leaf-list is a list of simple values (not a complex structure).

```yang
leaf-list dns-server {
    type string;
    description "DNS server addresses";
}
```

#### 5. Type System
YANG provides a comprehensive type system:

```yang
leaf enabled {
    type boolean;           // true or false
}

leaf mtu {
    type uint16 {
        range "68 .. 65535";  // Valid range
    }
    default "1500";         // Default value
}

leaf speed {
    type enumeration {      // Fixed set of values
        enum "auto";
        enum "10";
        enum "100";
        enum "1000";
    }
    default "auto";
}

leaf address {
    type string;            // Any string value
}

leaf bandwidth {
    type uint32;
    units "kbps";           // Units for documentation
}
```

## Interface Configuration Model Structure

### Root Container: `interfaces`

```
interfaces (container)
│
└── interface (list, key: name) [1..n instances]
    │
    ├── name (string) [MANDATORY]
    │   └── Interface identifier (e.g., GigabitEthernet0/0/0)
    │
    ├── description (string)
    │   └── Human-readable interface label
    │
    ├── enabled (boolean)
    │   └── Administrative enable/disable (default: true)
    │
    ├── mtu (uint16, range: 68-65535)
    │   └── Maximum Transmission Unit size (default: 1500)
    │
    ├── ipv4 (container, optional presence)
    │   ├── address (string)
    │   │   └── IPv4 address in dotted decimal (e.g., 192.168.1.1)
    │   └── netmask (string)
    │       └── IPv4 netmask in dotted decimal (e.g., 255.255.255.0)
    │
    ├── ipv6 (container, optional presence)
    │   ├── address (string)
    │   │   └── IPv6 address in standard notation
    │   └── prefix-length (uint8, range: 1-128)
    │       └── IPv6 prefix length
    │
    ├── bandwidth (uint32)
    │   └── Interface speed in kbps
    │
    ├── duplex (enumeration)
    │   ├── auto (default)
    │   ├── full
    │   └── half
    │
    ├── speed (enumeration)
    │   ├── auto (default)
    │   ├── 10 (10 Mbps)
    │   ├── 100 (100 Mbps)
    │   ├── 1000 (1 Gbps)
    │   └── 10000 (10 Gbps)
    │
    └── statistics (container, read-only config=false)
        ├── packets-in (uint64)
        ├── packets-out (uint64)
        ├── bytes-in (uint64)
        ├── bytes-out (uint64)
        └── errors (uint64)
```

### Operational State: `interfaces-state`

```
interfaces-state (container, config=false)
│
└── interface (list, key: name) [read-only]
    ├── name (string)
    ├── oper-status (enumeration)
    │   ├── up
    │   ├── down
    │   └── testing
    ├── admin-status (enumeration)
    │   ├── up
    │   ├── down
    │   └── testing
    └── last-change (string)
```

## YANG Features Used

### 1. Presence Container (IPv4/IPv6)
```yang
container ipv4 {
    presence "IPv4 configuration";  // Indicates this container may or may not exist
    // ...
}
```
**Use Case:** Indicates that IPv4 configuration is optional. An interface may have none, one, or multiple address configurations.

### 2. Enumeration (Speed, Duplex)
```yang
leaf speed {
    type enumeration {
        enum "auto" {
            description "Auto-negotiation";
        }
        enum "10" {
            description "10 Mbps";
        }
    }
    default "auto";
}
```
**Use Case:** Restricts values to a predefined set, preventing invalid configurations.

### 3. Range Constraints (MTU, Prefix-Length)
```yang
leaf mtu {
    type uint16 {
        range "68 .. 65535";
    }
    default "1500";
}
```
**Use Case:** Ensures only valid values are accepted (MTU must be between 68 and 65535 bytes).

### 4. Units (Bandwidth)
```yang
leaf bandwidth {
    type uint32;
    units "kbps";
}
```
**Use Case:** Documents the unit of measurement for clarity and API documentation.

### 5. Config vs State Separation
```yang
container statistics {
    config false;  // This is operational state, not configuration
    
    leaf packets-in {
        type uint64;
    }
}
```
**Use Case:** YANG distinguishes between configuration data (config true, default) and operational state (config false). This prevents administrators from trying to manually set statistic values.

### 6. RPC Operations
```yang
rpc reset-interface {
    description "Reset interface to default configuration";
    input {
        leaf interface-name {
            type string;
            mandatory true;
        }
    }
    output {
        leaf status {
            type string;
        }
    }
}
```
**Use Case:** Defines callable procedures for administrative actions beyond simple data modification.

## Configuration Examples

### Example 1: Simple Interface Update
```xml
<interfaces xmlns="http://example.com/ns/interface-config">
  <interface>
    <name>GigabitEthernet0/0/0</name>
    <description>Customer A - Primary Link</description>
    <enabled>true</enabled>
  </interface>
</interfaces>
```

### Example 2: Interface with IPv4 Configuration
```xml
<interfaces xmlns="http://example.com/ns/interface-config">
  <interface>
    <name>GigabitEthernet0/0/1</name>
    <description>Customer A - Backup Link</description>
    <enabled>true</enabled>
    <mtu>1500</mtu>
    <ipv4>
      <address>192.168.2.1</address>
      <netmask>255.255.255.0</netmask>
    </ipv4>
    <bandwidth>1000000</bandwidth>
    <speed>1000</speed>
    <duplex>full</duplex>
  </interface>
</interfaces>
```

### Example 3: Multiple Interfaces
```xml
<interfaces xmlns="http://example.com/ns/interface-config">
  <interface>
    <name>GigabitEthernet0/0/0</name>
    <description>Customer A - Primary</description>
  </interface>
  <interface>
    <name>GigabitEthernet0/0/1</name>
    <description>Customer A - Backup</description>
  </interface>
  <interface>
    <name>GigabitEthernet0/0/2</name>
    <description>Internal Management</description>
  </interface>
</interfaces>
```

## Design Rationale

### Why This YANG Model?

1. **Simplicity**
   - Focuses on most commonly changed parameters
   - Easy for L1 SE to understand and use
   - Reduces cognitive load for change requests

2. **Completeness**
   - Includes all essential interface parameters
   - Allows future expansion without breaking changes
   - Follows standard interface configuration patterns

3. **Safety**
   - Type constraints prevent invalid configurations
   - Range validation ensures values are within acceptable limits
   - Separation of configuration and state prevents accidental state modification

4. **Scalability**
   - List structure allows unlimited interfaces
   - Can be extended with additional containers for routing, QoS, security, etc.
   - Supports multiple devices through same model

5. **Standards Compliance**
   - Based on RFC 7950 YANG language specification
   - Compatible with standard NETCONF tools
   - Follows naming conventions from IETF standards

## Extension Points

The model is designed for future enhancements:

### Additional Parameters
```yang
container qos {
    // Quality of Service configuration
}

container security {
    // Interface security settings (port security, etc.)
}

container vlan {
    // VLAN membership and tagging
}

container routing {
    // Dynamic routing protocol configuration
}
```

### Additional Statistics
```yang
leaf drops {
    type uint64;
    description "Number of dropped packets";
}

leaf crc-errors {
    type uint64;
    description "CRC error count";
}

leaf collisions {
    type uint64;
    description "Collision count (half-duplex only)";
}
```

### RPC Operations
```yang
rpc show-interface-details {
    // More detailed statistics
}

rpc clear-interface-counters {
    // Reset statistics
}

rpc interface-diagnostic {
    // Run diagnostics
}
```

## YANG Validation

### YANG Validator Commands

```bash
# Using pyang (YANG validator)
pyang --strict interface-config.yang

# Generate tree representation
pyang -f tree interface-config.yang

# Generate HTML documentation
pyang -f html interface-config.yang -o interface-config.html
```

### Expected Tree Output
```
module: interface-config
  +--rw interfaces
  |  +--rw interface* [name]
  |     +--rw name                string
  |     +--rw description?        string
  |     +--rw enabled?            boolean
  |     +--rw mtu?                uint16
  |     +--rw ipv4?
  |     |  +--rw address?         string
  |     |  +--rw netmask?         string
  |     +--rw ipv6?
  |     |  +--rw address?         string
  |     |  +--rw prefix-length?   uint8
  |     +--rw bandwidth?          uint32
  |     +--rw duplex?             enumeration
  |     +--rw speed?              enumeration
  |     +--ro statistics?
  |        +--ro packets-in?      uint64
  |        +--ro packets-out?     uint64
  |        +--ro bytes-in?        uint64
  |        +--ro bytes-out?       uint64
  |        +--ro errors?          uint64
  +--ro interfaces-state
     +--ro interface* [name]
        +--ro name              string
        +--ro oper-status?      enumeration
        +--ro admin-status?     enumeration
        +--ro last-change?      string
```

## Integration with NETCONF

### NETCONF Edit-Config Example
```xml
<?xml version="1.0" encoding="UTF-8"?>
<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="101">
  <edit-config>
    <target>
      <candidate/>
    </target>
    <config>
      <interfaces xmlns="http://example.com/ns/interface-config">
        <interface>
          <name>GigabitEthernet0/0/0</name>
          <description>Updated Description</description>
        </interface>
      </interfaces>
    </config>
  </edit-config>
</rpc>
```

### NETCONF Get-Config Example
```xml
<?xml version="1.0" encoding="UTF-8"?>
<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="102">
  <get-config>
    <source>
      <running/>
    </source>
    <filter type="subtree">
      <interfaces xmlns="http://example.com/ns/interface-config"/>
    </filter>
  </get-config>
</rpc>
```

## References

- RFC 7950: The YANG 1.1 Data Modeling Language
- RFC 6241: NETCONF Protocol
- YANG Modular Network Models: https://tools.ietf.org/wg/netmod/
- Pyang Tool: https://github.com/mbj4668/pyang
