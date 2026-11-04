from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from myapp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Home & Authentication
    path('', views.home, name='home'),
    path('login', views.login, name='login'),
    path('login/', views.login),
    path('logout', views.logout, name='logout'),
    path('logout/', views.logout),
    path('customer_registration', views.customer_registration, name='customer_registration'),
    path('customer_registration/', views.customer_registration),
    path('agent_registration', views.agent_registration, name='agent_registration'),
    path('agent_registration/', views.agent_registration),
    
    # Public Tracking
    path('public_track_parcel', views.public_track_parcel, name='public_track_parcel'),
    path('public_track_parcel/', views.public_track_parcel),
    
    # Admin Portal
    path('admin_home', views.admin_home, name='admin_home'),
    path('admin_home/', views.admin_home),
    path('view_customers', views.view_customers, name='view_customers'),
    path('view_customers/', views.view_customers),
    path('view_agents', views.view_agents, name='view_agents'),
    path('view_agents/', views.view_agents),
    path('manage_branches', views.manage_branches, name='manage_branches'),
    path('manage_branches/', views.manage_branches),
    path('toggle_branch_status/<int:branch_id>', views.toggle_branch_status, name='toggle_branch_status'),
    path('toggle_agent_status/<int:agent_id>', views.toggle_agent_status, name='toggle_agent_status'),
    path('view_all_parcels', views.view_all_parcels, name='view_all_parcels'),
    path('view_all_parcels/', views.view_all_parcels),
    path('admin_parcel_detail/<int:parcel_id>', views.admin_parcel_detail, name='admin_parcel_detail'),
    path('cancel_parcel/<int:parcel_id>', views.cancel_parcel, name='cancel_parcel'),
    path('update_parcel_status/<int:parcel_id>', views.update_parcel_status, name='update_parcel_status'),
    path('update_parcel_branch/<int:parcel_id>', views.update_parcel_branch, name='update_parcel_branch'),
    
    # Customer Portal
    path('customer_home', views.customer_home, name='customer_home'),
    path('customer_home/', views.customer_home),
    path('book_parcel', views.book_parcel, name='book_parcel'),
    path('book_parcel/', views.book_parcel),
    path('customer_parcels', views.customer_parcels, name='customer_parcels'),
    path('customer_parcels/', views.customer_parcels),
    path('track_parcel/<int:parcel_id>', views.track_parcel, name='track_parcel'),
    path('customer_cancel_parcel/<int:parcel_id>', views.customer_cancel_parcel, name='customer_cancel_parcel'),
    path('customer_profile', views.customer_profile, name='customer_profile'),
    path('customer_profile/', views.customer_profile),
    
    # Delivery Agent Portal
    path('agent_home', views.agent_home, name='agent_home'),
    path('agent_home/', views.agent_home),
    path('agent_profile', views.agent_profile, name='agent_profile'),
    path('agent_profile/', views.agent_profile),
    path('toggle_agent_availability', views.toggle_agent_availability, name='toggle_agent_availability'),
    path('toggle_agent_availability/', views.toggle_agent_availability),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
