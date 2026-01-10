from django.db import models
from django.contrib.auth.models import User


# Placeholder models: we'll extend or replace with a custom user model later
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=20, choices=(('vendor', 'Vendor'), ('customer', 'Customer')))
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} ({self.user_type})"
