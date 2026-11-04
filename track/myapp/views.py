
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.utils import timezone
from django.db import transaction

from .models import *


# ==========================================
# 1. HOME
# ==========================================

def home(request):
    return render(request, 'home.html')


# ==========================================
# 2. LOGIN
# ==========================================

def login(request):

    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            if not user.is_active:
                messages.error(request, 'Your account is inactive.')
                return redirect('/login')

            auth_login(request, user)

            request.session['userid'] = user.id
            request.session['username'] = user.username

            if user.is_superuser:

                request.session['usertype'] = 'Admin'
                return redirect('/admin_home')

            request.session['usertype'] = user.user_type

            if user.user_type == 'Customer':
                return redirect('/customer_home')

            elif user.user_type == 'Delivery Agent':
                return redirect('/agent_home')

            else:
                messages.error(request, 'Invalid user type.')
                auth_logout(request)
                request.session.flush()
                return redirect('/login')

        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'login.html')


# ==========================================
# 3. LOGOUT
# ==========================================

def logout(request):

    auth_logout(request)
    request.session.flush()

    return redirect('/')


# ==========================================
# 4. CUSTOMER REGISTRATION
# ==========================================

def customer_registration(request):

    if request.method == 'POST':

        name = request.POST.get('name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        profile_image = request.FILES.get('profile_image')

        if password != confirm_password:

            messages.error(request, 'Passwords do not match.')
            return redirect('/customer_registration')

        if Login.objects.filter(username=username).exists():

            messages.error(request, 'Username already exists.')
            return redirect('/customer_registration')

        if not all([name, username, email, phone, address, password]):

            messages.error(request, 'Please fill all required fields.')
            return redirect('/customer_registration')

        user = Login.objects.create_user(
            username=username,
            email=email,
            password=password,
            user_type='Customer',
            view_pass=password
        )

        CustomerRegistration.objects.create(
            user=user,
            name=name,
            email=email,
            phone=phone,
            address=address,
            profile_image=profile_image
        )

        messages.success(request, 'Customer registration completed.')
        return redirect('/login')

    return render(request, 'customer_registration.html')


# ==========================================
# 5. DELIVERY AGENT REGISTRATION
# ==========================================

def agent_registration(request):

    if request.method == 'POST':

        name = request.POST.get('name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')

        employee_id = request.POST.get('employee_id')
        vehicle_number = request.POST.get('vehicle_number')
        vehicle_type = request.POST.get('vehicle_type')
        experience_years = request.POST.get('experience_years', 0)

        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        profile_image = request.FILES.get('profile_image')

        if password != confirm_password:

            messages.error(request, 'Passwords do not match.')
            return redirect('/agent_registration')

        if Login.objects.filter(username=username).exists():

            messages.error(request, 'Username already exists.')
            return redirect('/agent_registration')

        if DeliveryAgentRegistration.objects.filter(
            employee_id=employee_id
        ).exists():

            messages.error(request, 'Employee ID already exists.')
            return redirect('/agent_registration')

        if not all([
            name, username, email, phone, address,
            employee_id, vehicle_number, vehicle_type, password
        ]):

            messages.error(request, 'Please fill all required fields.')
            return redirect('/agent_registration')

        try:
            experience_years = int(experience_years)

            if experience_years < 0:
                raise ValueError

        except (ValueError, TypeError):

            messages.error(request, 'Invalid experience value.')
            return redirect('/agent_registration')

        user = Login.objects.create_user(
            username=username,
            email=email,
            password=password,
            user_type='Delivery Agent',
            view_pass=password
        )

        DeliveryAgentRegistration.objects.create(
            user=user,
            name=name,
            email=email,
            phone=phone,
            address=address,
            employee_id=employee_id,
            vehicle_number=vehicle_number,
            vehicle_type=vehicle_type,
            experience_years=experience_years,
            profile_image=profile_image
        )

        messages.success(request, 'Delivery agent registration completed.')
        return redirect('/login')

    return render(request, 'agent_registration.html')


# ==========================================
# 6. ADMIN DASHBOARD
# ==========================================

def admin_home(request):

    if 'userid' not in request.session:
        return redirect('/login')

    if request.session.get('usertype') != 'Admin':
        return redirect('/login')

    total_customers = CustomerRegistration.objects.count()
    total_agents = DeliveryAgentRegistration.objects.count()
    total_parcels = Parcel.objects.count()

    delivered_parcels = Parcel.objects.filter(
        status='Delivered'
    ).count()

    pending_parcels = Parcel.objects.filter(
        status__in=[
            'Booked',
            'Picked Up',
            'In Transit',
            'At Branch',
            'Out for Delivery'
        ]
    ).count()

    delayed_parcels = Parcel.objects.filter(
        status='Delayed'
    ).count()

    context = {
        'total_customers': total_customers,
        'total_agents': total_agents,
        'total_parcels': total_parcels,
        'delivered_parcels': delivered_parcels,
        'pending_parcels': pending_parcels,
        'delayed_parcels': delayed_parcels,
    }

    return render(request, 'ADMIN/home.html', context)

