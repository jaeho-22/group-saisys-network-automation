# Troubleshooting Guide

## Common Issues and Solutions

### Issue 1: SSH Connection Timeout

**Error Message:**
```
paramiko.ssh_exception.SSHException: Error reading SSH protocol banner
```

**Possible Causes:**
1. Device not reachable at specified IP:port
2. NETCONF subsystem not enabled on device
3. Wrong port (use 830 for NETCONF, not 22)
4. Device firewall blocking connection
5. SSH service disabled

**Solutions:**

**Step 1: Verify connectivity**
```bash
# From Windows PowerShell:
Test-Connection -ComputerName 192.168.1.1 -Count 4
```

**Step 2: Verify SSH port**
```bash
# Check if port 830 is open
Test-NetConnection -ComputerName 192.168.1.1 -Port 830
```

**Step 3: Verify SSH access**
```bash
# Install SSH client if needed (Windows 10+)
ssh admin@192.168.1.1 -p 830
```

**Step 4: Check device configuration**
- SSH must be enabled on device
- NETCONF subsystem must be configured
- User account must have access

**Example Cisco Config:**
```
ip ssh version 2
ssh rsa keypair-name default
netconf enabled
```

---

### Issue 2: Authentication Failed

**Error Message:**
```
paramiko.ssh_exception.AuthenticationException: Authentication failed
```

**Possible Causes:**
1. Wrong username or password
2. Account disabled
3. Too many failed attempts (lockout)
4. Different authentication method required (keys, certificates)

**Solutions:**

**Step 1: Verify credentials**
```bash
# Test credentials manually
ssh admin@192.168.1.1
# Enter password when prompted
```

**Step 2: Check account status**
- Verify account exists on device
- Check if account is locked
- Verify user has proper role/privilege level

**Step 3: Check failure threshold**
- Some devices lock accounts after N failed attempts
- Try resetting the account
- Wait if lockout timer is active

**Step 4: Use public key if configured**
```python
# Instead of password authentication:
client.connect(
    hostname=host,
    port=port,
    username=username,
    key_filename='/path/to/private/key',  # Use SSH key
    look_for_keys=True,
    allow_agent=True
)
```

---

### Issue 3: NETCONF Subsystem Not Available

**Error Message:**
```
paramiko.ssh_exception.SSHException: Subsystem 'netconf' not found
```

**Possible Causes:**
1. NETCONF not installed on device
2. NETCONF subsystem not mapped in SSH config
3. Using wrong subsystem name

**Solutions:**

**Step 1: Check if NETCONF is installed**
```bash
# SSH to device and verify NETCONF
ssh admin@192.168.1.1
show version | include NETCONF  # Cisco syntax
```

**Step 2: Check subsystem mapping**
- Verify SSH server has netconf subsystem configured
- Some devices use different subsystem names
- May need to explicitly enable NETCONF

**Example Cisco Configuration:**
```
! Enable NETCONF
netconf-yang enabled
```

**Step 3: Try alternative approaches**
- Some devices support NETCONF on port 22 with explicit subsystem
- Some use XML on RPC port instead
- Some require REST API instead

---

### Issue 4: XML Parsing Errors

**Error Message:**
```
xml.etree.ElementTree.ParseError: syntax error: line X, column Y
```

**Possible Causes:**
1. Malformed XML in response
2. Namespace issues
3. Incomplete response received
4. Binary data in response

**Solutions:**

**Step 1: Log the raw response**
```python
def _send_rpc(self, rpc: str) -> Optional[str]:
    try:
        self.channel.send(rpc.encode('utf-8'))
        response = ""
        while True:
            chunk = self.channel.recv(65536).decode('utf-8', errors='ignore')
            if not chunk:
                break
            response += chunk
            if ']]>]]>' in response:
                break
        
        # DEBUG: Log raw response
        with open('netconf_response.log', 'w') as f:
            f.write(response)
        
        return response
    except Exception as e:
        logger.error(f"RPC send failed: {str(e)}")
        return None
```

**Step 2: Check for complete response**
```python
# Ensure full response received
if ']]>]]>' not in response:
    logger.warning("Response may be incomplete")
    # Try receiving more data
    more_data = self.channel.recv(65536)
    response += more_data.decode('utf-8')
```

**Step 3: Handle namespaces properly**
```python
# Always specify namespaces
namespaces = {
    'rpc': 'urn:ietf:params:xml:ns:netconf:base:1.0',
    'ifcfg': 'http://example.com/ns/interface-config'
}

root = ET.fromstring(response)
# Use namespace prefix in XPath
data = root.find('.//rpc:data', namespaces)
```

**Step 4: Pretty print for debugging**
```python
def debug_xml(xml_string):
    try:
        root = ET.fromstring(xml_string)
        print(ET.tostring(root, encoding='unicode'))
    except ET.ParseError as e:
        print(f"Parse error: {e}")
        print(f"First 500 chars: {xml_string[:500]}")
```

---

### Issue 5: Configuration Commit Fails

**Error Message:**
```
<rpc-error>
  <error-type>application</error-type>
  <error-tag>operation-failed</error-tag>
  <error-message>Configuration validation failed: Interface not found</error-message>
</rpc-error>
```

**Possible Causes:**
1. Referenced interface doesn't exist
2. YANG model constraint violated
3. Conflicting configuration
4. Device resource limit exceeded

**Solutions:**

**Step 1: Verify interface exists**
```bash
# Check available interfaces
ssh admin@192.168.1.1
show interfaces
# Look for the interface name you're trying to configure
```

**Step 2: Check configuration for errors**
```python
# Test with simpler config first
config_xml = '''<interfaces xmlns="http://example.com/ns/interface-config">
  <interface>
    <name>GigabitEthernet0/0/0</name>
    <description>Test</description>
  </interface>
</interfaces>'''

if not client.edit_config("candidate", config_xml):
    # Get error details
    response = client._send_rpc(rpc)
    print(response)  # Shows error message
```

**Step 3: Discard and retry**
```python
# If commit fails, discard and try again
if not client.commit():
    logger.warning("Commit failed, discarding changes")
    client.discard_changes()
    # Review and fix configuration
```

**Step 4: Validate against YANG model**
- Check YANG model for constraints
- Verify value ranges and enumerations
- Ensure referenced objects exist
- Check for invalid parameter combinations

---

### Issue 6: Configuration Changes Not Persisting

**Symptom:**
Configuration appears applied but doesn't survive device reboot.

**Possible Causes:**
1. Device not saving configuration to startup-config
2. Only applied to running-config, not startup
3. Device has automatic rollback timer

**Solutions:**

**Step 1: Explicitly save configuration**
```bash
# SSH to device after commit
write memory  # Cisco syntax
save  # Juniper syntax
commit  # Some systems use commit to startup
```

**Step 2: Verify running vs startup**
```bash
show running-config | include Giga
show startup-config | include Giga
# Compare the two
```

**Step 3: Disable auto-rollback if active**
```bash
# Some devices auto-rollback changes after N minutes
show config-lock  # Check for rollback timer
# Disable if not needed
```

**Step 4: Modify automation to save explicitly**
```python
def commit_and_save(self):
    if self.commit():
        logger.info("Configuration committed to running")
        # Send save command via NETCONF RPC
        # or via separate CLI command
        return True
    return False
```

---

### Issue 7: Microsoft Teams Notification Not Sent

**Error Message:**
```
Error sending Teams notification: (requests.exceptions.Timeout)
```

**Possible Causes:**
1. Invalid webhook URL
2. Webhook URL expired
3. Network connectivity issue
4. Teams service down
5. Payload too large

**Solutions:**

**Step 1: Verify webhook URL**
```bash
# Test webhook with curl/PowerShell
$uri = "https://outlook.webhook.office.com/webhookb2/..."
$body = @{
    text = "Test message"
} | ConvertTo-Json

Invoke-RestMethod -Uri $uri -Method Post -ContentType 'application/json' -Body $body
```

**Step 2: Check webhook validity**
- Regenerate webhook URL in Teams
- Verify URL has not expired
- Ensure URL is correct (no extra spaces, etc)

**Step 3: Test connectivity**
```bash
# Test network connectivity to Teams
Test-NetConnection -ComputerName outlook.webhook.office.com -Port 443
```

**Step 4: Simplify payload**
```python
# Reduce payload complexity
simple_message = {
    "@type": "MessageCard",
    "@context": "https://schema.org/extensions",
    "summary": "Test message",
    "text": "Configuration changed"
}

response = requests.post(webhook_url, json=simple_message, timeout=10)
```

**Step 5: Add timeout handling**
```python
try:
    response = requests.post(
        webhook_url,
        json=card,
        timeout=5  # Shorter timeout
    )
except requests.exceptions.Timeout:
    logger.warning("Teams notification timed out, continuing")
    # Don't fail workflow if notification fails
```

---

### Issue 8: Memory or Resource Issues

**Error Message:**
```
Device memory full or resource exhausted
```

**Possible Causes:**
1. Device has limited resources
2. Large configuration retrieval
3. Too many simultaneous connections

**Solutions:**

**Step 1: Use filters in get-config**
```python
# Instead of retrieving all config:
# Only request what you need
filter_xml = '<interfaces xmlns="http://example.com/ns/interface-config"/>'
config = client.get_config("running")  # With filter parameter
```

**Step 2: Close unused sessions**
```python
# Always disconnect properly
client.disconnect()

# Or use context manager
with NetconfClient(host, user, pwd) as client:
    config = client.get_config("running")
# Automatically disconnects
```

**Step 3: Split large operations**
```python
# Instead of one big change:
# Apply changes one at a time
for interface in interfaces:
    client.edit_config("candidate", build_config(interface))
    if not client.commit():
        logger.error(f"Failed to apply config for {interface}")
        break
```

---

## Debugging Techniques

### Enable Debug Logging

```python
import logging

# Enable debug level logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Logs all operations
logger.debug(f"Sending RPC: {rpc}")
logger.debug(f"Response: {response}")
```

### Log All NETCONF Messages

```python
def _send_rpc(self, rpc: str) -> Optional[str]:
    # Log outgoing RPC
    with open('netconf.log', 'a') as f:
        f.write(f"\n=== OUTGOING RPC ===\n{rpc}\n")
    
    # Send and receive
    response = self.channel.recv(65536).decode('utf-8')
    
    # Log response
    with open('netconf.log', 'a') as f:
        f.write(f"\n=== RESPONSE ===\n{response}\n")
    
    return response
```

### Test with Simulation

```python
# Use demo_automation.py to test workflow
# without requiring actual device
python test_data/demo_automation.py
```

### Validate Configuration Before Applying

```python
# Validate against YANG model
def validate_config(config_xml):
    # Parse XML
    root = ET.fromstring(config_xml)
    
    # Check required fields
    # Validate ranges
    # Check enumerations
    
    return True  # or False with error details
```

---

## Performance Issues

### Slow Configuration Retrieval

**Problem:** `get_config()` takes 30+ seconds

**Solutions:**
1. Use filters to reduce data
2. Increase SSH session timeout
3. Check network latency
4. Consider pagination if supported

### Slow Commits

**Problem:** `commit()` takes 10+ seconds

**Solutions:**
1. Reduce number of changes
2. Batch related changes
3. Commit during low-traffic periods
4. Check device CPU load

---

## Getting Help

### Where to Find Information

1. **RFC 6241:** Complete NETCONF specification
2. **Vendor Documentation:** Device-specific NETCONF support
3. **YANG Model Documentation:** Data structure details
4. **Logs:** Always check logs first
5. **Community Forums:** Cisco, Juniper support communities

### Collecting Diagnostic Information

When asking for help, provide:
```
1. Full error message
2. Relevant log section (with debug enabled)
3. Network diagram (device IP, port, firewall rules)
4. Device type and software version
5. Steps to reproduce
6. What you've already tried
```

---

## Conclusion

Most NETCONF issues stem from:
1. Network connectivity (50%)
2. Authentication (25%)
3. XML/namespace handling (15%)
4. Device configuration (10%)

Start with network and authentication, then work backward through the stack to identify the root cause.
