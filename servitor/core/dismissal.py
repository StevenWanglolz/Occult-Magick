"""Dismissal protocol for servitors"""

import logging
from datetime import datetime
from typing import Optional
from .servitor import Servitor, ServitorStatus
from .storage import Storage


logger = logging.getLogger(__name__)


class DismissalProtocol:
    """Handles proper servitor dismissal"""
    
    def __init__(self, storage: Storage):
        """Initialize dismissal protocol"""
        self.storage = storage
    
    def dismiss_servitor(
        self,
        servitor: Servitor,
        reason: str = "",
        confirm: bool = True
    ) -> bool:
        """
        Dismiss a servitor with proper protocol
        
        Args:
            servitor: Servitor to dismiss
            reason: Reason for dismissal
            confirm: Require confirmation (for safety)
        
        Returns:
            True if dismissed successfully
        """
        if servitor.status == ServitorStatus.DISMISSED:
            logger.warning(f"Servitor {servitor.name} is already dismissed")
            return False
        
        # Perform dismissal ritual
        logger.info(f"Initiating dismissal protocol for {servitor.name}")
        
        # Deactivate first
        servitor.deactivate()
        
        # Add dismissal note
        dismissal_note = f"\n[DISMISSED {datetime.now().isoformat()}]"
        if reason:
            dismissal_note += f" Reason: {reason}"
        servitor.notes += dismissal_note
        
        # Set status to dismissed
        servitor.status = ServitorStatus.DISMISSED
        
        # Archive servitor
        success = self.storage.archive_servitor(servitor)
        
        if success:
            logger.info(f"Servitor {servitor.name} has been dismissed and archived")
        else:
            logger.error(f"Failed to archive servitor {servitor.name}")
        
        return success
    
    def create_dismissal_ritual(self, servitor: Servitor) -> str:
        """
        Create a dismissal ritual text
        
        Args:
            servitor: Servitor to create ritual for
        
        Returns:
            Ritual text
        """
        ritual = f"""
=== DISMISSAL RITUAL FOR {servitor.name.upper()} ===

Servitor Name: {servitor.name}
Purpose: {servitor.purpose}
Created: {servitor.creation_date.strftime('%Y-%m-%d %H:%M:%S')}
Final Charge Level: {servitor.charge_level:.1f}%

RITUAL:

I hereby release {servitor.name} from its purpose.
Its task is complete, its energy returned to the void.
{servitor.name}, you are dismissed.
Your form dissolves, your purpose fulfilled.
Return to the source from which you came.

So it is done.

=== END OF RITUAL ===
"""
        return ritual
    
    def perform_dismissal_ritual(self, servitor: Servitor) -> bool:
        """
        Perform the dismissal ritual and dismiss servitor
        
        Args:
            servitor: Servitor to dismiss
        
        Returns:
            True if dismissed successfully
        """
        ritual_text = self.create_dismissal_ritual(servitor)
        print(ritual_text)
        
        # Wait for user confirmation
        response = input("\nDo you wish to proceed with dismissal? (yes/no): ")
        
        if response.lower() in ['yes', 'y']:
            return self.dismiss_servitor(servitor, reason="Ritual dismissal", confirm=False)
        else:
            print("Dismissal cancelled.")
            return False

