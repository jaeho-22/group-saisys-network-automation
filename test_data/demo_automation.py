"""
Network Automation Demo Script
DEVASC Project Activity 5 - Demonstration

This script provides a simulated demonstration of the complete workflow
without requiring actual network devices. It shows all steps of the
automation process with realistic data.
"""

import sys
import os
import logging
from datetime import datetime
from typing import List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SimulatedNetconfConfig:
    """Simulated NETCONF device configuration."""
    
    INITIAL_CONFIG = """<?xml version="1.0" encoding="UTF-8"?>
<rpc-reply xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="1">
  <data>
    <interfaces xmlns="http://example.com/ns/interface-config">
      <interface>
        <name>GigabitEthernet0/0/0</name>
        <description>Initial Description - Customer A Primary</description>
        <enabled>true</enabled>
        <mtu>1500</mtu>
        <ipv4>
          <address>192.168.1.1</address>
          <netmask>255.255.255.0</netmask>
        </ipv4>
      </interface>
      <interface>
        <name>GigabitEthernet0/0/1</name>
        <description>Initial Description - Customer A Backup</description>
        <enabled>true</enabled>
        <mtu>1500</mtu>
        <ipv4>
          <address>192.168.2.1</address>
          <netmask>255.255.255.0</netmask>
        </ipv4>
      </interface>
      <interface>
        <name>GigabitEthernet0/0/2</name>
        <description>Initial Description - Management Network</description>
        <enabled>true</enabled>
        <mtu>1500</mtu>
        <ipv4>
          <address>10.0.0.1</address>
          <netmask>255.255.255.0</netmask>
        </ipv4>
      </interface>
    </interfaces>
  </data>
</rpc-reply>"""

    UPDATED_CONFIG = """<?xml version="1.0" encoding="UTF-8"?>
<rpc-reply xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="4">
  <data>
    <interfaces xmlns="http://example.com/ns/interface-config">
      <interface>
        <name>GigabitEthernet0/0/0</name>
        <description>Changed to: Customer A - Primary Link</description>
        <enabled>true</enabled>
        <mtu>1500</mtu>
        <ipv4>
          <address>192.168.1.1</address>
          <netmask>255.255.255.0</netmask>
        </ipv4>
      </interface>
      <interface>
        <name>GigabitEthernet0/0/1</name>
        <description>Changed to: Customer A - Backup Link</description>
        <enabled>true</enabled>
        <mtu>1500</mtu>
        <ipv4>
          <address>192.168.2.1</address>
          <netmask>255.255.255.0</netmask>
        </ipv4>
      </interface>
      <interface>
        <name>GigabitEthernet0/0/2</name>
        <description>Changed to: Internal Management Network</description>
        <enabled>true</enabled>
        <mtu>1500</mtu>
        <ipv4>
          <address>10.0.0.1</address>
          <netmask>255.255.255.0</netmask>
        </ipv4>
      </interface>
    </interfaces>
  </data>
</rpc-reply>"""


class DemoNetworkAutomation:
    """Demonstration of the network automation workflow."""
    
    CHANGES = [
        {
            "interface": "GigabitEthernet0/0/0",
            "description": "Changed to: Customer A - Primary Link",
            "change_type": "Interface description update"
        },
        {
            "interface": "GigabitEthernet0/0/1",
            "description": "Changed to: Customer A - Backup Link",
            "change_type": "Interface description update"
        },
        {
            "interface": "GigabitEthernet0/0/2",
            "description": "Changed to: Internal Management Network",
            "change_type": "Interface description update"
        }
    ]

    def run_demo(self) -> bool:
        """Execute the complete demonstration workflow."""
        logger.info("=" * 80)
        logger.info("DEVASC Network Automation Demo - Simulated Workflow")
        logger.info("=" * 80)
        
        try:
            # Step 1: Verify current running-config
            logger.info("\n[STEP 1/5] Verifying current running-config...")
            self._step_verify_current_config()
            
            # Step 2: Make three configuration changes
            logger.info("\n[STEP 2/5] Applying three configuration changes...")
            self._step_apply_changes()
            
            # Step 3: Verify the changes
            logger.info("\n[STEP 3/5] Verifying configuration changes...")
            self._step_verify_changes()
            
            # Step 4: Verify new running-config
            logger.info("\n[STEP 4/5] Verifying new running-config...")
            self._step_verify_new_config()
            
            # Step 5: Send Teams notification
            logger.info("\n[STEP 5/5] Sending Teams notification...")
            self._step_send_teams_notification()
            
            logger.info("\n" + "=" * 80)
            logger.info("✅ Demo Workflow COMPLETED SUCCESSFULLY")
            logger.info("=" * 80)
            return True
            
        except Exception as e:
            logger.error(f"Demo failed: {str(e)}", exc_info=True)
            return False

    def _step_verify_current_config(self):
        """Step 1: Display current running configuration."""
        logger.info("Connecting to device 192.168.1.1:830 (Simulated)")
        logger.info("✅ Connected to device")
        logger.info("Retrieving current running-config...")
        
        self._display_config("CURRENT RUNNING-CONFIG (BEFORE CHANGES)", 
                           SimulatedNetconfConfig.INITIAL_CONFIG)
        logger.info("✅ Current running-config retrieved successfully")

    def _step_apply_changes(self):
        """Step 2: Apply three configuration changes."""
        for idx, change in enumerate(self.CHANGES, 1):
            logger.info(f"\nApplying Change {idx}/3:")
            logger.info(f"  Interface: {change['interface']}")
            logger.info(f"  Action: {change['change_type']}")
            logger.info(f"  New Description: {change['description']}")
            
            # Simulate configuration send
            logger.info(f"  ✅ Configuration sent to candidate datastore")
        
        # Simulate commit
        logger.info("\nCommitting all changes to running-config...")
        logger.info("✅ All changes committed successfully")

    def _step_verify_changes(self):
        """Step 3: Verify applied changes."""
        logger.info("Verifying changes in device configuration...")
        
        for idx, change in enumerate(self.CHANGES, 1):
            interface = change['interface']
            logger.info(f"✅ Change {idx} verified: {interface}")
        
        logger.info("✅ Configuration changes verified")

    def _step_verify_new_config(self):
        """Step 4: Display new running configuration."""
        logger.info("Retrieving new running-config...")
        
        self._display_config("NEW RUNNING-CONFIG (AFTER CHANGES)", 
                           SimulatedNetconfConfig.UPDATED_CONFIG)
        logger.info("✅ New running-config verified successfully")

    def _step_send_teams_notification(self):
        """Step 5: Demonstrate Teams notification."""
        logger.info("Sending Microsoft Teams notification...")
        logger.info("\n" + "=" * 80)
        logger.info("MICROSOFT TEAMS MESSAGE PREVIEW")
        logger.info("=" * 80)
        
        teams_message = {
            "title": "🔧 Network Configuration Change Notification",
            "device": "192.168.1.1",
            "changed_by": "Network Automation System",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
            "status": "✅ Successfully Committed",
            "changes": [
                f"Interface {c['interface']}: {c['description']}"
                for c in self.CHANGES
            ],
            "protocol": "NETCONF (RFC 6241)",
            "data_model": "YANG (RFC 7950)"
        }
        
        import json
        logger.info(json.dumps(teams_message, indent=2))
        logger.info("=" * 80)
        logger.info("\n✅ Teams notification sent to L1/L2 SE group")

    def _display_config(self, title: str, config: str):
        """Display configuration in formatted output."""
        logger.info("\n" + "=" * 80)
        logger.info(f"   {title}")
        logger.info("=" * 80)
        
        # Pretty print the XML
        lines = config.split('\n')
        for line in lines:
            if line.strip():
                logger.info(line)
        
        logger.info("=" * 80 + "\n")


class ConfigurationChangesExplanation:
    """Explain the three configuration changes."""
    
    @staticmethod
    def display():
        """Display explanation of changes chosen."""
        logger.info("\n" + "=" * 80)
        logger.info("CONFIGURATION CHANGES RATIONALE")
        logger.info("=" * 80)
        
        explanation = """
WHY THESE CHANGES?
==================

1. INTERFACE DESCRIPTION CHANGES
   ✓ Most Common Support Request: L1 SE teams report that the most frequent
     customer request is interface description updates.
   
   ✓ Low Risk: Description changes have minimal impact on active network
     traffic and operations.
   
   ✓ Quick Turnaround: These changes can be executed within seconds,
     improving customer response time from hours to seconds.
   
   ✓ Clear Documentation: Updated descriptions help network operations
     teams understand interface purposes and customer assignments.


2. INTERFACE CONFIGURATION PATTERN
   ✓ Three Different Interfaces: Demonstrates capability to make multiple
     changes across different interfaces in a single operation.
   
   ✓ Customer A Interfaces: Primary and Backup links for a customer show
     a realistic multi-link scenario.
   
   ✓ Management Interface: Shows automation can be applied to both
     customer-facing and internal infrastructure interfaces.


BENEFITS TO L1 SUPPORT ENGINEERS
==================================
   • No longer need to escalate simple description changes
   • Self-service capability through simple web interface or chatbot
   • Reduce Mean Time to Resolution (MTTR) from hours to seconds
   • Automated notifications keep L2 team informed
   • Full audit trail of who made what changes and when


OPERATIONAL BENEFITS
====================
   • Reduce manual errors in configuration typing
   • 24/7 capability without requiring L2 engineer availability
   • Consistent configuration application
   • Automated verification of changes
   • Integration with team communication (Teams notifications)
        """
        logger.info(explanation)
        logger.info("=" * 80)


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    """Main entry point for demo."""
    
    # Display explanation
    ConfigurationChangesExplanation.display()
    
    # Run the demo
    demo = DemoNetworkAutomation()
    success = demo.run_demo()
    
    # Summary
    logger.info("\n" + "=" * 80)
    logger.info("DEMO SUMMARY")
    logger.info("=" * 80)
    logger.info("""
    ✅ Workflow Steps Demonstrated:
       1. ✓ Current configuration retrieval (before changes)
       2. ✓ Three configuration changes applied
       3. ✓ Changes verified and committed
       4. ✓ New configuration retrieved (after changes)
       5. ✓ Microsoft Teams notification sent
    
    ✅ Technologies Demonstrated:
       • NETCONF Protocol (RFC 6241)
       • YANG Data Modeling (RFC 7950)
       • Python Automation Orchestration
       • Microsoft Teams Integration
    
    ✅ Team Roles Demonstrated:
       • Software Developer: Built automation scripts
       • Network Engineer: Designed YANG models and device changes
       • Security Professional: Implemented secure NETCONF over SSH
       • DevOps: Orchestrated workflow and notification system
    """)
    logger.info("=" * 80)
    
    sys.exit(0 if success else 1)
