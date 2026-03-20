from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Account, Contact, Lead, Opportunity, IntegrationConfig

class IntegrationConfigForm(forms.ModelForm):
    class Meta:
        model = IntegrationConfig
        fields = ('webhook_url', 'api_key', 'is_active')
        widgets = {
            'webhook_url': forms.URLInput(attrs={
                'class': 'block w-full px-4 py-3 border border-gray-200 bg-gray-50/50 rounded-xl text-gray-900 focus:bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all duration-200 sm:text-sm',
                'placeholder': 'https://example.com/your-webhook-url'
            }),
            'api_key': forms.TextInput(attrs={
                'class': 'block w-full px-4 py-3 border border-gray-200 bg-gray-50/50 rounded-xl text-gray-900 focus:bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all duration-200 sm:text-sm',
                'placeholder': 'Enter API Key'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded'
            }),
        }

class SignUpForm(UserCreationForm):
    role = forms.ChoiceField(
        choices=User.ROLE_CHOICES, 
        required=True,
        widget=forms.Select(attrs={
            'class': 'block w-full pl-10 pr-4 py-3 border border-gray-200 bg-gray-50/50 rounded-xl text-gray-900 focus:bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all duration-200 sm:text-sm'
        })
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'role')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'block w-full pl-10 pr-4 py-3 border border-gray-200 bg-gray-50/50 rounded-xl text-gray-900 placeholder-gray-400 focus:bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all duration-200 sm:text-sm',
                'placeholder': 'Enter username'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'block w-full pl-10 pr-4 py-3 border border-gray-200 bg-gray-50/50 rounded-xl text-gray-900 placeholder-gray-400 focus:bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all duration-200 sm:text-sm',
                'placeholder': 'name@company.com'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apply classes to the base UserCreationForm fields (password1, password2)
        password_classes = 'block w-full pl-10 pr-4 py-3 border border-gray-200 bg-gray-50/50 rounded-xl text-gray-900 placeholder-gray-400 focus:bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all duration-200 sm:text-sm'
        if 'password1' in self.fields:
            self.fields['password1'].widget.attrs.update({'class': password_classes, 'placeholder': 'Create password'})
        if 'password2' in self.fields:
            self.fields['password2'].widget.attrs.update({'class': password_classes, 'placeholder': 'Confirm password'})

class LeadForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = ('first_name', 'last_name', 'email', 'phone', 'status', 'source')

class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ('name', 'industry', 'website', 'address')

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ('account', 'first_name', 'last_name', 'email', 'phone')

class OpportunityForm(forms.ModelForm):
    class Meta:
        model = Opportunity
        fields = ('name', 'account', 'contact', 'amount', 'stage', 'expected_close_date')
        widgets = {
            'expected_close_date': forms.DateInput(attrs={'type': 'date'}),
        }
