import requests
import json
import logging
from django.core.mail import send_mail
from django.conf import settings
from .models import IntegrationConfig

logger = logging.getLogger(__name__)

def send_slack_message(message):
    """Sends a message to the configured Slack webhook."""
    try:
        config = IntegrationConfig.objects.get(service='slack', is_active=True)
        if config.webhook_url:
            response = requests.post(
                config.webhook_url,
                json={"text": message},
                timeout=5
            )
            response.raise_for_status()
            return True
    except Exception as e:
        logger.warning(f"Slack integration skipped or failed: {e}")
    return False

def export_opportunity_to_json(opportunity):
    """Generates a JSON representation of an opportunity for external sync."""
    data = {
        "id": opportunity.id,
        "name": opportunity.name,
        "description": f"Opportunity for {opportunity.account.name if opportunity.account else 'None'}",
        "amount": float(opportunity.amount) if opportunity.amount else 0,
        "stage": opportunity.get_stage_display(),
        "tasks": [
            {"title": t.title, "status": t.get_status_display()}
            for t in opportunity.tasks.all()
        ]
    }
    return json.dumps(data, indent=4)

def send_integration_email(subject, message, recipient_list):
    """Sends an email using Django's core mail system."""
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            recipient_list,
            fail_silently=False,
        )
        return True
    except Exception as e:
        logger.error(f"Error sending integration email: {e}")
    return False
