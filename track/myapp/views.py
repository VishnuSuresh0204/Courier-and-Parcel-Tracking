
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout

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
                auth_logout(request)
                request.session.flush()

                messages.error(request, 'Invalid user type.')
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

            messages.error(request, 'Password does not match.')
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

        messages.success(request, 'Registration completed successfully.')

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

            messages.error(request, 'Password does not match.')
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

            messages.error(request, 'Invalid experience years.')
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

        messages.success(request, 'Delivery agent registered successfully.')

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

    total_branches = CourierBranch.objects.count()

    total_parcels = Parcel.objects.count()

    booked_parcels = Parcel.objects.filter(
        status='Booked'
    ).count()

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
        'total_branches': total_branches,
        'total_parcels': total_parcels,
        'booked_parcels': booked_parcels,
        'delivered_parcels': delivered_parcels,
        'pending_parcels': pending_parcels,
        'delayed_parcels': delayed_parcels,
    }

    return render(request, 'ADMIN/home.html', context)


# ==========================================
# 7. CUSTOMER DASHBOARD
# ==========================================

def customer_home(request):

    if 'userid' not in request.session:
        return redirect('/login')

    if request.session.get('usertype') != 'Customer':
        return redirect('/login')

    customer = get_object_or_404(
        CustomerRegistration,
        user_id=request.session['userid']
    )

    total_parcels = Parcel.objects.filter(
        customer=customer
    ).count()

    delivered_parcels = Parcel.objects.filter(
        customer=customer,
        status='Delivered'
    ).count()

    pending_parcels = Parcel.objects.filter(
        customer=customer
    ).exclude(
        status__in=['Delivered', 'Cancelled', 'Returned']
    ).count()

    recent_parcels = Parcel.objects.filter(
        customer=customer
    ).order_by('-booking_date')[:5]

    context = {
        'customer': customer,
        'total_parcels': total_parcels,
        'delivered_parcels': delivered_parcels,
        'pending_parcels': pending_parcels,
        'recent_parcels': recent_parcels,
    }

    return render(request, 'CUSTOMER/home.html', context)


# ==========================================
# 8. DELIVERY AGENT DASHBOARD
# ==========================================

def agent_home(request):

    if 'userid' not in request.session:
        return redirect('/login')

    if request.session.get('usertype') != 'Delivery Agent':
        return redirect('/login')

    agent = get_object_or_404(
        DeliveryAgentRegistration,
        user_id=request.session['userid']
    )

    context = {
        'agent': agent,
        'total_parcels': Parcel.objects.filter(
            status__in=['Picked Up', 'In Transit', 'At Branch', 'Out for Delivery']
        ).count(),
        'available_agents': DeliveryAgentRegistration.objects.filter(
            is_available=True,
            user__is_active=True
        ).count(),
    }

    return render(request, 'AGENT/home.html', context)


# ==========================================
# 9. CUSTOMER PROFILE
# ==========================================

def customer_profile(request):

    if 'userid' not in request.session:
        return redirect('/login')

    if request.session.get('usertype') != 'Customer':
        return redirect('/login')

    customer = get_object_or_404(
        CustomerRegistration,
        user_id=request.session['userid']
    )

    if request.method == 'POST':

        customer.name = request.POST.get('name')
        customer.email = request.POST.get('email')
        customer.phone = request.POST.get('phone')
        customer.address = request.POST.get('address')

        if request.FILES.get('profile_image'):
            customer.profile_image = request.FILES.get('profile_image')

        customer.save()

        customer.user.email = customer.email
        customer.user.save(update_fields=['email'])

        messages.success(request, 'Profile updated successfully.')

        return redirect('/customer_profile')

    return render(
        request,
        'CUSTOMER/profile.html',
        {'customer': customer}
    )


# ==========================================
# 10. DELIVERY AGENT PROFILE
# ==========================================

def agent_profile(request):

    if 'userid' not in request.session:
        return redirect('/login')

    if request.session.get('usertype') != 'Delivery Agent':
        return redirect('/login')

    agent = get_object_or_404(
        DeliveryAgentRegistration,
        user_id=request.session['userid']
    )

    if request.method == 'POST':

        agent.name = request.POST.get('name')
        agent.email = request.POST.get('email')
        agent.phone = request.POST.get('phone')
        agent.address = request.POST.get('address')

        agent.vehicle_number = request.POST.get('vehicle_number')
        agent.vehicle_type = request.POST.get('vehicle_type')

        if request.FILES.get('profile_image'):
            agent.profile_image = request.FILES.get('profile_image')

        agent.save()

        agent.user.email = agent.email
        agent.user.save(update_fields=['email'])

        messages.success(request, 'Profile updated successfully.')

        return redirect('/agent_profile')

    return render(
        request,
        'AGENT/profile.html',
        {'agent': agent}
    )


# ==========================================
# 11. VIEW CUSTOMERS - ADMIN
# ==========================================

def view_customers(request):

    if 'userid' not in request.session:
        return redirect('/login')

    if request.session.get('usertype') != 'Admin':
        return redirect('/login')

    customers = CustomerRegistration.objects.select_related(
        'user'
    ).order_by('-created_at')

    return render(
        request,
        'ADMIN/view_customers.html',
        {'customers': customers}
    )


# ==========================================
# 12. VIEW DELIVERY AGENTS - ADMIN
# ==========================================

def view_agents(request):

    if 'userid' not in request.session:
        return redirect('/login')

    if request.session.get('usertype') != 'Admin':
        return redirect('/login')

    agents = DeliveryAgentRegistration.objects.select_related(
        'user'
    ).order_by('-created_at')

    return render(
        request,
        'ADMIN/view_agents.html',
        {'agents': agents}
    )


# ==========================================
# 13. MANAGE BRANCHES - ADMIN
# ==========================================

def manage_branches(request):

    if 'userid' not in request.session:
        return redirect('/login')

    if request.session.get('usertype') != 'Admin':
        return redirect('/login')

    if request.method == 'POST':

        branch_name = request.POST.get('branch_name')
        branch_code = request.POST.get('branch_code')
        location = request.POST.get('location')
        address = request.POST.get('address')
        phone = request.POST.get('phone')
        email = request.POST.get('email')

        if not all([
            branch_name, branch_code,
            location, address, phone
        ]):

            messages.error(request, 'Please fill all required fields.')
            return redirect('/manage_branches')

        if CourierBranch.objects.filter(
            branch_code=branch_code
        ).exists():

            messages.error(request, 'Branch code already exists.')
            return redirect('/manage_branches')

        CourierBranch.objects.create(
            branch_name=branch_name,
            branch_code=branch_code,
            location=location,
            address=address,
            phone=phone,
            email=email
        )

        messages.success(request, 'Branch added successfully.')

        return redirect('/manage_branches')

    branches = CourierBranch.objects.all().order_by('-created_at')

    return render(
        request,
        'ADMIN/manage_branches.html',
        {'branches': branches}
    )


# ==========================================
# 14. TOGGLE BRANCH STATUS - ADMIN
# ==========================================

def toggle_branch_status(request, branch_id):

    if 'userid' not in request.session:
        return redirect('/login')

    if request.session.get('usertype') != 'Admin':
        return redirect('/login')

    branch = get_object_or_404(
        CourierBranch,
        id=branch_id
    )

    if request.method == 'POST':

        branch.is_active = not branch.is_active
        branch.save(update_fields=['is_active'])

        messages.success(request, 'Branch status updated.')

    return redirect('/manage_branches')


# ==========================================
# 15. TOGGLE AGENT STATUS - ADMIN
# ==========================================

def toggle_agent_status(request, agent_id):

    if 'userid' not in request.session:
        return redirect('/login')

    if request.session.get('usertype') != 'Admin':
        return redirect('/login')

    agent = get_object_or_404(
        DeliveryAgentRegistration,
        id=agent_id
    )

    if request.method == 'POST':

        agent.user.is_active = not agent.user.is_active
        agent.user.save(update_fields=['is_active'])

        messages.success(request, 'Agent account status updated.')

    return redirect('/view_agents')


# ==========================================
# 16. VIEW ALL PARCELS - ADMIN
# ==========================================

def view_all_parcels(request):

    if 'userid' not in request.session:
        return redirect('/login')

    if request.session.get('usertype') != 'Admin':
        return redirect('/login')

    parcels = Parcel.objects.select_related(
        'customer',
        'current_branch'
    ).order_by('-booking_date')

    return render(
        request,
        'ADMIN/view_parcels.html',
        {'parcels': parcels}
    )


# ==========================================
# 17. ADMIN PARCEL DETAILS
# ==========================================

def admin_parcel_detail(request, parcel_id):

    if 'userid' not in request.session:
        return redirect('/login')

    if request.session.get('usertype') != 'Admin':
        return redirect('/login')

    parcel = get_object_or_404(
        Parcel.objects.select_related(
            'customer',
            'current_branch'
        ),
        id=parcel_id
    )

    return render(
        request,
        'ADMIN/parcel_detail.html',
        {'parcel': parcel}
    )


# ==========================================
# 18. CANCEL PARCEL - ADMIN
# ==========================================

def cancel_parcel(request, parcel_id):

    if 'userid' not in request.session:
        return redirect('/login')

    if request.session.get('usertype') != 'Admin':
        return redirect('/login')

    parcel = get_object_or_404(
        Parcel,
        id=parcel_id
    )

    if request.method == 'POST':

        if parcel.status == 'Delivered':

            messages.error(request, 'Delivered parcel cannot be cancelled.')

        else:

            parcel.status = 'Cancelled'
            parcel.save(update_fields=['status'])

            messages.success(request, 'Parcel cancelled successfully.')

    return redirect('/admin_parcel_detail/' + str(parcel.id))


# ==========================================
# 19. BOOK PARCEL - CUSTOMER
# ==========================================

def book_parcel(request):

    if 'userid' not in request.session:
        return redirect('/login')

    if request.session.get('usertype') != 'Customer':
        return redirect('/login')

    customer = get_object_or_404(
        CustomerRegistration,
        user_id=request.session['userid']
    )

    if request.method == 'POST':

        sender_name = request.POST.get('sender_name')
        sender_phone = request.POST.get('sender_phone')
        sender_address = request.POST.get('sender_address')

        receiver_name = request.POST.get('receiver_name')
        receiver_phone = request.POST.get('receiver_phone')
        receiver_address = request.POST.get('receiver_address')

        source = request.POST.get('source')
        destination = request.POST.get('destination')

        parcel_type = request.POST.get('parcel_type')
        parcel_description = request.POST.get('parcel_description')

        weight = request.POST.get('weight')
        distance_km = request.POST.get('distance_km')
        delivery_type = request.POST.get('delivery_type')

        if not all([
            sender_name, sender_phone, sender_address,
            receiver_name, receiver_phone, receiver_address,
            source, destination, parcel_type,
            weight, distance_km, delivery_type
        ]):

            messages.error(request, 'Please fill all required fields.')
            return redirect('/book_parcel')

        try:

            weight = float(weight)
            distance_km = float(distance_km)

            if weight <= 0 or distance_km <= 0:
                raise ValueError

        except (ValueError, TypeError):

            messages.error(request, 'Enter valid weight and distance.')
            return redirect('/book_parcel')

        delivery_charges = {
            'Standard': 50,
            'Express': 100,
            'Same Day': 150
        }

        if delivery_type not in delivery_charges:

            messages.error(request, 'Invalid delivery type.')
            return redirect('/book_parcel')

        parcel = Parcel.objects.create(
            customer=customer,
            sender_name=sender_name,
            sender_phone=sender_phone,
            sender_address=sender_address,
            receiver_name=receiver_name,
            receiver_phone=receiver_phone,
            receiver_address=receiver_address,
            source=source,
            destination=destination,
            parcel_type=parcel_type,
            parcel_description=parcel_description,
            weight=weight,
            distance_km=distance_km,
            delivery_type=delivery_type,
            delivery_charge=delivery_charges[delivery_type],
            status='Booked'
        )

        messages.success(
            request,
            'Parcel booked successfully. Tracking ID: ' + parcel.tracking_id
        )

        return redirect('/customer_parcels')

    return render(request, 'CUSTOMER/book_parcel.html')


# ==========================================
# 20. CUSTOMER PARCEL LIST
# ==========================================

def customer_parcels(request):

    if 'userid' not in request.session:
        return redirect('/login')

    if request.session.get('usertype') != 'Customer':
        return redirect('/login')

    customer = get_object_or_404(
        CustomerRegistration,
        user_id=request.session['userid']
    )

    parcels = Parcel.objects.filter(
        customer=customer
    ).order_by('-booking_date')

    return render(
        request,
        'CUSTOMER/parcels.html',
        {'parcels': parcels}
    )


# ==========================================
# 21. CUSTOMER TRACK PARCEL
# ==========================================

def track_parcel(request, parcel_id):

    if 'userid' not in request.session:
        return redirect('/login')

    if request.session.get('usertype') != 'Customer':
        return redirect('/login')

    customer = get_object_or_404(
        CustomerRegistration,
        user_id=request.session['userid']
    )

    parcel = get_object_or_404(
        Parcel,
        id=parcel_id,
        customer=customer
    )

    return render(
        request,
        'CUSTOMER/track_parcel.html',
        {'parcel': parcel}
    )


# ==========================================
# 22. PUBLIC TRACK PARCEL
# ==========================================

def public_track_parcel(request):

    parcel = None

    if request.method == 'POST':

        tracking_id = request.POST.get(
            'tracking_id',
            ''
        ).strip().upper()

        if tracking_id:

            try:

                parcel = Parcel.objects.get(
                    tracking_id=tracking_id
                )

            except Parcel.DoesNotExist:

                messages.error(request, 'Invalid tracking ID.')

        else:

            messages.error(request, 'Please enter a tracking ID.')

    return render(
        request,
        'track_parcel.html',
        {'parcel': parcel}
    )


# ==========================================
# 23. CUSTOMER CANCEL PARCEL
# ==========================================

def customer_cancel_parcel(request, parcel_id):

    if 'userid' not in request.session:
        return redirect('/login')

    if request.session.get('usertype') != 'Customer':
        return redirect('/login')

    customer = get_object_or_404(
        CustomerRegistration,
        user_id=request.session['userid']
    )

    parcel = get_object_or_404(
        Parcel,
        id=parcel_id,
        customer=customer
    )

    if request.method == 'POST':

        if parcel.status != 'Booked':

            messages.error(
                request,
                'Only booked parcels can be cancelled.'
            )

        else:

            parcel.status = 'Cancelled'
            parcel.save(update_fields=['status'])

            messages.success(request, 'Parcel cancelled successfully.')

    return redirect('/customer_parcels')


# ==========================================
# 24. UPDATE PARCEL STATUS - ADMIN
# ==========================================

def update_parcel_status(request, parcel_id):

    if 'userid' not in request.session:
        return redirect('/login')

    if request.session.get('usertype') != 'Admin':
        return redirect('/login')

    parcel = get_object_or_404(
        Parcel,
        id=parcel_id
    )

    if request.method == 'POST':

        status = request.POST.get('status')

        valid_statuses = [
            'Booked',
            'Picked Up',
            'In Transit',
            'At Branch',
            'Out for Delivery',
            'Delivered',
            'Delayed',
            'Cancelled',
            'Returned'
        ]

        if status not in valid_statuses:

            messages.error(request, 'Invalid parcel status.')

        else:

            parcel.status = status
            parcel.save(update_fields=['status'])

            messages.success(request, 'Parcel status updated successfully.')

    return redirect('/admin_parcel_detail/' + str(parcel.id))


# ==========================================
# 25. UPDATE CURRENT BRANCH - ADMIN
# ==========================================

def update_parcel_branch(request, parcel_id):

    if 'userid' not in request.session:
        return redirect('/login')

    if request.session.get('usertype') != 'Admin':
        return redirect('/login')

    parcel = get_object_or_404(
        Parcel,
        id=parcel_id
    )

    if request.method == 'POST':

        branch_id = request.POST.get('branch_id')

        if branch_id:

            branch = get_object_or_404(
                CourierBranch,
                id=branch_id,
                is_active=True
            )

            parcel.current_branch = branch
            parcel.save(update_fields=['current_branch'])

            messages.success(request, 'Parcel branch updated.')

        else:

            parcel.current_branch = None
            parcel.save(update_fields=['current_branch'])

            messages.success(request, 'Parcel branch removed.')

    return redirect('/admin_parcel_detail/' + str(parcel.id))


# ==========================================
# 26. TOGGLE DELIVERY AGENT AVAILABILITY
# ==========================================

def toggle_agent_availability(request):

    if 'userid' not in request.session:
        return redirect('/login')

    if request.session.get('usertype') != 'Delivery Agent':
        return redirect('/login')

    agent = get_object_or_404(
        DeliveryAgentRegistration,
        user_id=request.session['userid']
    )

    if request.method == 'POST':

        agent.is_available = not agent.is_available
        agent.save(update_fields=['is_available'])

        messages.success(request, 'Availability updated successfully.')

    return redirect('/agent_home')
