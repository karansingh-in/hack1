from django.db import models


# Minimal vendor models to be expanded later
class Vendor(models.Model):
    user_id = models.IntegerField(null=True, blank=True)
    business_name = models.CharField(max_length=255)
    owner_name = models.CharField(max_length=255)
    stall_location = models.CharField(max_length=500)
    contact_number = models.CharField(max_length=20, blank=True)
    total_credits = models.IntegerField(default=0)
    hygiene_rating = models.CharField(max_length=5, blank=True)
    certificate_issued_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.business_name
