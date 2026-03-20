from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .forms import SignUpForm, LeadForm, AccountForm, ContactForm, OpportunityForm, IntegrationConfigForm
from .models import Lead, Account, Contact, Opportunity, IntegrationConfig, Task
from django.db.models import Sum, Count, Q
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from .utils import send_slack_message

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Log the user in after registration
            login(request, user)
            return redirect('dashboard')
    else:
        form = SignUpForm()
    
    return render(request, 'crm/signup.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                # Session is automatically created here by Django's login
                login(request, user)
                return redirect('dashboard')
    else:
        form = AuthenticationForm()

    return render(request, 'crm/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required(login_url='login')
def dashboard_view(request):
    # Calculate metrics
    user_role = request.user.role
    
    # 1. Pipeline Funnel Data (Group Opportunities by Stage)
    # Ensure all stages are represented even if 0
    stages = ['prospecting', 'proposal', 'negotiation', 'won', 'lost']
    pipeline_data = {stage: 0 for stage in stages}
    
    if user_role == 'admin':
        contacts_count = Contact.objects.count()
        leads_count = Lead.objects.exclude(status__in=['qualified', 'lost']).count()
        won_opps = Opportunity.objects.filter(stage='won').count()
        revenue = Opportunity.objects.filter(stage='won').aggregate(Sum('amount'))['amount__sum'] or 0
        
        # Aggregate pipeline
        stage_counts = Opportunity.objects.values('stage').annotate(count=Count('id'))
    else:
        contacts_count = Contact.objects.count()  # Everyone can see contacts
        leads_count = Lead.objects.filter(assigned_to=request.user).exclude(status__in=['qualified', 'lost']).count()
        won_opps = Opportunity.objects.filter(assigned_to=request.user, stage='won').count()
        revenue = Opportunity.objects.filter(assigned_to=request.user, stage='won').aggregate(Sum('amount'))['amount__sum'] or 0
        
        # Aggregate pipeline for user
        stage_counts = Opportunity.objects.filter(assigned_to=request.user).values('stage').annotate(count=Count('id'))

    # Fill the pipeline dictionary
    for item in stage_counts:
        pipeline_data[item['stage']] = item['count']

    # Convert to lists for Chart.js, maintaining order
    stage_labels = [s.capitalize() for s in stages]
    stage_values = [pipeline_data[s] for s in stages]

    # 2. Recent Activity
    if user_role == 'admin':
        recent_leads = Lead.objects.all().order_by('-created_at')[:5]
        recent_opps = Opportunity.objects.all().order_by('-created_at')[:5]
    else:
        recent_leads = Lead.objects.filter(assigned_to=request.user).order_by('-created_at')[:5]
        recent_opps = Opportunity.objects.filter(assigned_to=request.user).order_by('-created_at')[:5]

    context = {
        'total_contacts': contacts_count,
        'active_leads': leads_count,
        'opportunities_won': won_opps,
        'revenue_pipeline': revenue,
        'stage_labels': stage_labels,
        'stage_values': stage_values,
        'recent_leads': recent_leads,
        'recent_opportunities': recent_opps,
    }
    return render(request, 'crm/dashboard.html', context)

# --- Lead Views ---
class LeadListView(LoginRequiredMixin, ListView):
    model = Lead
    template_name = 'crm/lead_list.html'
    context_object_name = 'leads'
    login_url = 'login'
    paginate_by = 10

    def get_queryset(self):
        query = self.request.GET.get('q', '')
        
        # Allow agents to only see their leads, admins see all
        if self.request.user.role == 'admin':
            queryset = Lead.objects.all()
        else:
            queryset = Lead.objects.filter(assigned_to=self.request.user)
            
        if query:
            queryset = queryset.filter(
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query) |
                Q(email__icontains=query)
            )
            
        return queryset.order_by('-created_at')

class LeadDetailView(LoginRequiredMixin, DetailView):
    model = Lead
    template_name = 'crm/lead_detail.html'
    context_object_name = 'lead'
    login_url = 'login'

class LeadCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Lead
    form_class = LeadForm
    template_name = 'crm/lead_form.html'
    success_url = reverse_lazy('lead-list')
    login_url = 'login'
    success_message = "Lead '%(first_name)s %(last_name)s' was created successfully."

    def form_valid(self, form):
        form.instance.assigned_to = self.request.user
        return super().form_valid(form)

class LeadUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Lead
    form_class = LeadForm
    template_name = 'crm/lead_form.html'
    success_url = reverse_lazy('lead-list')
    login_url = 'login'
    success_message = "Lead '%(first_name)s %(last_name)s' was updated successfully."

class LeadDeleteView(LoginRequiredMixin, DeleteView):
    model = Lead
    template_name = 'crm/lead_confirm_delete.html'
    success_url = reverse_lazy('lead-list')
    login_url = 'login'

# --- Account Views ---
class AccountListView(LoginRequiredMixin, ListView):
    model = Account
    template_name = 'crm/account_list.html'
    context_object_name = 'accounts'
    login_url = 'login'
    paginate_by = 10
    
    def get_queryset(self):
        query = self.request.GET.get('q', '')
        queryset = Account.objects.all()
            
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) |
                Q(industry__icontains=query)
            )
            
        return queryset.order_by('-created_at')

class AccountDetailView(LoginRequiredMixin, DetailView):
    model = Account
    template_name = 'crm/account_detail.html'
    context_object_name = 'account'
    login_url = 'login'

class AccountCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Account
    form_class = AccountForm
    template_name = 'crm/account_form.html'
    success_url = reverse_lazy('account-list')
    login_url = 'login'
    success_message = "Account '%(name)s' was created successfully."

class AccountUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Account
    form_class = AccountForm
    template_name = 'crm/account_form.html'
    success_url = reverse_lazy('account-list')
    login_url = 'login'
    success_message = "Account '%(name)s' was updated successfully."

class AccountDeleteView(LoginRequiredMixin, DeleteView):
    model = Account
    template_name = 'crm/account_confirm_delete.html'
    success_url = reverse_lazy('account-list')
    login_url = 'login'

# --- Opportunity Views ---
class OpportunityListView(LoginRequiredMixin, ListView):
    model = Opportunity
    template_name = 'crm/opportunity_list.html'
    context_object_name = 'opportunities'
    login_url = 'login'
    paginate_by = 10
    
    def get_queryset(self):
        query = self.request.GET.get('q', '')
        stage = self.request.GET.get('stage', '')
        
        if self.request.user.role == 'admin':
            queryset = Opportunity.objects.all()
        else:
            queryset = Opportunity.objects.filter(assigned_to=self.request.user)
            
        if query:
            queryset = queryset.filter(name__icontains=query)
            
        if stage:
            queryset = queryset.filter(stage=stage)
            
        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Pass stages choices to the template for the dropdown
        context['stages'] = Opportunity._meta.get_field('stage').choices
        return context

class OpportunityDetailView(LoginRequiredMixin, DetailView):
    model = Opportunity
    template_name = 'crm/opportunity_detail.html'
    context_object_name = 'opportunity'
    login_url = 'login'

class OpportunityCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Opportunity
    form_class = OpportunityForm
    template_name = 'crm/opportunity_form.html'
    success_url = reverse_lazy('opportunity-list')
    login_url = 'login'
    success_message = "Opportunity '%(name)s' was created successfully."

    def form_valid(self, form):
        form.instance.assigned_to = self.request.user
        return super().form_valid(form)

class OpportunityUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Opportunity
    form_class = OpportunityForm
    template_name = 'crm/opportunity_form.html'
    success_url = reverse_lazy('opportunity-list')
    login_url = 'login'
    success_message = "Opportunity '%(name)s' was updated successfully."

class OpportunityDeleteView(LoginRequiredMixin, DeleteView):
    model = Opportunity
    template_name = 'crm/opportunity_confirm_delete.html'
    success_url = reverse_lazy('opportunity-list')
    login_url = 'login'

# --- Integration Views ---
class IntegrationListView(LoginRequiredMixin, ListView):
    model = IntegrationConfig
    template_name = 'crm/integration_list.html'
    context_object_name = 'integrations'
    login_url = 'login'

    def get_queryset(self):
        # Ensure default configs exist for display
        for service, label in IntegrationConfig.SERVICE_CHOICES:
            IntegrationConfig.objects.get_or_create(service=service)
        return IntegrationConfig.objects.all()

class OpportunityExportView(LoginRequiredMixin, DetailView):
    model = Opportunity
    login_url = 'login'

    def get(self, request, *args, **kwargs):
        opportunity = self.get_object()
        from .utils import export_opportunity_to_json
        from django.http import HttpResponse
        
        json_data = export_opportunity_to_json(opportunity)
        response = HttpResponse(json_data, content_type='application/json')
        response['Content-Disposition'] = f'attachment; filename="opportunity_{opportunity.id}_export.json"'
        return response

class IntegrationUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = IntegrationConfig
    form_class = IntegrationConfigForm
    template_name = 'crm/integration_form.html'
    success_url = reverse_lazy('integration-list')
    login_url = 'login'
    success_message = "Integration settings updated successfully."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['service_name'] = self.object.get_service_display()
        return context

@login_required(login_url='login')
def test_integration_view(request, pk):
    config = IntegrationConfig.objects.get(pk=pk)
    if config.service == 'slack':
        success = send_slack_message(f"🚀 Test connection from CRM Pro for Service: {config.get_service_display()}")
        if success:
            messages.success(request, f"Successfully sent test message to {config.get_service_display()}!")
        else:
            messages.error(request, f"Failed to send test message to {config.get_service_display()}. Check your webhook URL.")
    else:
        messages.info(request, f"Test connection for {config.get_service_display()} is not yet implemented.")
        
    return redirect('integration-update', pk=pk)
