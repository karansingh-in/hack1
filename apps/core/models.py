from django.db import models


class HygieneCriteria(models.Model):
    CATEGORY_CHOICES = (
        ('Personal Hygiene', 'Personal Hygiene'),
        ('Facilities', 'Facilities'),
        ('Cleanliness', 'Cleanliness'),
        ('Waste Management', 'Waste Management'),
        ('Location', 'Location'),
    )

    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    criterion_name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    credit_points = models.IntegerField()
    is_mandatory = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.criterion_name} ({self.credit_points} pts)"
