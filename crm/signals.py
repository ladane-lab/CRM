from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Opportunity, Lead, Account, Contact
from .utils import send_slack_message, send_integration_email

@receiver(post_save, sender=Lead)
def lead_qualified(sender, instance, created, **kwargs):
    # Check if the lead is now qualified
    if instance.status == 'qualified':
        # 1. Create an Account (Company)
        account, acct_created = Account.objects.get_or_create(
            name=f"{instance.last_name} Corp", # Default name
        )
        
        # 2. Create a Contact (Person)
        contact, cont_created = Contact.objects.get_or_create(
            email=instance.email,
            defaults={
                'first_name': instance.first_name,
                'last_name': instance.last_name,
                'phone': instance.phone,
                'account': account
            }
        )

        # 3. Create an Opportunity
        if not Opportunity.objects.filter(contact=contact, account=account).exists():
            Opportunity.objects.create(
                name=f"New Opportunity - {account.name}",
                account=account,
                contact=contact,
                assigned_to=instance.assigned_to,
                stage='prospecting',
                amount=0 # Initial amount
            )

@receiver(post_save, sender=Opportunity)
def opportunity_stage_changed(sender, instance, created, **kwargs):
    # Check if the opportunity was just won
    if instance.stage == 'won':
        message = f"🎉 Deal Closed! Opportunity '{instance.name}' for {instance.account.name if instance.account else 'None'} has been WON! Amount: ₹{instance.amount}"
        
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
