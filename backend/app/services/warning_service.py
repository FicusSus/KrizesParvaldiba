"""
Warning Service

This service handles the creation and delivery of warnings and alerts
to users based on crisis predictions.
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

import structlog

from app.core.config import settings
from app.core.logger import get_logger
from app.models.crisis import Crisis, CrisisSeverity
from app.models.user import User
from app.models.warning import Warning, WarningPriority, WarningStatus, WarningType
from app.services.crisis_predictor import CrisisPredictor

logger = get_logger(__name__)


class WarningService:
    """
    Service for managing and delivering crisis warnings.
    
    Features:
    - Generate warnings based on crisis predictions
    - Send warnings via multiple channels (email, SMS, etc.)
    - Track warning delivery and status
    - Manage user notification preferences
    """
    
    def __init__(self):
        """Initialize the warning service."""
        self.crisis_predictor = CrisisPredictor()
        self.warning_channels = {
            WarningType.EMAIL: EmailWarningChannel(),
            WarningType.SMS: SMSWarningChannel(),
            WarningType.PUSH: PushWarningChannel(),
            WarningType.WEBHOOK: WebhookWarningChannel(),
            WarningType.IN_APP: InAppWarningChannel(),
        }
    
    async def generate_warnings_for_crisis(
        self,
        crisis: Crisis,
        users: List[User],
        config: Optional[Dict[str, Any]] = None
    ) -> List[Warning]:
        """
        Generate warnings for a crisis event.
        
        Args:
            crisis: The crisis event to generate warnings for
            users: List of users to notify
            config: Warning generation configuration
            
        Returns:
            List of generated Warning objects
        """
        logger.info("Generating warnings for crisis", crisis_id=crisis.id)
        
        warnings = []
        
        if config is None:
            config = {}
        
        # Determine warning priority based on crisis severity
        priority = self._map_crisis_severity_to_priority(crisis.severity)
        
        # Determine which users should be notified
        target_users = self._filter_users_for_notification(users, crisis, config)
        
        # Generate warning message
        subject, message = self._generate_crisis_message(crisis)
        
        # Create warnings for each user
        for user in target_users:
            # Determine preferred warning channels for this user
            channels = self._get_user_channels(user, config)
            
            for channel in channels:
                warning = Warning(
                    user_id=user.id,
                    crisis_id=crisis.id,
                    warning_type=channel,
                    priority=priority,
                    subject=subject,
                    message=message,
                    recipient=self._get_recipient_for_channel(user, channel),
                    metadata={
                        "crisis_type": crisis.crisis_type.value,
                        "crisis_severity": crisis.severity.value,
                        "generated_by": "automated",
                        "priority_reason": f"Crisis severity: {crisis.severity.value}",
                    }
                )
                warnings.append(warning)
        
        logger.info("Generated warnings", count=len(warnings), crisis_id=crisis.id)
        return warnings
    
    def _map_crisis_severity_to_priority(
        self,
        severity: CrisisSeverity
    ) -> WarningPriority:
        """Map crisis severity to warning priority."""
        severity_priority_map = {
            CrisisSeverity.LOW: WarningPriority.LOW,
            CrisisSeverity.MEDIUM: WarningPriority.MEDIUM,
            CrisisSeverity.HIGH: WarningPriority.HIGH,
            CrisisSeverity.CRITICAL: WarningPriority.URGENT,
        }
        return severity_priority_map.get(severity, WarningPriority.MEDIUM)
    
    def _filter_users_for_notification(
        self,
        users: List[User],
        crisis: Crisis,
        config: Dict[str, Any]
    ) -> List[User]:
        """Filter users who should receive notifications for this crisis."""
        target_users = []
        
        for user in users:
            # Always notify admins
            if user.is_admin:
                target_users.append(user)
                continue
            
            # Check user preferences
            preferences = user.preferences or {}
            
            # Check if user wants to receive crisis notifications
            receive_notifications = preferences.get("receive_notifications", True)
            if not receive_notifications:
                continue
            
            # Check if user wants to receive notifications for this crisis type
            crisis_type_prefs = preferences.get("crisis_types", {})
            if crisis_type_prefs:
                crisis_type_key = crisis.crisis_type.value
                if crisis_type_key in crisis_type_prefs:
                    if not crisis_type_prefs[crisis_type_key]:
                        continue
            
            # Check if user wants to receive notifications for this severity level
            severity_prefs = preferences.get("severity_levels", {})
            if severity_prefs:
                severity_key = crisis.severity.value
                if severity_key in severity_prefs:
                    if not severity_prefs[severity_key]:
                        continue
            
            target_users.append(user)
        
        return target_users
    
    def _generate_crisis_message(
        self,
        crisis: Crisis
    ) -> tuple:
        """Generate subject and message for a crisis warning."""
        # Create subject
        subject = f"CRISIS ALERT: {crisis.severity.value.upper()} {crisis.crisis_type.value.upper()}"
        
        if crisis.title:
            subject = f"CRISIS ALERT: {crisis.title}"
        
        # Create message
        message_lines = [
            f"A {crisis.severity.value} severity {crisis.crisis_type.value} crisis has been detected.",
            "",
            f"Title: {crisis.title or 'N/A'}",
            f"Type: {crisis.crisis_type.value}",
            f"Severity: {crisis.severity.value}",
        ]
        
        if crisis.description:
            message_lines.append(f"Description: {crisis.description}")
        
        if crisis.location:
            message_lines.append(f"Location: {crisis.location}")
        
        if crisis.start_date:
            message_lines.append(f"Started: {crisis.start_date.isoformat()}")
        
        if crisis.confidence_score:
            message_lines.append(f"Confidence: {crisis.confidence_score:.2%}")
        
        if crisis.impact_score:
            message_lines.append(f"Impact Score: {crisis.impact_score:.1f}/100")
        
        message_lines.append("")
        message_lines.append("Please take appropriate action immediately.")
        
        message = "\n".join(message_lines)
        
        return subject, message
    
    def _get_user_channels(
        self,
        user: User,
        config: Dict[str, Any]
    ) -> List[WarningType]:
        """Get warning channels for a user."""
        preferences = user.preferences or {}
        
        # Default to all channels
        available_channels = list(self.warning_channels.keys())
        
        # Check user's preferred channels
        preferred_channels = preferences.get("notification_channels", [])
        if preferred_channels:
            available_channels = [
                channel for channel in available_channels 
                if channel.value in preferred_channels
            ]
        
        # Ensure at least one channel
        if not available_channels:
            available_channels = [WarningType.IN_APP]  # Default to in-app
        
        return available_channels
    
    def _get_recipient_for_channel(
        self,
        user: User,
        channel: WarningType
    ) -> Optional[str]:
        """Get recipient address for a specific channel."""
        if channel == WarningType.EMAIL:
            return user.email
        elif channel == WarningType.SMS:
            # In production, this would be the user's phone number
            preferences = user.preferences or {}
            return preferences.get("phone_number")
        elif channel == WarningType.PUSH:
            # Push notification token
            preferences = user.preferences or {}
            return preferences.get("push_token")
        elif channel == WarningType.WEBHOOK:
            # User's webhook URL
            preferences = user.preferences or {}
            return preferences.get("webhook_url")
        else:
            # For in-app notifications, recipient is not needed
            return None
    
    async def send_warning(
        self,
        warning: Warning,
        crisis: Optional[Crisis] = None
    ) -> bool:
        """
        Send a warning via the specified channel.
        
        Args:
            warning: The warning to send
            crisis: Optional crisis object for context
            
        Returns:
            bool: True if warning was sent successfully, False otherwise
        """
        logger.info("Sending warning", warning_id=warning.id, type=warning.warning_type)
        
        try:
            # Get the appropriate channel handler
            channel_handler = self.warning_channels.get(warning.warning_type)
            if channel_handler is None:
                logger.error("No channel handler found", type=warning.warning_type)
                return False
            
            # Prepare data for the channel
            data = {
                "warning": warning,
                "crisis": crisis,
                "subject": warning.subject,
                "message": warning.message,
                "recipient": warning.recipient,
            }
            
            # Send via the channel
            success = await channel_handler.send(data)
            
            if success:
                logger.info("Warning sent successfully", 
                           warning_id=warning.id, 
                           type=warning.warning_type)
                return True
            else:
                logger.warning("Warning delivery failed", 
                              warning_id=warning.id, 
                              type=warning.warning_type)
                return False
                
        except Exception as e:
            logger.error("Warning delivery error", 
                        warning_id=warning.id, 
                        error=str(e))
            return False
    
    async def batch_send_warnings(
        self,
        warnings: List[Warning],
        crises: Optional[List[Crisis]] = None
    ) -> Dict[str, Any]:
        """
        Send multiple warnings as a batch.
        
        Args:
            warnings: List of warnings to send
            crises: Optional list of crises corresponding to warnings
            
        Returns:
            Dict: Summary of sending results
        """
        logger.info("Batch sending warnings", count=len(warnings))
        
        crises_map = {}
        if crises:
            for crisis in crises:
                crises_map[crisis.id] = crisis
        
        results = {
            "total": len(warnings),
            "success": 0,
            "failed": 0,
            "details": [],
        }
        
        # Send warnings concurrently for efficiency
        tasks = []
        for warning in warnings:
            crisis = crises_map.get(warning.crisis_id) if warning.crisis_id else None
            tasks.append(self.send_warning(warning, crisis))
        
        # Run with limited concurrency to avoid overwhelming resources
        for i in range(0, len(tasks), 10):  # Process 10 at a time
            batch = tasks[i:i + 10]
            batch_results = await asyncio.gather(*batch)
            
            for j, success in enumerate(batch_results):
                warning = warnings[i + j]
                details = {
                    "warning_id": warning.id,
                    "type": warning.warning_type.value,
                    "success": success,
                }
                results["details"].append(details)
                
                if success:
                    results["success"] += 1
                else:
                    results["failed"] += 1
        
        logger.info("Batch sending completed", 
                   success=results["success"], 
                   failed=results["failed"])
        
        return results


# Base class for warning channels
class WarningChannel:
    """Base class for warning channels."""
    
    async def send(self, data: Dict[str, Any]) -> bool:
        """Send a warning via this channel."""
        raise NotImplementedError("Subclasses must implement send method")


class EmailWarningChannel(WarningChannel):
    """Email warning channel."""
    
    async def send(self, data: Dict[str, Any]) -> bool:
        """Send a warning via email."""
        logger.info("Sending email warning", 
                   recipient=data.get("recipient"),
                   subject=data.get("subject"))
        
        # In production, this would integrate with an email service
        # For now, we'll simulate the sending
        
        try:
            # Simulate email sending delay
            await asyncio.sleep(0.1)
            
            # Check if email is valid
            recipient = data.get("recipient")
            if not recipient or "@" not in recipient:
                logger.warning("Invalid email recipient", recipient=recipient)
                return False
            
            # Simulate success
            logger.debug("Email sent successfully", recipient=recipient)
            return True
            
        except Exception as e:
            logger.error("Email sending failed", error=str(e))
            return False


class SMSWarningChannel(WarningChannel):
    """SMS warning channel."""
    
    async def send(self, data: Dict[str, Any]) -> bool:
        """Send a warning via SMS."""
        logger.info("Sending SMS warning", 
                   recipient=data.get("recipient"))
        
        # In production, this would integrate with an SMS service like Twilio
        
        try:
            # Simulate SMS sending delay
            await asyncio.sleep(0.2)
            
            # Check if phone number is valid
            recipient = data.get("recipient")
            if not recipient or len(recipient) < 7:  # Basic phone number validation
                logger.warning("Invalid phone recipient", recipient=recipient)
                return False
            
            # Simulate success
            logger.debug("SMS sent successfully", recipient=recipient)
            return True
            
        except Exception as e:
            logger.error("SMS sending failed", error=str(e))
            return False


class PushWarningChannel(WarningChannel):
    """Push notification warning channel."""
    
    async def send(self, data: Dict[str, Any]) -> bool:
        """Send a warning via push notification."""
        logger.info("Sending push warning", 
                   recipient=data.get("recipient"))
        
        # In production, this would integrate with a push notification service
        
        try:
            # Simulate push notification delay
            await asyncio.sleep(0.1)
            
            # Check if push token is valid
            recipient = data.get("recipient")
            if not recipient or len(recipient) < 10:  # Basic token validation
                logger.warning("Invalid push token", recipient=recipient)
                return False
            
            # Simulate success
            logger.debug("Push notification sent successfully", recipient=recipient)
            return True
            
        except Exception as e:
            logger.error("Push notification failed", error=str(e))
            return False


class WebhookWarningChannel(WarningChannel):
    """Webhook warning channel."""
    
    async def send(self, data: Dict[str, Any]) -> bool:
        """Send a warning via webhook."""
        logger.info("Sending webhook warning", 
                   url=data.get("recipient"))
        
        # In production, this would make an HTTP POST request to the webhook URL
        
        try:
            # Simulate webhook delay
            await asyncio.sleep(0.1)
            
            # Check if URL is valid
            recipient = data.get("recipient")
            if not recipient or not (recipient.startswith("http://") or recipient.startswith("https://")):
                logger.warning("Invalid webhook URL", url=recipient)
                return False
            
            # Simulate success
            logger.debug("Webhook sent successfully", url=recipient)
            return True
            
        except Exception as e:
            logger.error("Webhook sending failed", error=str(e))
            return False


class InAppWarningChannel(WarningChannel):
    """In-app warning channel."""
    
    async def send(self, data: Dict[str, Any]) -> bool:
        """Send a warning via in-app notification."""
        logger.info("Sending in-app warning", 
                   user_id=data.get("warning", {}).get("user_id"))
        
        # In-app notifications are typically stored in the database
        # and displayed when the user logs in
        
        try:
            # Simulate in-app notification processing
            await asyncio.sleep(0.05)
            
            # For in-app, we just need to store the notification
            # This is handled by the API, so we always return True
            logger.debug("In-app notification stored successfully")
            return True
            
        except Exception as e:
            logger.error("In-app notification failed", error=str(e))
            return False