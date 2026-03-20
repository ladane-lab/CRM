from django.core.management.base import BaseCommand
from crm.models import Account, Contact, Lead, Opportunity, Task, IntegrationConfig
from django.contrib.auth import get_user_model
import random
from datetime import timedelta
from django.utils import timezone

User = get_user_model()

class Command(BaseCommand):
    help = 'Populates the database with Indian themed sample CRM data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Generating Indian sample data...')

        user = User.objects.first()
        if not user:
            admin_password = os.environ.get('DJANGO_ADMIN_PASSWORD', 'admin123')
            user = User.objects.create_superuser('admin', 'admin@example.com', admin_password)
            user.role = 'admin'
            user.save()
            if admin_password == 'admin123':
                self.stdout.write(self.style.WARNING('Created default admin user with fallback password "admin123". Please change it!'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Created default admin user {user.username}'))
        else:
            user.role = 'admin'
            user.save()

        # Cleanup existing data
        self.stdout.write('Cleaning up old sample data...')
        Opportunity.objects.all().delete()
        Task.objects.all().delete()
        Contact.objects.all().delete()
        Lead.objects.all().delete()
        Account.objects.all().delete()

        # 1. Create Accounts
        accounts_data = [
            {'name': 'Reliance Industries', 'industry': 'Energy/Telecom', 'website': 'https://reliance.com'},
            {'name': 'Tata Consultancy Services', 'industry': 'Technology', 'website': 'https://tcs.com'},
            {'name': 'HDFC Bank', 'industry': 'Finance', 'website': 'https://hdfcbank.com'},
            {'name': 'Infosys', 'industry': 'Technology', 'website': 'https://infosys.com'},
            {'name': 'Mahindra Group', 'industry': 'Automotive', 'website': 'https://mahindra.com'},
            {'name': 'Bharti Airtel', 'industry': 'Telecommunications', 'website': 'https://airtel.in'},
            {'name': 'Adani Enterprises', 'industry': 'Infrastructure', 'website': 'https://adani.com'},
            {'name': 'Wipro', 'industry': 'Technology', 'website': 'https://wipro.com'},
        ]
        
        accounts_map = {}
        for data in accounts_data:
            account, created = Account.objects.get_or_create(name=data['name'], defaults=data)
            accounts_map[data['name']] = account
        self.stdout.write(self.style.SUCCESS(f'Processed {len(accounts_data)} Accounts'))

        # 2. Create Contacts
        contacts_data = [
            {'account_name': 'Reliance Industries', 'first_name': 'Rajesh', 'last_name': 'Sharma', 'email': 'rajesh.sharma@reliance.com'},
            {'account_name': 'Reliance Industries', 'first_name': 'Anita', 'last_name': 'Desai', 'email': 'anita.desai@reliance.com'},
            {'account_name': 'Tata Consultancy Services', 'first_name': 'Vikram', 'last_name': 'Malhotra', 'email': 'v.malhotra@tcs.com'},
            {'account_name': 'HDFC Bank', 'first_name': 'Sunita', 'last_name': 'Gupta', 'email': 'sunita.g@hdfcbank.com'},
            {'account_name': 'Infosys', 'first_name': 'Amit', 'last_name': 'Patel', 'email': 'amit.p@infosys.com'},
            {'account_name': 'Mahindra Group', 'first_name': 'Priya', 'last_name': 'Reddy', 'email': 'priya.r@mahindra.com'},
            {'account_name': 'Bharti Airtel', 'first_name': 'Sanjay', 'last_name': 'Verma', 'email': 'sanjay.v@airtel.in'},
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
            {'first_name': 'Arjun', 'last_name': 'Kapoor', 'email': 'arjun.k@example.in', 'status': 'new'},
            {'first_name': 'Deepika', 'last_name': 'Mehta', 'email': 'deepika.m@example.in', 'status': 'contacted'},
            {'first_name': 'Rohan', 'last_name': 'Joshi', 'email': 'rohan.j@example.in', 'status': 'qualified'},
            {'first_name': 'Ishani', 'last_name': 'Shah', 'email': 'ishani.s@example.in', 'status': 'new'},
            {'first_name': 'Neha', 'last_name': 'Sharma', 'email': 'neha.s@example.in', 'status': 'lost'},
            {'first_name': 'Aarav', 'last_name': 'Singh', 'email': 'aarav.s@example.in', 'status': 'qualified'},
            {'first_name': 'Sanya', 'last_name': 'Iyer', 'email': 'sanya.i@example.in', 'status': 'contacted'},
            {'first_name': 'Rahul', 'last_name': 'Dravid', 'email': 'rahul.d@cricket.in', 'status': 'new'},
            {'first_name': 'Anupam', 'last_name': 'Kher', 'email': 'anupam@movies.in', 'status': 'qualified'},
            {'first_name': 'Kunal', 'last_name': 'Kamra', 'email': 'kunal@comedy.in', 'status': 'lost'},
            {'first_name': 'Zoya', 'last_name': 'Akhtar', 'email': 'zoya@cinema.in', 'status': 'contacted'},
            {'first_name': 'Virat', 'last_name': 'Kohli', 'email': 'virat@captain.in', 'status': 'new'},
            {'first_name': 'Priyanka', 'last_name': 'Chopra', 'email': 'priyanka@global.in', 'status': 'qualified'},
            {'first_name': 'Manish', 'last_name': 'Malhotra', 'email': 'manish@fashion.in', 'status': 'contacted'},
            {'first_name': 'Ratan', 'last_name': 'Tata', 'email': 'ratan@trust.in', 'status': 'qualified'},
        ]

        for data in leads_data:
            Lead.objects.get_or_create(email=data['email'], defaults={**data, 'assigned_to': user})
        self.stdout.write(self.style.SUCCESS(f'Processed Leads'))

        # 4. Create Opportunities
        opportunities_data = [
            {'name': '5G Network Expansion', 'account_name': 'Bharti Airtel', 'contact_name': 'Sanjay Verma', 'amount': 25000000.00, 'stage': 'won'},
            {'name': 'Solar Farm Setup', 'account_name': 'Adani Enterprises', 'industry': 'Energy', 'amount': 15000000.00, 'stage': 'proposal'},
            {'name': 'Digital Banking Portal', 'account_name': 'HDFC Bank', 'contact_name': 'Sunita Gupta', 'amount': 8500000.00, 'stage': 'negotiation'},
            {'name': 'EV Battery R&D', 'account_name': 'Mahindra Group', 'contact_name': 'Priya Reddy', 'amount': 4500000.00, 'stage': 'prospecting'},
            {'name': 'Cloud Migration Services', 'account_name': 'Tata Consultancy Services', 'contact_name': 'Vikram Malhotra', 'amount': 12000000.00, 'stage': 'won'},
            {'name': 'AI Excellence Center', 'account_name': 'Infosys', 'contact_name': 'Amit Patel', 'amount': 9500000.00, 'stage': 'negotiation'},
        ]

        for data in opportunities_data:
            acc_name = data.pop('account_name')
            con_name = data.pop('contact_name', None)
            industry = data.pop('industry', None)
            
            data['account'] = accounts_map[acc_name]
            if con_name:
                data['contact'] = contacts_map[con_name]
            
            opp, created = Opportunity.objects.get_or_create(name=data['name'], defaults={**data, 'assigned_to': user})
            if created:
                opp.expected_close_date = timezone.now().date() + timedelta(days=random.randint(5, 60))
                opp.save()
                
                # Create sample tasks
                titles = ['Initial Discussion', 'Proposal Submission', 'Value Negotiation', 'Contract Review']
                for title in titles:
                    Task.objects.create(
                        opportunity=opp,
                        title=title,
                        status=random.choice(['todo', 'in_progress', 'done']),
                        assigned_to=user,
                        due_date=timezone.now().date() + timedelta(days=random.randint(-5, 15))
                    )

        self.stdout.write(self.style.SUCCESS(f'Processed Opportunities with Indian Context'))
        self.stdout.write(self.style.SUCCESS('Indian Sample data generation complete!'))
