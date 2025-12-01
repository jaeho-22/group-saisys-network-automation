"""
Group Saisys Network Automation System
DEVASC Project Activity 5 - Network Programmability and Automation

A comprehensive network automation solution using NETCONF and YANG.
"""

__version__ = "1.0.0"
__author__ = "Group Saisys DEVASC Team"
__license__ = "MIT"

from .netconf_client.netconf_client import NetconfClient, NetconfXmlBuilder
from .netconf_client.teams_notifier import TeamsNotifier

__all__ = [
    'NetconfClient',
    'NetconfXmlBuilder',
    'TeamsNotifier'
]
