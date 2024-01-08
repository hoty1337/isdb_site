from datetime import date, timedelta
from django.shortcuts import render, redirect
from django.db import connection
import hashlib
from collections import namedtuple


# Create your views here.


def index(request):
    with connection.cursor() as cursor:
        cursor.callproc('get_doctors_list')
        doctors = namedTupleFetchAll(cursor)
        cursor.callproc('get_news')
        news = namedTupleFetchAll(cursor)
    return render(request, 'main/index.html', {'doctors': doctors, 'news': news, 'session': request.session})


def about(request):
    return render(request, 'main/about.html', {'session': request.session})


def doctors(request):
    with connection.cursor() as cursor:
        cursor.callproc('get_doctors_list')
        doctors = namedTupleFetchAll(cursor)
        cursor.callproc('get_news')
        news = namedTupleFetchAll(cursor)
    return render(request, 'main/doctors.html', {'doctors':doctors,'news':news,'session': request.session})


def namedTupleFetchAll(cursor):
    """Return all rows from a cursor as a namedtuple"""
    desc = cursor.description
    nt_result = namedtuple('Result', [col[0] for col in desc])
    return [nt_result(*row) for row in cursor.fetchall()]


def login(request):
	if 'id_user' in request.session:
		return redirect('/')
	email = None
	password = None
	if request.method == 'POST':
		email = request.POST['email']
		password = hashlib.md5(str(request.POST['password']).encode('utf-8')).hexdigest()
		with connection.cursor() as cursor:
			cursor.execute('SELECT id FROM people WHERE email = %s AND password = %s', (email, password))
			res = cursor.fetchone()
			if res is None:
				return render(request, 'main/login.html', {'error': 'Неверная почта или пароль.', 'session': request.session})
			request.session['id_user'] = res[0]
			return redirect('/')

	return render(request, 'main/login.html', {'email': email, 'password': password, 'session': request.session})


def register(request):
	if 'id_user' in request.session:
		return redirect('/')
	email = None
	password = None
	if request.method == 'POST':
		email = str(request.POST['email'])
		with connection.cursor() as cursor:
			cursor.execute('SELECT id FROM people WHERE email = %s', [email])
			res = cursor.fetchone()
			if res is None:
				name = str(request.POST['name'])
				surname = str(request.POST['surname'])
				patronymic = str(request.POST['patronymic'])
				sex = str(request.POST['sex'])
				dob = str(request.POST['dob'])
				password = hashlib.md5(str(request.POST['password']).encode('utf-8')).hexdigest()
				cursor.execute(
					'INSERT INTO people(name, surename, patrynomic, sex, dob, email, password) VALUES (%s, %s, %s, %s, %s, %s, %s)\
					 RETURNING id', [name, surname, patronymic, sex, dob, email, password])
				request.session['id_user'] = cursor.fetchone()[0]
				return redirect('/')
	return render(request, 'main/register.html', {'email': email, 'password': password, 'session': request.session})


def logout(request):
	if 'id_user' not in request.session:
		return redirect('/')
	del request.session['id_user']
	return redirect('/')


def appointments(request):
	if 'id_user' not in request.session:
		return redirect('/')
	with connection.cursor() as cursor:
		cursor.callproc('get_doctors_list')
		doctors = namedTupleFetchAll(cursor)
	return render(request, 'main/appointments.html', {'session': request.session, 'doctors': doctors, 'curdate': date.today().strftime('%Y-%m-%d'), 'lastdate': (date.today() + timedelta(days=30)).strftime('%Y-%m-%d')})
