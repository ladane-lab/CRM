from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Account, Contact, Lead, Opportunity

User = get_user_model()

class CRMModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testsales', 
            password='password123',
            role='sales'
        )
        self.account = Account.objects.create(
            name='Test Corp',
            industry='Technology',
            website='https://testcorp.com'
        )
        self.contact = Contact.objects.create(
            account=self.account,
            first_name='John',
            last_name='Doe',
            email='john@testcorp.com'
        )

    def test_account_creation(self):
        self.assertEqual(Account.objects.count(), 1)
        self.assertEqual(self.account.name, 'Test Corp')

    def test_contact_creation(self):
        self.assertEqual(Contact.objects.count(), 1)
        self.assertEqual(self.contact.account, self.account)

    def test_lead_creation(self):
        lead = Lead.objects.create(
            first_name='Jane',
            last_name='Smith',
            email='jane@example.com',
            assigned_to=self.user,
            status='new'
        )
        self.assertEqual(Lead.objects.count(), 1)
        self.assertEqual(lead.assigned_to, self.user)

    def test_opportunity_creation(self):
        opp = Opportunity.objects.create(
            name='Big Deal',
            amount=50000.00,
            stage='prospecting',
            account=self.account,
            assigned_to=self.user
        )
        self.assertEqual(Opportunity.objects.count(), 1)
        self.assertEqual(opp.amount, 50000.00)


class CRMViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testsales', 
            password='password123',
            role='sales'
        )
        self.client.login(username='testsales', password='password123')

    def test_dashboard_view(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'crm/dashboard.html')

    def test_account_list_view(self):
        response = self.client.get(reverse('account-list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'crm/account_list.html')
        
    def test_lead_list_view(self):
        response = self.client.get(reverse('lead-list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'crm/lead_list.html')

class CRMWorkflowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testadmin', password='password123', role='admin')

    def test_lead_to_opportunity_flow(self):
        # 1. Create a lead
        lead = Lead.objects.create(
            first_name='Peter',
            last_name='Parker',
            email='peter@dailybugle.com',
            status='new',
            assigned_to=self.user
        )
        
        # 2. Qualify the lead
        lead.status = 'qualified'
        lead.save()
        
        # 3. Verify Account creation
        account = Account.objects.get(name='Parker Corp')
        self.assertIsNotNone(account)
        
        # 4. Verify Contact creation
        contact = Contact.objects.get(email='peter@dailybugle.com')
        self.assertEqual(contact.account, account)
        
        # 5. Verify Opportunity creation
        opp = Opportunity.objects.get(contact=contact, account=account)
        self.assertEqual(opp.stage, 'prospecting')
        
        # 6. Close the Opportunity (Won)
        opp.stage = 'won'
        opp.save()
        
        # 7. Verify Task creation (Signal)
        task = Task.objects.get(opportunity=opp, title="Kickoff Meeting")
        self.assertIsNotNone(task)
