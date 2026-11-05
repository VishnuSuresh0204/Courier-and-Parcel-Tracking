
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.db import transaction
from django.utils import timezone

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

        if not all([name, username, email, phone, address, password]):
            messages.error(request, 'Please fill all required fields.')
            return redirect('/customer_registration')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return redirect('/customer_registration')

        if Login.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return redirect('/customer_registration')

        if Login.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return redirect('/customer_registration')

        with transaction.atomic():

            user = Login.objects.create_user(
                username=username,
                email=email,
                password=password,
                user_type='Customer',
                view_pass=''
            )

            CustomerRegistration.objects.create(
                user=user,
                name=name,
                email=email,
                phone=phone,
                address=address,
                profile_image=profile_image
            )

        messages.success(request, 'Customer registration completed successfully.')
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

        if not all([
            name, username, email, phone, address,
            employee_id, vehicle_number, vehicle_type, password
        ]):
            messages.error(request, 'Please fill all required fields.')
            return redirect('/agent_registration')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return redirect('/agent_registration')

        if Login.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return redirect('/agent_registration')

        if Login.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return redirect('/agent_registration')

        if DeliveryAgentRegistration.objects.filter(
            employee_id=employee_id
        ).exists():
            messages.error(request, 'Employee ID already exists.')
            return redirect('/agent_registration')

        try:
            experience_years = int(experience_years)

            if experience_years < 0:
                raise ValueError

        except (ValueError, TypeError):
            messages.error(request, 'Invalid experience years.')
            return redirect('/agent_registration')

        with transaction.atomic():

            user = Login.objects.create_user(
                username=username,
                email=email,
                password=password,
                user_type='Delivery Agent',
                view_pass=''
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

    context = {
        'total_customers': CustomerRegistration.objects.count(),
        'total_agents': DeliveryAgentRegistration.objects.count(),
        'total_branches': CourierBranch.objects.count(),
        'total_parcels': Parcel.objects.count(),

        'booked_parcels': Parcel.objects.filter(
            status='Booked'
        ).count(),

        'delivered_parcels': Parcel.objects.filter(
            status='Delivered'
        ).count(),

        'pending_parcels': Parcel.objects.filter(
            status__in=[
                'Booked',
                'Picked Up',
                'In Transit',
                'At Branch',
                'Out for Delivery'
            ]
        ).count(),

        'delayed_parcels': Parcel.objects.filter(
            status='Delayed'
        ).count(),

        'active_assignments': DeliveryAssignment.objects.filter(
            assignment_status__in=['Assigned', 'In Progress']
        ).count(),
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

    context = {
        'customer': customer,

        'total_parcels': Parcel.objects.filter(
            customer=customer
        ).count(),

        'delivered_parcels': Parcel.objects.filter(
            customer=customer,
            status='Delivered'
        ).count(),

        'pending_parcels': Parcel.objects.filter(
            customer=customer,
            status__in=[
                'Booked',
                'Picked Up',
                'In Transit',
                'At Branch',
                'Out for Delivery',
                'Delayed'
            ]
        ).count(),

        'recent_parcels': Parcel.objects.filter(
            customer=customer
        ).order_by('-booking_date')[:5],
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

    assignments = DeliveryAssignment.objects.filter(
        delivery_agent=agent,
        assignment_status__in=['Assigned', 'In Progress']
    ).select_related('parcel').order_by('-assigned_at')

    context = {
        'agent': agent,
        'assignments': assignments,

        'total_assignments': DeliveryAssignment.objects.filter(
            delivery_agent=agent
        ).count(),

        'completed_deliveries': DeliveryAssignment.objects.filter(
            delivery_agent=agent,
            assignment_status='Completed'
        ).count(),

        'active_assignments': assignments.count(),
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
# 13. MANAGE COURIER BRANCHES - ADMIN
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

        if not all([branch_name, branch_code, location, address, phone]):
            messages.error(request, 'Please fill all required fields.')
            return redirect('/manage_branches')

        if CourierBranch.objects.filter(branch_code=branch_code).exists():
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

    branch = get_object_or_404(CourierBranch, id=branch_id)

    if request.method == 'POST':

        branch.is_active = not branch.is_active
        branch.save(update_fields=['is_active'])

        messages.success(request, 'Branch status updated.')

    return redirect('/manage_branches')


# ==========================================
# 15. TOGGLE AGENT ACCOUNT STATUS - ADMIN
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

        if agent.user.is_active:

            active_assignments = DeliveryAssignment.objects.filter(
                delivery_agent=agent,
                assignment_status__in=['Assigned', 'In Progress']
            ).exists()

            if active_assignments:
                messages.error(
                    request,
                    'Cannot deactivate an agent with active assignments.'
                )
                return redirect('/view_agents')

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

    history = ParcelTrackingHistory.objects.filter(
        parcel=parcel
    ).select_related('updated_by').order_by('-updated_at')

    assignments = DeliveryAssignment.objects.filter(
        parcel=parcel
    ).select_related(
        'delivery_agent',
        'assigned_by'
    ).order_by('-assigned_at')

    return render(
        request,
        'ADMIN/parcel_detail.html',
        {
            'parcel': parcel,
            'history': history,
            'assignments': assignments
        }
    )


# ==========================================
# 18. CANCEL PARCEL - ADMIN
# ==========================================

def cancel_parcel(request, parcel_id):

    if 'userid' not in request.session:
        return redirect('/login')

    if request.session.get('usertype') != 'Admin':
        return redirect('/login')

    parcel = get_object_or_404(Parcel, id=parcel_id)

    if request.method == 'POST':

        if parcel.status in ['Delivered', 'Cancelled', 'Returned']:
            messages.error(request, 'This parcel cannot be cancelled.')
            return redirect('/admin_parcel_detail/' + str(parcel.id))

        with transaction.atomic():

            active_assignments = DeliveryAssignment.objects.filter(
                parcel=parcel,
                assignment_status__in=['Assigned', 'In Progress']
            )

            affected_agents = list(
                DeliveryAgentRegistration.objects.filter(
                    assignments__in=active_assignments
                ).distinct()
            )

            active_assignments.update(
                assignment_status='Cancelled'
            )

            for agent in affected_agents:

                other_active = DeliveryAssignment.objects.filter(
                    delivery_agent=agent,
                    assignment_status__in=['Assigned', 'In Progress']
                ).exists()

                if not other_active:
                    agent.is_available = True
                    agent.save(update_fields=['is_available'])

            parcel.status = 'Cancelled'
            parcel.save(update_fields=['status'])

            ParcelTrackingHistory.objects.create(
                parcel=parcel,
                status='Cancelled',
                location=parcel.current_branch.location if parcel.current_branch else parcel.source,
                description='Parcel cancelled by administrator.',
                updated_by_id=request.session['userid']
            )

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

        ParcelTrackingHistory.objects.create(
            parcel=parcel,
            status='Booked',
            location=source,
            description='Parcel booking completed.',
            updated_by_id=request.session['userid']
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
    ).select_related('current_branch').order_by('-booking_date')

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

    history = ParcelTrackingHistory.objects.filter(
        parcel=parcel
    ).order_by('-updated_at')

    return render(
        request,
        'CUSTOMER/track_parcel.html',
        {
            'parcel': parcel,
            'history': history
        }
    )


# ==========================================
# 22. PUBLIC PARCEL TRACKING
# ==========================================

def public_track_parcel(request):

    parcel = None
    history = None

    if request.method == 'POST':

        tracking_id = request.POST.get(
            'tracking_id', ''
        ).strip().upper()

        if tracking_id:

            try:
                parcel = Parcel.objects.select_related(
                    'current_branch'
                ).get(tracking_id=tracking_id)

                history = ParcelTrackingHistory.objects.filter(
                    parcel=parcel
                ).order_by('-updated_at')

            except Parcel.DoesNotExist:
                messages.error(request, 'Invalid tracking ID.')

        else:
            messages.error(request, 'Please enter a tracking ID.')

    return render(
        request,
        'track_parcel.html',
        {
            'parcel': parcel,
            'history': history
        }
    )


# ==========================================
# 23. CANCEL PARCEL - CUSTOMER
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
                'Only booked parcels can be cancelled by the customer.'
            )

        else:

            parcel.status = 'Cancelled'
            parcel.save(update_fields=['status'])

            ParcelTrackingHistory.objects.create(
                parcel=parcel,
                status='Cancelled',
                location=parcel.source,
                description='Parcel cancelled by customer.',
                updated_by_id=request.session['userid']
            )

            messages.success(request, 'Parcel cancelled successfully.')

    return redirect('/customer_parcels')


# ==========================================
# 24. ASSIGN PARCEL TO DELIVERY AGENT - ADMIN
# ==========================================

def assign_parcel(request, parcel_id=None):

    if 'userid' not in request.session:
        return redirect('/login')

    if request.session.get('usertype') != 'Admin':
        return redirect('/login')

    parcels = Parcel.objects.filter(
        status__in=['Booked', 'At Branch']
    ).order_by('-booking_date')

    agents = DeliveryAgentRegistration.objects.filter(
        is_available=True,
        user__is_active=True
    ).select_related('user')

    if request.method == 'POST':

        parcel_id = request.POST.get('parcel_id')
        agent_id = request.POST.get('agent_id')

        parcel = get_object_or_404(Parcel, id=parcel_id)

        agent = get_object_or_404(
            DeliveryAgentRegistration,
            id=agent_id,
            is_available=True,
            user__is_active=True
        )

        if parcel.status not in ['Booked', 'At Branch']:
            messages.error(request, 'This parcel cannot be assigned.')
            return redirect('/assign_parcel')

        if DeliveryAssignment.objects.filter(
            parcel=parcel,
            assignment_status__in=['Assigned', 'In Progress']
        ).exists():
            messages.error(request, 'This parcel already has an active assignment.')
            return redirect('/assign_parcel')

        with transaction.atomic():

            DeliveryAssignment.objects.create(
                parcel=parcel,
                delivery_agent=agent,
                assigned_by_id=request.session['userid'],
                assignment_status='Assigned'
            )

            agent.is_available = False
            agent.save(update_fields=['is_available'])

            parcel.status = 'Picked Up'
            parcel.save(update_fields=['status'])

            ParcelTrackingHistory.objects.create(
                parcel=parcel,
                status='Picked Up',
                location=parcel.source,
                description='Parcel assigned to delivery agent.',
                updated_by_id=request.session['userid']
            )

        messages.success(request, 'Parcel assigned successfully.')
        return redirect('/delivery_assignments')

    return render(
        request,
        'ADMIN/assign_parcel.html',
        {
            'parcels': parcels,
            'agents': agents
        }
    )


# ==========================================
# 25. VIEW DELIVERY ASSIGNMENTS - ADMIN
# ==========================================

def delivery_assignments(request):

    if 'userid' not in request.session:
        return redirect('/login')

    if request.session.get('usertype') != 'Admin':
        return redirect('/login')

    assignments = DeliveryAssignment.objects.select_related(
        'parcel',
        'delivery_agent',
        'assigned_by'
    ).order_by('-assigned_at')

    return render(
        request,
        'ADMIN/delivery_assignments.html',
        {'assignments': assignments}
    )


# ==========================================
# 26. REASSIGN PARCEL - ADMIN
# ==========================================

def reassign_parcel(request, assignment_id):

    if 'userid' not in request.session:
        return redirect('/login')

    if request.session.get('usertype') != 'Admin':
        return redirect('/login')

    assignment = get_object_or_404(
        DeliveryAssignment.objects.select_related(
            'parcel',
            'delivery_agent'
        ),
        id=assignment_id
    )

    if assignment.assignment_status not in ['Assigned', 'In Progress']:
        messages.error(request, 'This assignment cannot be reassigned.')
        return redirect('/delivery_assignments')

    agents = DeliveryAgentRegistration.objects.filter(
        is_available=True,
        user__is_active=True
    ).exclude(id=assignment.delivery_agent_id)

    if request.method == 'POST':

        agent_id = request.POST.get('agent_id')

        new_agent = get_object_or_404(
            DeliveryAgentRegistration,
            id=agent_id,
            is_available=True,
            user__is_active=True
        )

        old_agent = assignment.delivery_agent

        with transaction.atomic():

            if old_agent:

                old_agent_has_other_active = DeliveryAssignment.objects.filter(
                    delivery_agent=old_agent,
                    assignment_status__in=['Assigned', 'In Progress']
                ).exclude(id=assignment.id).exists()

                if not old_agent_has_other_active:
                    old_agent.is_available = True
                    old_agent.save(update_fields=['is_available'])

            assignment.delivery_agent = new_agent
            assignment.assignment_status = 'Assigned'
            assignment.save(
                update_fields=['delivery_agent', 'assignment_status']
            )

            new_agent.is_available = False
            new_agent.save(update_fields=['is_available'])

            ParcelTrackingHistory.objects.create(
                parcel=assignment.parcel,
                status=assignment.parcel.status,
                location=assignment.parcel.source,
                description='Delivery agent reassigned by administrator.',
                updated_by_id=request.session['userid']
            )

        messages.success(request, 'Parcel reassigned successfully.')
        return redirect('/delivery_assignments')

    return render(
        request,
        'ADMIN/assign_parcel.html',
        {
            'assignment': assignment,
            'parcels': Parcel.objects.filter(id=assignment.parcel_id),
            'agents': agents,
            'reassign_mode': True
        }
    )


# ==========================================
# 27. VIEW DELIVERY RECORDS - ADMIN
# ==========================================

def view_delivery_records(request):

    if 'userid' not in request.session:
        return redirect('/login')

    if request.session.get('usertype') != 'Admin':
        return redirect('/login')

    records = DeliveryRecord.objects.select_related(
        'parcel',
        'delivery_agent'
    ).order_by('-created_at')

    return render(
        request,
        'ADMIN/delivery_records.html',
        {'records': records}
    )


# ==========================================
# 28. VIEW ALL TRACKING HISTORY - ADMIN
# ==========================================

def all_tracking_history(request):

    if 'userid' not in request.session:
        return redirect('/login')

    if request.session.get('usertype') != 'Admin':
        return redirect('/login')

    history = ParcelTrackingHistory.objects.select_related(
        'parcel',
        'updated_by'
    ).order_by('-updated_at')

    return render(
        request,
        'ADMIN/tracking_history.html',
        {'history': history}
    )


# ==========================================
# 29. VIEW ASSIGNED PARCELS - DELIVERY AGENT
# ==========================================

def assigned_parcels(request):

    if 'userid' not in request.session:
        return redirect('/login')

    if request.session.get('usertype') != 'Delivery Agent':
        return redirect('/login')

    agent = get_object_or_404(
        DeliveryAgentRegistration,
        user_id=request.session['userid']
    )

    assignments = DeliveryAssignment.objects.filter(
        delivery_agent=agent
    ).select_related('parcel').order_by('-assigned_at')

    return render(
        request,
        'AGENT/assigned_parcels.html',
        {'assignments': assignments}
    )


# ==========================================
# 30. AGENT PARCEL DETAILS
# ==========================================

def agent_parcel_detail(request, parcel_id):

    if 'userid' not in request.session:
        return redirect('/login')

    if request.session.get('usertype') != 'Delivery Agent':
        return redirect('/login')

    agent = get_object_or_404(
        DeliveryAgentRegistration,
        user_id=request.session['userid']
    )

    assignment = get_object_or_404(
        DeliveryAssignment.objects.select_related('parcel'),
        parcel_id=parcel_id,
        delivery_agent=agent,
        assignment_status__in=['Assigned', 'In Progress']
    )

    history = ParcelTrackingHistory.objects.filter(
        parcel=assignment.parcel
    ).order_by('-updated_at')

    branches = CourierBranch.objects.filter(
        is_active=True
    )

    return render(
        request,
        'AGENT/parcel_detail.html',
        {
            'assignment': assignment,
            'parcel': assignment.parcel,
            'history': history,
            'branches': branches
        }
    )


# ==========================================
# 31. UPDATE PARCEL TRACKING - DELIVERY AGENT
# ==========================================

def update_parcel_tracking(request, parcel_id):

    if 'userid' not in request.session:
        return redirect('/login')

    if request.session.get('usertype') != 'Delivery Agent':
        return redirect('/login')

    agent = get_object_or_404(
        DeliveryAgentRegistration,
        user_id=request.session['userid']
    )

    assignment = get_object_or_404(
        DeliveryAssignment,
        parcel_id=parcel_id,
        delivery_agent=agent,
        assignment_status__in=['Assigned', 'In Progress']
    )

    parcel = assignment.parcel

    if request.method == 'POST':

        status = request.POST.get('status')
        location = request.POST.get('location')
        description = request.POST.get('description')

        allowed_statuses = [
            'In Transit',
            'At Branch',
            'Out for Delivery',
            'Delayed'
        ]

        if status not in allowed_statuses:
            messages.error(request, 'Invalid parcel status.')
            return redirect('/agent_parcel_detail/' + str(parcel.id))

        if not location:
            messages.error(request, 'Please enter the current location.')
            return redirect('/agent_parcel_detail/' + str(parcel.id))

        branch = None

        if status == 'At Branch':

            branch_id = request.POST.get('branch_id')

            if not branch_id:
                messages.error(request, 'Please select a branch.')
                return redirect('/agent_parcel_detail/' + str(parcel.id))

            branch = get_object_or_404(
                CourierBranch,
                id=branch_id,
                is_active=True
            )

        with transaction.atomic():

            parcel.status = status

            if status == 'At Branch':
                parcel.current_branch = branch
            elif status == 'In Transit':
                parcel.current_branch = None

            parcel.save()

            assignment.assignment_status = 'In Progress'
            assignment.save(update_fields=['assignment_status'])

            ParcelTrackingHistory.objects.create(
                parcel=parcel,
                status=status,
                location=location,
                description=description or 'Parcel tracking updated.',
                updated_by_id=request.session['userid']
            )

        messages.success(request, 'Parcel tracking updated successfully.')

    return redirect('/agent_parcel_detail/' + str(parcel.id))


# ==========================================
# 32. COMPLETE DELIVERY - DELIVERY AGENT
# ==========================================

def complete_delivery(request, parcel_id):

    if 'userid' not in request.session:
        return redirect('/login')

    if request.session.get('usertype') != 'Delivery Agent':
        return redirect('/login')

    agent = get_object_or_404(
        DeliveryAgentRegistration,
        user_id=request.session['userid']
    )

    assignment = get_object_or_404(
        DeliveryAssignment,
        parcel_id=parcel_id,
        delivery_agent=agent,
        assignment_status__in=['Assigned', 'In Progress']
    )

    parcel = assignment.parcel

    if request.method == 'POST':

        if parcel.status != 'Out for Delivery':
            messages.error(
                request,
                'Parcel must be Out for Delivery before completion.'
            )
            return redirect('/agent_parcel_detail/' + str(parcel.id))

        receiver_name = request.POST.get('receiver_name')
        receiver_phone = request.POST.get('receiver_phone')
        delivery_remarks = request.POST.get('delivery_remarks')
        delivery_proof = request.FILES.get('delivery_proof')

        if not receiver_name or not receiver_phone:
            messages.error(request, 'Receiver name and phone are required.')
            return redirect('/agent_parcel_detail/' + str(parcel.id))

        with transaction.atomic():

            delivery_date = timezone.now()

            DeliveryRecord.objects.create(
                parcel=parcel,
                delivery_agent=agent,
                receiver_name=receiver_name,
                receiver_phone=receiver_phone,
                delivery_status='Delivered',
                delivery_proof=delivery_proof,
                delivery_remarks=delivery_remarks,
                delivery_date=delivery_date
            )

            parcel.status = 'Delivered'
            parcel.delivered_at = delivery_date
            parcel.save(update_fields=['status', 'delivered_at'])

            assignment.assignment_status = 'Completed'
            assignment.completed_at = delivery_date
            assignment.save(
                update_fields=['assignment_status', 'completed_at']
            )

            other_active_assignments = DeliveryAssignment.objects.filter(
                delivery_agent=agent,
                assignment_status__in=['Assigned', 'In Progress']
            ).exclude(id=assignment.id).exists()

            if not other_active_assignments:
                agent.is_available = True
                agent.save(update_fields=['is_available'])

            ParcelTrackingHistory.objects.create(
                parcel=parcel,
                status='Delivered',
                location=parcel.destination,
                description='Parcel successfully delivered to receiver.',
                updated_by_id=request.session['userid']
            )

        messages.success(request, 'Delivery completed successfully.')
        return redirect('/assigned_parcels')

    return redirect('/agent_parcel_detail/' + str(parcel.id))


# ==========================================
# 33. FAILED DELIVERY - DELIVERY AGENT
# ==========================================

def failed_delivery(request, parcel_id):

    if 'userid' not in request.session:
        return redirect('/login')

    if request.session.get('usertype') != 'Delivery Agent':
        return redirect('/login')

    agent = get_object_or_404(
        DeliveryAgentRegistration,
        user_id=request.session['userid']
    )

    assignment = get_object_or_404(
        DeliveryAssignment,
        parcel_id=parcel_id,
        delivery_agent=agent,
        assignment_status__in=['Assigned', 'In Progress']
    )

    parcel = assignment.parcel

    if request.method == 'POST':

        remarks = request.POST.get('delivery_remarks')
        receiver_name = request.POST.get('receiver_name') or parcel.receiver_name
        receiver_phone = request.POST.get('receiver_phone') or parcel.receiver_phone

        if parcel.status != 'Out for Delivery':
            messages.error(request, 'Parcel must be Out for Delivery.')
            return redirect('/agent_parcel_detail/' + str(parcel.id))

        with transaction.atomic():

            delivery_date = timezone.now()

            DeliveryRecord.objects.create(
                parcel=parcel,
                delivery_agent=agent,
                receiver_name=receiver_name,
                receiver_phone=receiver_phone,
                delivery_status='Failed',
                delivery_remarks=remarks or 'Delivery attempt failed.',
                delivery_date=delivery_date
            )

            parcel.status = 'Returned'
            parcel.save(update_fields=['status'])

            assignment.assignment_status = 'Completed'
            assignment.completed_at = delivery_date
            assignment.save(
                update_fields=['assignment_status', 'completed_at']
            )

            other_active_assignments = DeliveryAssignment.objects.filter(
                delivery_agent=agent,
                assignment_status__in=['Assigned', 'In Progress']
            ).exclude(id=assignment.id).exists()

            if not other_active_assignments:
                agent.is_available = True
                agent.save(update_fields=['is_available'])

            ParcelTrackingHistory.objects.create(
                parcel=parcel,
                status='Returned',
                location=parcel.destination,
                description=remarks or 'Delivery attempt failed. Parcel returned.',
                updated_by_id=request.session['userid']
            )

        messages.success(request, 'Failed delivery recorded.')
        return redirect('/assigned_parcels')

    return redirect('/agent_parcel_detail/' + str(parcel.id))


# ==========================================
# 34. TOGGLE AGENT AVAILABILITY
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

        active_assignments = DeliveryAssignment.objects.filter(
            delivery_agent=agent,
            assignment_status__in=['Assigned', 'In Progress']
        ).exists()

        if active_assignments and agent.is_available:
            messages.error(
                request,
                'You cannot become unavailable while you have active assignments.'
            )

        else:
            agent.is_available = not agent.is_available
            agent.save(update_fields=['is_available'])

            messages.success(request, 'Availability updated successfully.')

    return redirect('/agent_home')
