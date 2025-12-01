"""
Microsoft Teams Notification Module

Sends notifications to Microsoft Teams channels to inform L1 and L2
Support Engineers of network configuration changes.
"""

import requests
import json
import logging
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class TeamsNotifier:
    """
    Microsoft Teams Webhook Integration
    
    Sends rich notifications to Teams channels about network configuration changes.
    """

    def __init__(self, webhook_url: str):
        """
        Initialize Teams notifier.
        
        Args:
            webhook_url: Incoming Webhook URL from Teams channel
        """
        self.webhook_url = webhook_url

    def send_change_notification(self, changes: list, device_ip: str,
                                engineer_name: str, timestamp: str = None) -> bool:
        """
        Send configuration change notification to Teams.
        
        Args:
            changes: List of configuration changes made
            device_ip: IP address of modified device
            engineer_name: Name of engineer who made changes
            timestamp: Change timestamp
            
        Returns:
            bool: True if notification sent successfully
        """
        if not timestamp:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")

        # Build adaptiveCard for Teams
        card = {
            "@type": "MessageCard",
            "@context": "https://schema.org/extensions",
            "summary": f"Network Configuration Change - {device_ip}",
            "themeColor": "0078D4",
            "title": "🔧 Network Configuration Change Notification",
            "sections": [
                {
                    "activityTitle": f"Device: {device_ip}",
                    "activitySubtitle": f"Changed by: {engineer_name}",
                    "facts": [
                        {
                            "name": "Timestamp:",
                            "value": timestamp
                        },
                        {
                            "name": "Change Type:",
                            "value": "Interface Configuration Update"
                        },
                        {
                            "name": "Status:",
                            "value": "✅ Successfully Committed"
                        }
                    ],
                    "markdown": True
                },
                {
                    "activityTitle": "Changes Applied:",
                    "text": self._format_changes(changes)
                },
                {
                    "activityTitle": "Details:",
                    "facts": [
                        {
                            "name": "Automation System:",
                            "value": "Group Saisys Network Automation"
                        },
                        {
                            "name": "Protocol:",
                            "value": "NETCONF (RFC 6241)"
                        },
                        {
                            "name": "Data Model:",
                            "value": "YANG (RFC 7950)"
                        }
                    ]
                }
            ],
            "potentialAction": [
                {
                    "@type": "OpenUri",
                    "name": "View Automation Logs",
                    "targets": [
                        {
                            "os": "default",
                            "uri": "https://example.com/automation/logs"
                        }
                    ]
                }
            ]
        }

        try:
            response = requests.post(
                self.webhook_url,
                json=card,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info("Teams notification sent successfully")
                return True
            else:
                logger.error(f"Teams notification failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending Teams notification: {str(e)}")
            return False

    def _format_changes(self, changes: list) -> str:
        """Format changes for Teams display."""
        formatted = "```\n"
        for i, change in enumerate(changes, 1):
            formatted += f"{i}. {change}\n"
        formatted += "```"
        return formatted

    def send_error_notification(self, error_message: str, device_ip: str,
                               engineer_name: str) -> bool:
        """
        Send error notification to Teams.
        
        Args:
            error_message: Description of the error
            device_ip: IP address of target device
            engineer_name: Name of engineer
            
        Returns:
            bool: True if notification sent
        """
        card = {
            "@type": "MessageCard",
            "@context": "https://schema.org/extensions",
            "summary": f"Network Automation Error - {device_ip}",
            "themeColor": "FF0000",
            "title": "❌ Network Automation Error",
            "sections": [
                {
                    "activityTitle": f"Device: {device_ip}",
                    "activitySubtitle": f"Attempted by: {engineer_name}",
                    "facts": [
                        {
                            "name": "Timestamp:",
                            "value": datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
                        },
                        {
                            "name": "Status:",
                            "value": "❌ Failed"
                        }
                    ]
                },
                {
                    "activityTitle": "Error Details:",
                    "text": f"```\n{error_message}\n```"
                }
            ]
        }

        try:
            response = requests.post(
                self.webhook_url,
                json=card,
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Error sending error notification: {str(e)}")
            return False
