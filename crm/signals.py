from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Opportunity
from .utils import send_slack_message, send_integration_email

@receiver(post_save, sender=Opportunity)
def opportunity_stage_changed(sender, instance, created, **kwargs):
    # Check if the opportunity was just won
    if instance.stage == 'won':
        message = f"🎉 Deal Closed! Opportunity '{instance.name}' for {instance.account.name} has been WON! Amount: ₹{instance.amount}"
        
        # 1. Send Slack Notification
        send_slack_message(message)
        
        # 2. Send Email to Admin/Assigned Agent
        recipients = []
        if instance.assigned_to and instance.assigned_to.email:
            recipients.append(instance.assigned_to.email)
        
        if recipients:
            send_integration_email(
                subject="Opportunity Won!",
                message=message,
                recipient_list=recipients
            )
        
        # 3. Project Sync (Foundation)
        # Create an initial task for the won opportunity
        from .models import Task
        if not Task.objects.filter(opportunity=instance, title="Kickoff Meeting").exists():
            Task.objects.create(
                opportunity=instance,
                title="Kickoff Meeting",
                description="Initial project kickoff for the won opportunity.",
                assigned_to=instance.assigned_to,
                status='todo'
            )
