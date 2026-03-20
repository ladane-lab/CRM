from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('agent', 'Sales Agent'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='agent')

class Account(models.Model):
    name = models.CharField(max_length=255)
    industry = models.CharField(max_length=100, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Contact(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='contacts', null=True, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Lead(models.Model):
    STATUS_CHOICES = (
        ('new', 'New'),
        ('contacted', 'Contacted'),
        ('qualified', 'Qualified'),
        ('lost', 'Lost'),
    )
    SOURCE_CHOICES = (
        ('website', 'Website'),
        ('referral', 'Referral'),
        ('cold_call', 'Cold Call'),
        ('other', 'Other'),
    )
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='leads')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='website')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Integration Fields
    mailchimp_synced = models.BooleanField(default=False)
    mailchimp_subscriber_id = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Opportunity(models.Model):
    STAGE_CHOICES = (
        ('prospecting', 'Prospecting'),
        ('proposal', 'Proposal/Price Quote'),
        ('negotiation', 'Negotiation/Review'),
        ('won', 'Closed Won'),
        ('lost', 'Closed Lost'),
    )
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='opportunities', null=True, blank=True)
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name='opportunities', null=True, blank=True)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='opportunities')
    name = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    stage = models.CharField(max_length=20, choices=STAGE_CHOICES, default='prospecting')
    expected_close_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Document Management & Project Sync
    contract_file = models.FileField(upload_to='contracts/', null=True, blank=True)
    docusign_status = models.CharField(max_length=50, default='none')
    external_project_id = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name

class Task(models.Model):
    STATUS_CHOICES = (
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    opportunity = models.ForeignKey(Opportunity, on_delete=models.CASCADE, related_name='tasks')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo')
    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title

class IntegrationConfig(models.Model):
    SERVICE_CHOICES = (
        ('slack', 'Slack'),
        ('mailchimp', 'Mailchimp'),
        ('docusign', 'DocuSign'),
        ('trello', 'Trello'),
    )
    service = models.CharField(max_length=20, choices=SERVICE_CHOICES, unique=True)
    webhook_url = models.URLField(blank=True, null=True)
    api_key = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=False)
    last_sync = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.get_service_display()
