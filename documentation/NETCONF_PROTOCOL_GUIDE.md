# NETCONF Protocol Implementation Guide

## Overview

NETCONF (Network Configuration Protocol) is defined in RFC 6241. It provides a standardized mechanism for network device configuration management using a client-server model over secure transport (typically SSH).

## NETCONF Architecture

### Layered Model

```
┌─────────────────────────────────┐
│   NETCONF Messages              │
│   (RPC, RPC-reply)              │
├─────────────────────────────────┤
│   Operations Layer              │
│   (get, edit-config, commit)    │
├─────────────────────────────────┤
│   Content Layer                 │
│   (XML data models via YANG)    │
├─────────────────────────────────┤
│   Transport Session Layer       │
│   (NETCONF over SSH)            │
├─────────────────────────────────┤
│   SSH Protocol (RFC 5322)       │
├─────────────────────────────────┤
│   TCP/IP                        │
└─────────────────────────────────┘
```

## NETCONF Message Format

### Basic RPC Message Structure

```xml
<?xml version="1.0" encoding="UTF-8"?>
<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="1">
  <!-- Operation details -->
</rpc>
]]>]]>
```

### Message Framing

NETCONF uses a specific framing mechanism:
- Each message ends with `]]>]]>` delimiter
- Allows multiple messages in single SSH session
- Chunked-framing extension available for large messages

## Core NETCONF Operations

### 1. Hello - Session Establishment

**Client Hello:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<hello xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <capabilities>
    <capability>urn:ietf:params:netconf:base:1.0</capability>
    <capability>urn:ietf:params:netconf:base:1.1</capability>
  </capabilities>
</hello>
]]>]]>
```

**Server Response:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<hello xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <capabilities>
    <capability>urn:ietf:params:netconf:base:1.0</capability>
    <capability>urn:ietf:params:netconf:base:1.1</capability>
    <capability>urn:ietf:params:netconf:capability:startup:1.0</capability>
    <capability>urn:ietf:params:netconf:capability:url:1.0</capability>
  </capabilities>
  <session-id>1</session-id>
</hello>
]]>]]>
```

**What's Happening:**
- Client announces supported NETCONF versions
- Server responds with session ID and its capabilities
- Session ID used in log correlation
- Capabilities determine available operations

### 2. Get-Config - Retrieve Configuration

**Request:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="2">
  <get-config>
    <source>
      <running/>
    </source>
    <filter type="subtree">
      <interfaces xmlns="http://example.com/ns/interface-config"/>
    </filter>
  </get-config>
</rpc>
]]>]]>
```

**Response:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<rpc-reply xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="2">
  <data>
    <interfaces xmlns="http://example.com/ns/interface-config">
      <interface>
        <name>GigabitEthernet0/0/0</name>
        <description>Customer Link</description>
        <enabled>true</enabled>
      </interface>
    </interfaces>
  </data>
</rpc-reply>
]]>]]>
```

**Parameters:**
- `<source>`: Where to get data (running, candidate, startup)
- `<filter>`: Optional filter to reduce data volume
- `<data>`: Returned configuration matching YANG model

### 3. Edit-Config - Apply Changes

**Request:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="3">
  <edit-config>
    <target>
      <candidate/>
    </target>
    <default-operation>merge</default-operation>
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
]]>]]>
```

**Response:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<rpc-reply xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="3">
  <ok/>
</rpc-reply>
]]>]]>
```

**Key Concepts:**
- `<target>`: Usually "candidate" (staging area) before commit
- `<default-operation>`: 
  - `merge`: Combine with existing config
  - `replace`: Replace entire config
  - `none`: Explicit operation per node
- `<config>`: XML data matching YANG model
- `<ok/>`: Success confirmation

### 4. Commit - Apply Candidate to Running

**Request:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="4">
  <commit/>
</rpc>
]]>]]>
```

**Response:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<rpc-reply xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="4">
  <ok/>
</rpc-reply>
]]>]]>
```

**What Happens:**
1. Validates candidate configuration against YANG models
2. Checks for conflicts
3. If valid, applies to running configuration
4. Old running config typically saved as rollback point

### 5. Discard-Changes - Revert Candidate

**Request:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="5">
  <discard-changes/>
</rpc>
]]>]]>
```

**Response:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<rpc-reply xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="5">
  <ok/>
</rpc-reply>
]]>]]>
```

**Effect:**
- Candidate datastore reverted to running datastore
- Pending changes discarded
- No impact on active device configuration

## Configuration Datastores

### Three-Layer Model

```
┌──────────────────────┐
│   Running Config     │  Active configuration on device
│  (Active)            │  - Changes have immediate effect
└──────────────────────┘
         ▲
         │ commit
         │
┌──────────────────────┐
│   Candidate Config   │  Staging area for changes
│  (Proposed)          │  - Changes validated
└──────────────────────┘
         ▲
         │ edit-config
         │
┌──────────────────────┐
│   Startup Config     │  Configuration loaded on boot
│  (Persistent)        │  - Used for recovery
└──────────────────────┘
```

### Datastore Concepts

**Running (Config=true):**
- Currently active configuration
- Changes applied via commit
- Persisted based on device behavior

**Candidate (Config=true):**
- Staging area for proposed changes
- Can discard without affecting device
- Can commit to make running
- Optional (not all devices support)

**Startup (Config=true):**
- Configuration loaded at boot
- May differ from running
- Usually synchronized on commit

## Error Handling

### Success Response
```xml
<rpc-reply xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="X">
  <ok/>
</rpc-reply>
```

### Error Response
```xml
<rpc-reply xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="X">
  <rpc-error>
    <error-type>protocol</error-type>
    <error-tag>operation-failed</error-tag>
    <error-severity>error</error-severity>
    <error-message>Interface not found</error-message>
    <error-info>
      <bad-element>interface-name</bad-element>
    </error-info>
  </rpc-error>
</rpc-reply>
```

### Error Categories

**By Type:**
- `transport`: SSH connection issue
- `rpc`: NETCONF protocol issue
- `protocol`: Protocol version mismatch
- `application`: Device/model specific

**By Severity:**
- `warning`: Operation succeeded but with warnings
- `error`: Operation failed
- `critical`: Critical error, may need recovery

## Implementation Details in Our Project

### SSH Transport (RFC 6242)

**Connection Setup:**
```python
client = paramiko.SSHClient()
client.connect(host, port=830, username=user, password=pwd)
channel = client.get_transport().open_session()
channel.invoke_subsystem('netconf')
```

**Why Port 830:**
- IANA assigned port for NETCONF SSH subsystem
- Allows NETCONF to run alongside regular SSH on port 22
- Some devices may use port 22 with 'netconf' subsystem

**Security:**
- SSH provides encryption
- Mutual authentication (client + server)
- Protection against MITM attacks
- Perfect forward secrecy with SSH keys

### Message ID Tracking

Each RPC needs unique message-id:
```python
self.message_id = 1

def send_rpc(self, rpc):
    # Use current message-id
    rpc = rpc.format(message_id=self.message_id)
    self.message_id += 1
    
    # Send and receive
    self.channel.send(rpc.encode('utf-8'))
    response = self.channel.recv(65536)
```

**Why Important:**
- Correlates requests with responses
- Supports asynchronous operation
- Enables logging and debugging
- Required by RFC 6241

### XML Namespace Handling

```python
# Device uses namespace prefixes
namespaces = {
    'netconf': 'urn:ietf:params:xml:ns:netconf:base:1.0',
    'ifcfg': 'http://example.com/ns/interface-config'
}

# Must specify in XPath
interfaces = root.findall('.//ifcfg:interface', namespaces)
```

**Common Pitfall:**
- Forgetting namespaces causes findall() to return empty
- Every NETCONF device uses namespaces
- Must be handled in client implementation

## Standards and References

- **RFC 6241**: NETCONF Protocol (core specification)
- **RFC 6242**: Using NETCONF over SSH
- **RFC 6243**: NETCONF "Candidate" Datastore Capability
- **RFC 8174**: Ambiguity of Uppercase vs Lowercase in RFCs

## Comparison with Other Management Protocols

| Feature | SNMP | NETCONF | REST API |
|---------|------|---------|----------|
| Transport | UDP | SSH | HTTP/HTTPS |
| Security | Community strings | SSH keys | OAuth |
| Config Capability | Limited | Full | Device specific |
| Transaction Support | No | Yes (commit) | No |
| Large Data | Difficult | Efficient | Good |
| Learning Curve | Easy | Medium | Hard |
| Standardization | RFC | RFC | Varies |

## Conclusion

NETCONF provides a secure, standardized, and efficient way to manage network configuration at scale. The protocol's commit model and transaction support make it suitable for critical infrastructure where consistency is paramount. Our implementation demonstrates core NETCONF features required for enterprise network automation.
