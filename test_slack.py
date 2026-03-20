import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from crm.utils import send_slack_message
from crm.models import IntegrationConfig

def test_slack():
    print("Starting Slack Test...")
    try:
        config = IntegrationConfig.objects.get(service='slack')
        print(f"Service: {config.service}")
        print(f"Active: {config.is_active}")
        print(f"URL: {config.webhook_url}")
        
        success = send_slack_message("🤖 Standalone Test Message from CRM Pro")
        if success:
            print("SUCCESS: Slack message sent!")
        else:
            print("FAILED: send_slack_message returned False")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_slack()
