from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Account, Contact, Lead, Opportunity, Task, IntegrationConfig

admin.site.register(User, UserAdmin)
admin.site.register(Account)
admin.site.register(Contact)
admin.site.register(Lead)
admin.site.register(Opportunity)
admin.site.register(Task)
admin.site.register(IntegrationConfig)
