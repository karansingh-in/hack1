from django.db import models
from django.conf import settings


class Vendor(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    business_name = models.CharField(max_length=255)
    owner_name = models.CharField(max_length=255)
    stall_location = models.CharField(max_length=500)
    contact_number = models.CharField(max_length=20, blank=True)
    stall_photo = models.ImageField(upload_to='stall_photos/', null=True, blank=True)
    total_credits = models.IntegerField(default=0)
    hygiene_rating = models.CharField(max_length=5, blank=True)
    certificate_issued_date = models.DateField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.business_name


class HygieneChecklist(models.Model):
    vendor = models.OneToOneField(Vendor, on_delete=models.CASCADE)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Checklist for {self.vendor.business_name}"


class ChecklistItem(models.Model):
    checklist = models.ForeignKey(HygieneChecklist, on_delete=models.CASCADE, related_name='items')
    criterion = models.ForeignKey('core.HygieneCriteria', on_delete=models.CASCADE)
    is_compliant = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.criterion.criterion_name}: {'Yes' if self.is_compliant else 'No'}"
