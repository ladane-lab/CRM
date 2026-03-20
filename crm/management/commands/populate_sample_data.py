from django.core.management.base import BaseCommand
from crm.models import Account, Contact, Lead, Opportunity, Task, IntegrationConfig
from django.contrib.auth import get_user_model
import random
from datetime import timedelta
from django.utils import timezone

User = get_user_model()

class Command(BaseCommand):
    help = 'Populates the database with sample CRM data including integrations and tasks'

    def handle(self, *args, **kwargs):
        self.stdout.write('Generating sample data...')

        # Ensure we have at least one user to assign things to
        user = User.objects.first()
        if not user:
            user = User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
            user.role = 'admin'
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Created default admin user {user.username}'))
        else:
            user.role = 'admin'
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Updated role for user {user.username} to admin'))

        # 0. Create Integration Configs
        for service, label in IntegrationConfig.SERVICE_CHOICES:
            config, created = IntegrationConfig.objects.get_or_create(service=service)
            config.is_active = True
            if service == 'slack':
                config.webhook_url = 'https://example.com/placeholder-webhook'
            config.save()
        self.stdout.write(self.style.SUCCESS('Configured sample Integrations'))

        # Cleanup existing data to avoid MultipleObjectsReturned
        self.stdout.write('Cleaning up old sample data...')
        Opportunity.objects.all().delete()
        Task.objects.all().delete()
        Contact.objects.all().delete()
        Lead.objects.all().delete()
        Account.objects.all().delete()

        # 1. Create Accounts
        accounts_data = [
            {'name': 'Stark Industries', 'industry': 'Technology', 'website': 'https://stark.com'},
            {'name': 'Wayne Enterprises', 'industry': 'Finance', 'website': 'https://wayne.com'},
            {'name': 'Oscorp', 'industry': 'Healthcare', 'website': 'https://oscorp.com'},
            {'name': 'Daily Bugle', 'industry': 'Media', 'website': 'https://dailybugle.com'},
            {'name': 'Pym Technologies', 'industry': 'Science', 'website': 'https://pym.com'},
            {'name': 'Oscorp Europe', 'industry': 'Healthcare', 'website': 'https://oscorp.eu'},
            {'name': 'Rand Enterprises', 'industry': 'Finance', 'website': 'https://rand.com'},
            {'name': 'Roxxon Energy', 'industry': 'Energy', 'website': 'https://roxxon.com'},
        ]
        
        accounts_map = {}
        for data in accounts_data:
            account, created = Account.objects.get_or_create(name=data['name'], defaults=data)
            accounts_map[data['name']] = account
        self.stdout.write(self.style.SUCCESS(f'Processed {len(accounts_data)} Accounts'))

        # 2. Create Contacts
        contacts_data = [
            {'account_name': 'Stark Industries', 'first_name': 'Tony', 'last_name': 'Stark', 'email': 'tony@stark.com'},
            {'account_name': 'Stark Industries', 'first_name': 'Pepper', 'last_name': 'Potts', 'email': 'pepper@stark.com'},
            {'account_name': 'Wayne Enterprises', 'first_name': 'Bruce', 'last_name': 'Wayne', 'email': 'bruce@wayne.com'},
            {'account_name': 'Oscorp', 'first_name': 'Norman', 'last_name': 'Osborn', 'email': 'norman@oscorp.com'},
            {'account_name': 'Daily Bugle', 'first_name': 'J. Jonah', 'last_name': 'Jameson', 'email': 'jjj@dailybugle.com'},
            {'account_name': 'Pym Technologies', 'first_name': 'Hank', 'last_name': 'Pym', 'email': 'hank@pym.com'},
            {'account_name': 'Rand Enterprises', 'first_name': 'Danny', 'last_name': 'Rand', 'email': 'ironfist@rand.com'},
        ]

        contacts_map = {}
        for data in contacts_data:
            acc_name = data.pop('account_name')
            data['account'] = accounts_map[acc_name]
            contact, created = Contact.objects.get_or_create(email=data['email'], defaults=data)
            contacts_map[f"{data['first_name']} {data['last_name']}"] = contact
        self.stdout.write(self.style.SUCCESS(f'Processed {len(contacts_data)} Contacts'))

        # 3. Create Leads
        leads_data = [
            {'first_name': 'Peter', 'last_name': 'Parker', 'email': 'peter@spidey.com', 'status': 'new'},
            {'first_name': 'Clark', 'last_name': 'Kent', 'email': 'clark@dailyplanet.com', 'status': 'contacted'},
            {'first_name': 'Diana', 'last_name': 'Prince', 'email': 'diana@themyscira.gov', 'status': 'qualified'},
            {'first_name': 'Barry', 'last_name': 'Allen', 'email': 'barry@ccpd.gov', 'status': 'new'},
            {'first_name': 'Arthur', 'last_name': 'Curry', 'email': 'arthur@atlantis.gov', 'status': 'lost'},
            {'first_name': 'Natasha', 'last_name': 'Romanoff', 'email': 'blackwidow@shield.gov', 'status': 'qualified'},
            {'first_name': 'Steve', 'last_name': 'Rogers', 'email': 'cap@avengers.com', 'status': 'contacted'},
        ]

        for data in leads_data:
            lead, created = Lead.objects.get_or_create(email=data['email'], defaults={**data, 'assigned_to': user})
            if created or lead:
                if random.random() > 0.4:
                    lead.mailchimp_synced = True
                    lead.mailchimp_subscriber_id = f"sub_{random.randint(1000, 9999)}"
                    lead.save()
        self.stdout.write(self.style.SUCCESS(f'Processed Leads'))

        # 4. Create Opportunities
        opportunities_data = [
            {'name': 'Arc Reactor Upgrade', 'account_name': 'Stark Industries', 'contact_name': 'Tony Stark', 'amount': 150000.00, 'stage': 'won'},
            {'name': 'Stark Tower Security', 'account_name': 'Stark Industries', 'contact_name': 'Pepper Potts', 'amount': 75000.00, 'stage': 'negotiation'},
            {'name': 'Satellites Contract', 'account_name': 'Wayne Enterprises', 'contact_name': 'Bruce Wayne', 'amount': 2500000.00, 'stage': 'proposal'},
            {'name': 'Glider Tech Demo', 'account_name': 'Oscorp', 'contact_name': 'Norman Osborn', 'amount': 45000.00, 'stage': 'lost'},
            {'name': 'Exclusive Interview Rights', 'account_name': 'Daily Bugle', 'contact_name': 'J. Jonah Jameson', 'amount': 10000.00, 'stage': 'won'},
            {'name': 'Quantum Realm Portal', 'account_name': 'Pym Technologies', 'contact_name': 'Hank Pym', 'amount': 2000000.00, 'stage': 'prospecting'},
            {'name': 'K-Business Expansion', 'account_name': 'Rand Enterprises', 'contact_name': 'Danny Rand', 'amount': 500000.00, 'stage': 'negotiation'},
        ]

        task_titles = ['Initial Call', 'Requirements Gathering', 'Price Calculation', 'Legal Review', 'Contract Signing', 'Follow-up Email', 'Product Demo']

        for data in opportunities_data:
            acc_name = data.pop('account_name')
            con_name = data.pop('contact_name')
            data['account'] = accounts_map[acc_name]
            data['contact'] = contacts_map[con_name]
            
            opp, created = Opportunity.objects.get_or_create(name=data['name'], defaults={**data, 'assigned_to': user})
            
            if created:
                opp.expected_close_date = timezone.now().date() + timedelta(days=random.randint(5, 60))
                opp.save()
                
                # Create sample tasks
                for title in random.sample(task_titles, k=random.randint(2, 5)):
                    Task.objects.create(
                        opportunity=opp,
                        title=title,
                        status=random.choice(['todo', 'in_progress', 'done']),
                        assigned_to=user,
                        due_date=timezone.now().date() + timedelta(days=random.randint(-5, 15))
                    )
            
            # Update info if already exists
            if not created:
                opp.stage = data['stage']
                opp.amount = data['amount']
                opp.save()

            # Add dummy document info
            if opp.stage == 'won':
                opp.docusign_status = 'completed'
                opp.save()
            elif opp.stage == 'negotiation':
                opp.docusign_status = 'sent'
                opp.save()

        self.stdout.write(self.style.SUCCESS(f'Processed Opportunities with Tasks'))
        self.stdout.write(self.style.SUCCESS('Sample data generation complete!'))
