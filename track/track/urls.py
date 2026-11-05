
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from myapp import views


urlpatterns = [

    # ==========================================
    # ADMIN
    # ==========================================

    path('admin/', admin.site.urls),

    # ==========================================
    # HOME & AUTHENTICATION
    # ==========================================

    path('', views.home, name='home'),

    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),

    path('customer_registration/', views.customer_registration, name='customer_registration'),
    path('agent_registration/', views.agent_registration, name='agent_registration'),

    # ==========================================
    # PUBLIC PARCEL TRACKING
    # ==========================================

    path('public_track_parcel/', views.public_track_parcel, name='public_track_parcel'),

    # ==========================================
    # ADMIN DASHBOARD
    # ==========================================

    path('admin_home/', views.admin_home, name='admin_home'),

    # ==========================================
    # ADMIN - CUSTOMER MANAGEMENT
    # ==========================================

    path('view_customers/', views.view_customers, name='view_customers'),

    # ==========================================
    # ADMIN - DELIVERY AGENT MANAGEMENT
    # ==========================================

    path('view_agents/', views.view_agents, name='view_agents'),
    path('toggle_agent_status/<int:agent_id>/', views.toggle_agent_status, name='toggle_agent_status'),

    # ==========================================
    # ADMIN - BRANCH MANAGEMENT
    # ==========================================

    path('manage_branches/', views.manage_branches, name='manage_branches'),
    path('toggle_branch_status/<int:branch_id>/', views.toggle_branch_status, name='toggle_branch_status'),

    # ==========================================
    # ADMIN - PARCEL MANAGEMENT
    # ==========================================

    path('view_all_parcels/', views.view_all_parcels, name='view_all_parcels'),
    path('admin_parcel_detail/<int:parcel_id>/', views.admin_parcel_detail, name='admin_parcel_detail'),
    path('cancel_parcel/<int:parcel_id>/', views.cancel_parcel, name='cancel_parcel'),

    # ==========================================
    # ADMIN - PARCEL ASSIGNMENT
    # ==========================================

    path('assign_parcel/', views.assign_parcel, name='assign_parcel'),
    path('assign_parcel/<int:parcel_id>/', views.assign_parcel, name='assign_parcel_id'),
    path('delivery_assignments/', views.delivery_assignments, name='delivery_assignments'),
    path('reassign_parcel/<int:assignment_id>/', views.reassign_parcel, name='reassign_parcel'),

    # ==========================================
    # ADMIN - DELIVERY RECORDS & TRACKING HISTORY
    # ==========================================

    path('view_delivery_records/', views.view_delivery_records, name='view_delivery_records'),
    path('all_tracking_history/', views.all_tracking_history, name='all_tracking_history'),

    # ==========================================
    # CUSTOMER DASHBOARD
    # ==========================================

    path('customer_home/', views.customer_home, name='customer_home'),

    # ==========================================
    # CUSTOMER - PARCEL BOOKING
    # ==========================================

    path('book_parcel/', views.book_parcel, name='book_parcel'),
    path('customer_parcels/', views.customer_parcels, name='customer_parcels'),
    path('track_parcel/<int:parcel_id>/', views.track_parcel, name='track_parcel'),
    path('customer_cancel_parcel/<int:parcel_id>/', views.customer_cancel_parcel, name='customer_cancel_parcel'),

    # ==========================================
    # CUSTOMER - PROFILE
    # ==========================================

    path('customer_profile/', views.customer_profile, name='customer_profile'),

    # ==========================================
    # DELIVERY AGENT DASHBOARD
    # ==========================================

    path('agent_home/', views.agent_home, name='agent_home'),

    # ==========================================
    # DELIVERY AGENT - PROFILE
    # ==========================================

    path('agent_profile/', views.agent_profile, name='agent_profile'),
    path('toggle_agent_availability/', views.toggle_agent_availability, name='toggle_agent_availability'),

    # ==========================================
    # DELIVERY AGENT - ASSIGNED PARCELS
    # ==========================================

    path('assigned_parcels/', views.assigned_parcels, name='assigned_parcels'),
    path('agent_parcel_detail/<int:parcel_id>/', views.agent_parcel_detail, name='agent_parcel_detail'),

    # ==========================================
    # DELIVERY AGENT - TRACKING UPDATES
    # ==========================================

    path('update_parcel_tracking/<int:parcel_id>/', views.update_parcel_tracking, name='update_parcel_tracking'),

    # ==========================================
    # DELIVERY AGENT - DELIVERY COMPLETION
    # ==========================================

    path('complete_delivery/<int:parcel_id>/', views.complete_delivery, name='complete_delivery'),
    path('failed_delivery/<int:parcel_id>/', views.failed_delivery, name='failed_delivery'),

]


# ==========================================
# MEDIA FILE CONFIGURATION
# ==========================================

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
