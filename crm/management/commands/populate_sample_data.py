from django.core.management.base import BaseCommand
from crm.models import Account, Contact, Lead, Opportunity
from django.contrib.auth import get_user_model
import random
from datetime import timedelta
from django.utils import timezone

User = get_user_model()

class Command(BaseCommand):
    help = 'Populates the database with sample CRM data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Generating sample data...')

        # Ensure we have at least one user to assign things to
        user = User.objects.first()
        if not user:
            user = User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
            self.stdout.write(self.style.SUCCESS(f'Created default admin user {user.username}'))

        # 1. Create Accounts
        accounts_data = [
            {'name': 'Stark Industries', 'industry': 'Technology', 'website': 'https://stark.com'},
            {'name': 'Wayne Enterprises', 'industry': 'Finance', 'website': 'https://wayne.com'},
            {'name': 'Oscorp', 'industry': 'Healthcare', 'website': 'https://oscorp.com'},
            {'name': 'Daily Bugle', 'industry': 'Media', 'website': 'https://dailybugle.com'},
        ]
        
        accounts = []
        for data in accounts_data:
            account, created = Account.objects.get_or_create(**data)
            accounts.append(account)
        self.stdout.write(self.style.SUCCESS(f'Created {len(accounts)} Accounts'))

        # 2. Create Contacts
        contacts_data = [
            {'account': accounts[0], 'first_name': 'Tony', 'last_name': 'Stark', 'email': 'tony@stark.com'},
            {'account': accounts[0], 'first_name': 'Pepper', 'last_name': 'Potts', 'email': 'pepper@stark.com'},
            {'account': accounts[1], 'first_name': 'Bruce', 'last_name': 'Wayne', 'email': 'bruce@wayne.com'},
            {'account': accounts[2], 'first_name': 'Norman', 'last_name': 'Osborn', 'email': 'norman@oscorp.com'},
            {'account': accounts[3], 'first_name': 'J. Jonah', 'last_name': 'Jameson', 'email': 'jjj@dailybugle.com'},
        ]

        contacts = []
        for data in contacts_data:
            contact, created = Contact.objects.get_or_create(**data)
            contacts.append(contact)
        self.stdout.write(self.style.SUCCESS(f'Created {len(contacts)} Contacts'))

        # 3. Create Leads
        lead_statuses = ['new', 'contacted', 'qualified', 'lost']
        leads_data = [
            {'first_name': 'Peter', 'last_name': 'Parker', 'email': 'peter@spidey.com', 'status': random.choice(lead_statuses)},
            {'first_name': 'Clark', 'last_name': 'Kent', 'email': 'clark@dailyplanet.com', 'status': random.choice(lead_statuses)},
            {'first_name': 'Diana', 'last_name': 'Prince', 'email': 'diana@themyscira.gov', 'status': random.choice(lead_statuses)},
            {'first_name': 'Barry', 'last_name': 'Allen', 'email': 'barry@ccpd.gov', 'status': random.choice(lead_statuses)},
            {'first_name': 'Arthur', 'last_name': 'Curry', 'email': 'arthur@atlantis.gov', 'status': random.choice(lead_statuses)},
        ]

        for data in leads_data:
            Lead.objects.get_or_create(**data, assigned_to=user)
        self.stdout.write(self.style.SUCCESS(f'Created {len(leads_data)} Leads'))

        # 4. Create Opportunities
        stages = ['prospecting', 'proposal', 'negotiation', 'won', 'lost']
        opportunities_data = [
            {'name': 'Arc Reactor Upgrade', 'account': accounts[0], 'contact': contacts[0], 'amount': 150000.00, 'stage': random.choice(stages)},
            {'name': 'Stark Tower Security', 'account': accounts[0], 'contact': contacts[1], 'amount': 75000.00, 'stage': random.choice(stages)},
            {'name': 'Satellites Contract', 'account': accounts[1], 'contact': contacts[2], 'amount': 2500000.00, 'stage': random.choice(stages)},
            {'name': 'Glider Tech Demo', 'account': accounts[2], 'contact': contacts[3], 'amount': 45000.00, 'stage': random.choice(stages)},
            {'name': 'Exclusive Interview Rights', 'account': accounts[3], 'contact': contacts[4], 'amount': 10000.00, 'stage': random.choice(stages)},
        ]

        for i, data in enumerate(opportunities_data):
            # assign some random dates within the next 60 days
            close_date = timezone.now().date() + timedelta(days=random.randint(5, 60))
            Opportunity.objects.get_or_create(**data, assigned_to=user, expected_close_date=close_date)
            
        self.stdout.write(self.style.SUCCESS(f'Created {len(opportunities_data)} Opportunities'))
        self.stdout.write(self.style.SUCCESS('Sample data generation complete!'))
