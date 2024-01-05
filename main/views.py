from django.shortcuts import render
from django.db import connection
from .models import Doctors, Articles
from collections import namedtuple

# Create your views here.


def index(request):
    with connection.cursor() as cursor:
        cursor.callproc('get_doctors_list')
        doctors = namedTupleFetchAll(cursor)
        cursor.callproc('get_news')
        news = namedTupleFetchAll(cursor)
    return render(request, 'main/index.html', {'doctors': doctors, 'news': news})


def about(request):
    return render(request, 'main/about.html')


def namedTupleFetchAll(cursor):
    """Return all rows from a cursor as a namedtuple"""
    desc = cursor.description
    nt_result = namedtuple('Result', [col[0] for col in desc])
    return [nt_result(*row) for row in cursor.fetchall()]