from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Lead URLs
    path('leads/', views.LeadListView.as_view(), name='lead-list'),
    path('leads/create/', views.LeadCreateView.as_view(), name='lead-create'),
    path('leads/<int:pk>/', views.LeadDetailView.as_view(), name='lead-detail'),
    path('leads/<int:pk>/update/', views.LeadUpdateView.as_view(), name='lead-update'),
    path('leads/<int:pk>/delete/', views.LeadDeleteView.as_view(), name='lead-delete'),

    # Account URLs
    path('accounts/', views.AccountListView.as_view(), name='account-list'),
    path('accounts/create/', views.AccountCreateView.as_view(), name='account-create'),
    path('accounts/<int:pk>/', views.AccountDetailView.as_view(), name='account-detail'),
    path('accounts/<int:pk>/update/', views.AccountUpdateView.as_view(), name='account-update'),
    path('accounts/<int:pk>/delete/', views.AccountDeleteView.as_view(), name='account-delete'),

    # Opportunity URLs
    path('opportunities/', views.OpportunityListView.as_view(), name='opportunity-list'),
    path('opportunities/create/', views.OpportunityCreateView.as_view(), name='opportunity-create'),
    path('opportunities/<int:pk>/', views.OpportunityDetailView.as_view(), name='opportunity-detail'),
    path('opportunities/<int:pk>/update/', views.OpportunityUpdateView.as_view(), name='opportunity-update'),
    path('opportunities/<int:pk>/delete/', views.OpportunityDeleteView.as_view(), name='opportunity-delete'),

    # Integration URLs
    path('integrations/', views.IntegrationListView.as_view(), name='integration-list'),
    path('integrations/<int:pk>/configure/', views.IntegrationUpdateView.as_view(), name='integration-update'),
    path('integrations/<int:pk>/test/', views.test_integration_view, name='integration-test'),
    path('opportunities/<int:pk>/export/', views.OpportunityExportView.as_view(), name='opportunity-export'),
]
