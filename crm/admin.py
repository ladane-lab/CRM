from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Account, Contact, Lead, Opportunity

admin.site.register(User, UserAdmin)
admin.site.register(Account)
admin.site.register(Contact)
admin.site.register(Lead)
admin.site.register(Opportunity)
