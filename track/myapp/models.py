
from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid


# ==========================================
# 1. LOGIN
# ==========================================

class Login(AbstractUser):

    user_type = models.CharField(max_length=50, blank=True)
    view_pass = models.CharField(max_length=255, blank=True)


# ==========================================
# 2. CUSTOMER REGISTRATION
# ==========================================

class CustomerRegistration(models.Model):

    user = models.OneToOneField(
        Login,
        on_delete=models.CASCADE,
        related_name='customer_profile'
    )

    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    address = models.TextField()
    profile_image = models.ImageField(
        upload_to='customer_profiles/',
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# ==========================================
# 3. DELIVERY AGENT REGISTRATION
# ==========================================

class DeliveryAgentRegistration(models.Model):

    user = models.OneToOneField(
        Login,
        on_delete=models.CASCADE,
        related_name='agent_profile'
    )

    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    address = models.TextField()

    employee_id = models.CharField(max_length=50, unique=True)

    vehicle_number = models.CharField(max_length=30)
    vehicle_type = models.CharField(max_length=50)

    experience_years = models.PositiveIntegerField(default=0)

    profile_image = models.ImageField(
        upload_to='agent_profiles/',
        blank=True,
        null=True
    )

    is_available = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# ==========================================
# 4. COURIER BRANCH
# ==========================================

class CourierBranch(models.Model):

    branch_name = models.CharField(max_length=100)
    branch_code = models.CharField(max_length=30, unique=True)

    location = models.CharField(max_length=200)
    address = models.TextField()

    phone = models.CharField(max_length=15)
    email = models.EmailField(blank=True)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.branch_name


# ==========================================
# 5. PARCEL
# ==========================================

class Parcel(models.Model):

    DELIVERY_TYPE = [
        ('Standard', 'Standard'),
        ('Express', 'Express'),
        ('Same Day', 'Same Day'),
    ]

    STATUS = [
        ('Booked', 'Booked'),
        ('Picked Up', 'Picked Up'),
        ('In Transit', 'In Transit'),
        ('At Branch', 'At Branch'),
        ('Out for Delivery', 'Out for Delivery'),
        ('Delivered', 'Delivered'),
        ('Delayed', 'Delayed'),
        ('Cancelled', 'Cancelled'),
        ('Returned', 'Returned'),
    ]

    tracking_id = models.CharField(
        max_length=20,
        unique=True,
        editable=False
    )

    customer = models.ForeignKey(
        CustomerRegistration,
        on_delete=models.CASCADE,
        related_name='parcels'
    )

    sender_name = models.CharField(max_length=100)
    sender_phone = models.CharField(max_length=15)
    sender_address = models.TextField()

    receiver_name = models.CharField(max_length=100)
    receiver_phone = models.CharField(max_length=15)
    receiver_address = models.TextField()

    source = models.CharField(max_length=200)
    destination = models.CharField(max_length=200)

    parcel_type = models.CharField(max_length=100)
    parcel_description = models.TextField(blank=True)

    weight = models.FloatField()

    # Distance used for ML prediction
    distance_km = models.FloatField(default=0)

    delivery_type = models.CharField(
        max_length=30,
        choices=DELIVERY_TYPE,
        default='Standard'
    )

    delivery_charge = models.FloatField(default=0)

    status = models.CharField(
        max_length=30,
        choices=STATUS,
        default='Booked'
    )

    current_branch = models.ForeignKey(
        CourierBranch,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='parcels'
    )

    booking_date = models.DateTimeField(auto_now_add=True)

    expected_delivery_date = models.DateField(
        null=True,
        blank=True
    )

    delivered_at = models.DateTimeField(
        null=True,
        blank=True
    )

    def save(self, *args, **kwargs):

        if not self.tracking_id:
            self.tracking_id = 'CR' + uuid.uuid4().hex[:12].upper()

        super().save(*args, **kwargs)

    def __str__(self):
        return self.tracking_id


# ==========================================
# 6. DELIVERY ASSIGNMENT
# ==========================================

class DeliveryAssignment(models.Model):

    ASSIGNMENT_STATUS = [
        ('Assigned', 'Assigned'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]

    parcel = models.ForeignKey(
        Parcel,
        on_delete=models.CASCADE,
        related_name='assignments'
    )

    delivery_agent = models.ForeignKey(
        DeliveryAgentRegistration,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assignments'
    )

    assigned_by = models.ForeignKey(
        Login,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_assignments'
    )

    assignment_status = models.CharField(
        max_length=30,
        choices=ASSIGNMENT_STATUS,
        default='Assigned'
    )

    assigned_at = models.DateTimeField(auto_now_add=True)

    completed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    remarks = models.TextField(blank=True)

    def __str__(self):
        return self.parcel.tracking_id


# ==========================================
# 7. PARCEL TRACKING HISTORY
# ==========================================

class ParcelTrackingHistory(models.Model):

    parcel = models.ForeignKey(
        Parcel,
        on_delete=models.CASCADE,
        related_name='tracking_history'
    )

    status = models.CharField(max_length=30)

    location = models.CharField(max_length=200)

    description = models.TextField()

    updated_by = models.ForeignKey(
        Login,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.parcel.tracking_id + ' - ' + self.status


# ==========================================
# 8. DELIVERY RECORD
# ==========================================

class DeliveryRecord(models.Model):

    DELIVERY_STATUS = [
        ('Delivered', 'Delivered'),
        ('Failed', 'Failed'),
    ]

    parcel = models.OneToOneField(
        Parcel,
        on_delete=models.CASCADE,
        related_name='delivery_record'
    )

    delivery_agent = models.ForeignKey(
        DeliveryAgentRegistration,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    receiver_name = models.CharField(max_length=100)
    receiver_phone = models.CharField(max_length=15)

    delivery_status = models.CharField(
        max_length=30,
        choices=DELIVERY_STATUS,
        default='Delivered'
    )

    delivery_proof = models.ImageField(
        upload_to='delivery_proofs/',
        null=True,
        blank=True
    )

    delivery_remarks = models.TextField(blank=True)

    delivery_date = models.DateTimeField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.parcel.tracking_id
