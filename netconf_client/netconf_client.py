"""
NETCONF Client Implementation
RFC 6241 - NETCONF Protocol

This module provides a NETCONF client for communicating with
network devices that support the NETCONF protocol over SSH.
"""

import paramiko
import xml.etree.ElementTree as ET
from xml.dom import minidom
import socket
import time
from typing import Tuple, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class NetconfClient:
    """
    NETCONF Protocol Client Implementation.
    
    Supports RFC 6241 compliant NETCONF protocol operations over SSH.
    Default port: 830 (NETCONF over SSH)
    """

    def __init__(self, host: str, port: int = 830, username: str = "", 
                 password: str = "", timeout: int = 30):
        """
        Initialize NETCONF client.
        
        Args:
            host: Device IP address or hostname
            port: SSH port (default 830 for NETCONF)
            username: Authentication username
            password: Authentication password
            timeout: Connection timeout in seconds
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.timeout = timeout
        self.client = None
        self.transport = None
        self.channel = None
        self.session_id = None
        self.message_id = 1

    def connect(self) -> bool:
        """
        Establish NETCONF connection to device.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            logger.info(f"Connecting to {self.host}:{self.port}")
            self.client.connect(
                hostname=self.host,
                port=self.port,
                username=self.username,
                password=self.password,
                timeout=self.timeout,
                look_for_keys=False,
                allow_agent=False
            )
            
            self.transport = self.client.get_transport()
            self.channel = self.transport.open_session()
            self.channel.invoke_subsystem('netconf')
            
            # Perform NETCONF hello exchange
            hello_resp = self._receive_hello()
            if hello_resp:
                logger.info(f"NETCONF connection established. Session ID: {self.session_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Connection failed: {str(e)}")
            return False

    def _receive_hello(self) -> bool:
        """Receive and parse NETCONF hello message."""
        try:
            hello_msg = self.channel.recv(65536).decode('utf-8')
            
            # Parse session ID from hello response
            if '<session-id>' in hello_msg:
                start = hello_msg.find('<session-id>') + len('<session-id>')
                end = hello_msg.find('</session-id>')
                self.session_id = hello_msg[start:end]
            
            # Send our hello message
            hello = self._build_hello()
            self.channel.send(hello.encode('utf-8') + b'\n')
            
            return True
        except Exception as e:
            logger.error(f"Hello exchange failed: {str(e)}")
            return False

    def _build_hello(self) -> str:
        """Build NETCONF hello message."""
        return """<?xml version="1.0" encoding="UTF-8"?>
<hello xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <capabilities>
    <capability>urn:ietf:params:netconf:base:1.0</capability>
    <capability>urn:ietf:params:netconf:base:1.1</capability>
  </capabilities>
</hello>]]>]]>"""

    def get_config(self, source: str = "running") -> Optional[str]:
        """
        Get configuration from device.
        
        Args:
            source: "running" or "candidate"
            
        Returns:
            XML configuration string or None
        """
        rpc = f"""<?xml version="1.0" encoding="UTF-8"?>
<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="{self.message_id}">
  <get-config>
    <source>
      <{source}/>
    </source>
  </get-config>
</rpc>]]>]]>"""
        
        self.message_id += 1
        return self._send_rpc(rpc)

    def edit_config(self, target: str = "candidate", config: str = "") -> bool:
        """
        Send configuration edit to device.
        
        Args:
            target: "candidate" or "running"
            config: XML configuration snippet
            
        Returns:
            bool: True if successful
        """
        rpc = f"""<?xml version="1.0" encoding="UTF-8"?>
<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="{self.message_id}">
  <edit-config>
    <target>
      <{target}/>
    </target>
    <default-operation>merge</default-operation>
    <config>
{config}
    </config>
  </edit-config>
</rpc>]]>]]>"""
        
        self.message_id += 1
        response = self._send_rpc(rpc)
        return response and '<ok/>' in response

    def commit(self) -> bool:
        """Commit candidate configuration to running."""
        rpc = f"""<?xml version="1.0" encoding="UTF-8"?>
<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="{self.message_id}">
  <commit/>
</rpc>]]>]]>"""
        
        self.message_id += 1
        response = self._send_rpc(rpc)
        return response and '<ok/>' in response

    def discard_changes(self) -> bool:
        """Discard candidate configuration changes."""
        rpc = f"""<?xml version="1.0" encoding="UTF-8"?>
<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="{self.message_id}">
  <discard-changes/>
</rpc>]]>]]>"""
        
        self.message_id += 1
        response = self._send_rpc(rpc)
        return response and '<ok/>' in response

    def _send_rpc(self, rpc: str) -> Optional[str]:
        """
        Send RPC command and receive response.
        
        Args:
            rpc: RPC message as XML string
            
        Returns:
            Response XML string or None
        """
        try:
            logger.debug(f"Sending RPC: {rpc[:100]}...")
            self.channel.send(rpc.encode('utf-8'))
            
            response = ""
            while True:
                chunk = self.channel.recv(65536).decode('utf-8', errors='ignore')
                if not chunk:
                    break
                response += chunk
                if ']]>]]>' in response:
                    break
            
            logger.debug(f"Response received: {response[:200]}...")
            return response
            
        except Exception as e:
            logger.error(f"RPC send failed: {str(e)}")
            return None

    def disconnect(self):
        """Close NETCONF session."""
        try:
            if self.channel:
                self.channel.close()
            if self.client:
                self.client.close()
            logger.info("NETCONF session closed")
        except Exception as e:
            logger.error(f"Disconnect failed: {str(e)}")

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()


class NetconfXmlBuilder:
    """Helper class for building NETCONF configuration XML."""

    @staticmethod
    def build_interface_config(interface_name: str, description: str = None,
                              ipv4_addr: str = None, ipv4_mask: str = None) -> str:
        """
        Build interface configuration XML.
        
        Args:
            interface_name: Interface name (e.g., "GigabitEthernet0/0/0")
            description: Interface description
            ipv4_addr: IPv4 address
            ipv4_mask: IPv4 netmask
            
        Returns:
            XML configuration string
        """
        config = f'<interfaces xmlns="http://example.com/ns/interface-config">\n'
        config += f'  <interface>\n'
        config += f'    <name>{interface_name}</name>\n'
        
        if description:
            config += f'    <description>{description}</description>\n'
        
        if ipv4_addr and ipv4_mask:
            config += f'    <ipv4>\n'
            config += f'      <address>{ipv4_addr}</address>\n'
            config += f'      <netmask>{ipv4_mask}</netmask>\n'
            config += f'    </ipv4>\n'
        
        config += f'    <enabled>true</enabled>\n'
        config += f'  </interface>\n'
        config += f'</interfaces>'
        
        return config

    @staticmethod
    def prettify_xml(xml_string: str) -> str:
        """Format XML string for readability."""
        try:
            dom = minidom.parseString(xml_string)
            return dom.toprettyxml(indent="  ")
        except:
            return xml_string
