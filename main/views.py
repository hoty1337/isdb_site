from django.shortcuts import render
from .models import Doctors, Articles

# Create your views here.


def index(request):
    doctors = Doctors.objects.all()
    news = Articles.objects.all().order_by('-date')
    return render(request, 'main/index.html', {'doctors': doctors, 'news': news})


def about(request):
    return render(request, 'main/about.html')
