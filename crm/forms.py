from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Account, Contact, Lead, Opportunity

class SignUpForm(UserCreationForm):
    role = forms.ChoiceField(choices=User.ROLE_CHOICES, required=False)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'role')

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
