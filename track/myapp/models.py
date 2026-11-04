
from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid


# ==========================================
# 1. LOGIN
# ==========================================

class Login(AbstractUser):

    user_type = models.CharField(max_length=50, blank=True)

    view_pass = models.CharField(
        max_length=255,
        blank=True
    )

    def __str__(self):
        return self.username


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
    phone = models.CharField(max_length=20)
    address = models.TextField()

    profile_image = models.FileField(
        upload_to='customer_profiles/',
        null=True,
        blank=True
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
    phone = models.CharField(max_length=20)
    address = models.TextField()

    employee_id = models.CharField(
        max_length=50,
        unique=True
    )

    vehicle_number = models.CharField(max_length=50)

    vehicle_type = models.CharField(max_length=100)

    experience_years = models.PositiveIntegerField(default=0)

    profile_image = models.FileField(
        upload_to='agent_profiles/',
        null=True,
        blank=True
    )

    is_available = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name