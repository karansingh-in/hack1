from django.contrib import admin
from .models import HygieneCriteria


@admin.register(HygieneCriteria)
class HygieneCriteriaAdmin(admin.ModelAdmin):
    list_display = ('criterion_name', 'category', 'credit_points', 'is_mandatory')
    list_filter = ('category', 'is_mandatory')
