from django.shortcuts import render
from django.http import HttpResponse
from .models import Vendor


def vendor_list(request):
    vendors = Vendor.objects.all()[:20]
    return render(request, 'vendors/vendor_list.html', {'vendors': vendors})


def dummy(request):
    return HttpResponse('vendors placeholder')
