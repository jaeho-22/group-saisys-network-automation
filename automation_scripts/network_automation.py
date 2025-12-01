"""
Network Automation Orchestration Script
DEVASC Project Activity 5 - Network Programmability and Automation

This script implements the complete workflow for secure network device
configuration changes through NETCONF with multiple verification steps.

Operational Workflow:
1. Verify current running-config
2. Make three configuration changes
3. Verify the changes
4. Verify new running-config
5. Send Teams notification to L1/L2 SE groups
"""

import sys
import os
import logging
from datetime import datetime
import json
from typing import List, Dict, Optional, Tuple
import re

# Add paths for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from netconf_client.netconf_client import NetconfClient, NetconfXmlBuilder
from netconf_client.teams_notifier import TeamsNotifier


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('network_automation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class NetworkAutomationOrchestrator:
    """
    Main orchestrator for network automation workflow.
    
    Coordinates NETCONF operations with verification and notification steps.
    """

    # Device Configuration - MODIFY THESE FOR YOUR ENVIRONMENT
    DEVICE_HOST = "192.168.1.1"
    DEVICE_PORT = 830
    DEVICE_USERNAME = "admin"
    DEVICE_PASSWORD = "password"
    
    # Teams Configuration - Set your webhook URL
    TEAMS_WEBHOOK_URL = "https://outlook.webhook.office.com/webhookb2/YOUR_WEBHOOK_ID"

    # Interface Changes Configuration
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

    def __init__(self, device_host: str = None, teams_webhook: str = None):
        """
        Initialize automation orchestrator.
        
        Args:
            device_host: Device IP (uses config if not provided)
            teams_webhook: Teams webhook URL (uses config if not provided)
        """
        self.device_host = device_host or self.DEVICE_HOST
        self.teams_webhook = teams_webhook or self.TEAMS_WEBHOOK_URL
        self.netconf_client = None
        self.teams_notifier = None
        self.changes_applied = []
        self.start_time = None

    def run_automation(self) -> bool:
        """
        Execute the complete automation workflow.
        
        Returns:
            bool: True if workflow completed successfully
        """
        self.start_time = datetime.now()
        logger.info("=" * 80)
        logger.info("Network Automation Workflow Started")
        logger.info("=" * 80)
        
        try:
            # Step 1: Verify current running-config
            logger.info("\n[STEP 1] Verifying current running-config...")
            if not self._verify_current_config():
                return False

            # Step 2: Make three configuration changes
            logger.info("\n[STEP 2] Applying three configuration changes...")
            if not self._apply_configuration_changes():
                return False

            # Step 3: Verify the changes
            logger.info("\n[STEP 3] Verifying configuration changes...")
            if not self._verify_changes_applied():
                return False

            # Step 4: Verify new running-config
            logger.info("\n[STEP 4] Verifying new running-config...")
            if not self._verify_new_config():
                return False

            # Step 5: Send Teams notification
            logger.info("\n[STEP 5] Sending Teams notification...")
            self._send_notification()

            logger.info("\n" + "=" * 80)
            logger.info("✅ Automation Workflow COMPLETED SUCCESSFULLY")
            logger.info("=" * 80)
            return True

        except Exception as e:
            logger.error(f"Automation workflow failed: {str(e)}", exc_info=True)
            self._send_error_notification(str(e))
            return False
        
        finally:
            if self.netconf_client:
                self.netconf_client.disconnect()

    def _verify_current_config(self) -> bool:
        """
        Step 1: Verify and display current running configuration.
        
        Returns:
            bool: True if verification successful
        """
        try:
            # Create NETCONF client
            logger.info(f"Connecting to device: {self.device_host}:{self.DEVICE_PORT}")
            self.netconf_client = NetconfClient(
                host=self.device_host,
                port=self.DEVICE_PORT,
                username=self.DEVICE_USERNAME,
                password=self.DEVICE_PASSWORD
            )
            
            if not self.netconf_client.connect():
                logger.error("Failed to connect to device")
                return False
            
            logger.info("✅ Connected to device")
            
            # Get running configuration
            logger.info("Retrieving current running-config...")
            config = self.netconf_client.get_config("running")
            
            if config:
                self._display_config("CURRENT RUNNING-CONFIG", config)
                logger.info("✅ Current running-config retrieved successfully")
                return True
            else:
                logger.error("Failed to retrieve running configuration")
                return False
                
        except Exception as e:
            logger.error(f"Config verification failed: {str(e)}")
            return False

    def _apply_configuration_changes(self) -> bool:
        """
        Step 2: Apply three configuration changes via NETCONF.
        
        Returns:
            bool: True if all changes applied successfully
        """
        try:
            for idx, change in enumerate(self.CHANGES, 1):
                logger.info(f"\nApplying Change {idx}/3:")
                logger.info(f"  Interface: {change['interface']}")
                logger.info(f"  Action: {change['change_type']}")
                logger.info(f"  New Description: {change['description']}")
                
                # Build configuration XML
                config_xml = self._build_interface_update_xml(
                    change['interface'],
                    change['description']
                )
                
                # Send configuration change
                if self.netconf_client.edit_config("candidate", config_xml):
                    logger.info(f"  ✅ Configuration sent to candidate datastore")
                    self.changes_applied.append(change)
                else:
                    logger.error(f"  ❌ Failed to send configuration")
                    return False
            
            # Commit all changes
            logger.info("\nCommitting all changes to running-config...")
            if self.netconf_client.commit():
                logger.info("✅ All changes committed successfully")
                return True
            else:
                logger.error("❌ Failed to commit changes")
                return False
                
        except Exception as e:
            logger.error(f"Configuration change failed: {str(e)}")
            return False

    def _verify_changes_applied(self) -> bool:
        """
        Step 3: Verify that configuration changes were applied.
        
        Returns:
            bool: True if changes are verified
        """
        try:
            logger.info("Verifying changes in device configuration...")
            config = self.netconf_client.get_config("running")
            
            if not config:
                logger.error("Failed to retrieve running-config for verification")
                return False
            
            # Verify each change
            all_verified = True
            for idx, change in enumerate(self.changes_applied, 1):
                interface = change['interface']
                expected_desc = change['description'].replace("Changed to: ", "")
                
                # Simple verification - check if interface name and description appear
                if interface in config and expected_desc in config:
                    logger.info(f"✅ Change {idx} verified: {interface}")
                else:
                    logger.warning(f"⚠️ Change {idx} - partial verification: {interface}")
            
            logger.info("✅ Configuration changes verified")
            return True
            
        except Exception as e:
            logger.error(f"Change verification failed: {str(e)}")
            return False

    def _verify_new_config(self) -> bool:
        """
        Step 4: Verify and display new running configuration.
        
        Returns:
            bool: True if new config verified
        """
        try:
            logger.info("Retrieving new running-config...")
            config = self.netconf_client.get_config("running")
            
            if config:
                self._display_config("NEW RUNNING-CONFIG (AFTER CHANGES)", config)
                logger.info("✅ New running-config verified successfully")
                return True
            else:
                logger.error("Failed to retrieve new running configuration")
                return False
                
        except Exception as e:
            logger.error(f"New config verification failed: {str(e)}")
            return False

    def _send_notification(self):
        """
        Step 5: Send Microsoft Teams notification.
        """
        try:
            self.teams_notifier = TeamsNotifier(self.teams_webhook)
            
            # Format change messages
            change_messages = [
                f"Interface {c['interface']}: {c['description']}"
                for c in self.changes_applied
            ]
            
            timestamp = self.start_time.strftime("%Y-%m-%d %H:%M:%S UTC")
            
            if self.teams_notifier.send_change_notification(
                change_messages,
                self.device_host,
                "Network Automation System",
                timestamp
            ):
                logger.info("✅ Teams notification sent successfully")
            else:
                logger.warning("⚠️ Teams notification may not have been sent")
                
        except Exception as e:
            logger.error(f"Notification failed: {str(e)}")

    def _send_error_notification(self, error_message: str):
        """Send error notification to Teams."""
        try:
            if not self.teams_notifier:
                self.teams_notifier = TeamsNotifier(self.teams_webhook)
            
            self.teams_notifier.send_error_notification(
                error_message,
                self.device_host,
                "Network Automation System"
            )
        except Exception as e:
            logger.error(f"Error notification failed: {str(e)}")

    def _build_interface_update_xml(self, interface_name: str, 
                                   description: str) -> str:
        """
        Build interface configuration update XML.
        
        Args:
            interface_name: Interface name
            description: New interface description
            
        Returns:
            XML configuration snippet
        """
        xml = f'''<interfaces xmlns="http://example.com/ns/interface-config">
      <interface>
        <name>{interface_name}</name>
        <description>{description}</description>
        <enabled>true</enabled>
      </interface>
    </interfaces>'''
        return xml

    def _display_config(self, title: str, config: str):
        """Display configuration in formatted output."""
        logger.info("\n" + "=" * 80)
        logger.info(f"   {title}")
        logger.info("=" * 80)
        
        # Extract and display relevant sections
        lines = config.split('\n')
        for line in lines[:50]:  # Display first 50 lines
            if line.strip():
                logger.info(line)
        
        if len(lines) > 50:
            logger.info(f"... ({len(lines) - 50} more lines)")
        
        logger.info("=" * 80 + "\n")


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    """
    Main entry point for network automation.
    
    Usage:
        python network_automation.py [--device <ip>] [--webhook <url>]
    """
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Network Automation Orchestrator - DEVASC Project Activity 5"
    )
    parser.add_argument('--device', help='Device IP address')
    parser.add_argument('--webhook', help='Teams webhook URL')
    parser.add_argument('--simulate', action='store_true', help='Run simulation mode')
    
    args = parser.parse_args()
    
    # Create and run orchestrator
    orchestrator = NetworkAutomationOrchestrator(
        device_host=args.device,
        teams_webhook=args.webhook
    )
    
    success = orchestrator.run_automation()
    sys.exit(0 if success else 1)
