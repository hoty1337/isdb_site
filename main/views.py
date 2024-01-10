from datetime import date, datetime, timedelta
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
				try:
					cursor.execute(
					'INSERT INTO people(name, surename, patrynomic, sex, dob, email, password) VALUES (%s, %s, %s, %s, %s, %s, %s)\
					 RETURNING id', [name, surname, patronymic, sex, dob, email, password])
					request.session['id_user'] = cursor.fetchone()[0]
					return redirect('/')
				except Exception as err:
					return render(request, 'main/register.html',
												{'email': email, 'password': password, 'session': request.session,
												 'error': 'Ваш возраст должен быть больше 18 лет!'})
			return render(request, 'main/register.html',
								{'email': email, 'password': password, 'session': request.session, 'error': 'Данная почта уже занята!'})
	return render(request, 'main/register.html',
								{'email': email, 'password': password, 'session': request.session})


def logout(request):
	if 'id_user' not in request.session:
		return redirect('/')
	del request.session['id_user']
	return redirect('/')


def get_free_time(request):
	if request.method == 'GET':
		date = request.GET.get('date')
		doc_id = request.GET.get('doc_id')
		all_time = ['08:00', '09:00', '10:00', '11:00',
								'12:00', '13:00', '14:00', '15:00',
								'16:00', '17:00', '18:00', '19:00']
		with connection.cursor() as cursor:
			cursor.execute('SELECT date FROM appointments WHERE doctor_id = %s', [doc_id])
			result = cursor.fetchall()
			for row in result:
				if str(row[0].date()) == str(date):
					all_time.remove(row[0].time().strftime('%H:%M'))
		return render(request, 'main/time_range.html', {'all_time': all_time})
	return redirect('/')


def appointments(request):
	if 'id_user' not in request.session:
		return redirect('/')

	if request.method == 'POST':
		with connection.cursor() as cursor:
			cursor.execute('SELECT * FROM people WHERE id = %s', [request.session['id_user']])
			person = namedTupleFetchAll(cursor)
			email = person[0].email
			doc_id = request.POST.get('doc_id')
			chosen_date = request.POST.get('calendar')
			chosen_time = request.POST.get('time')
			chosen_datetime = chosen_date + ' ' + chosen_time
			tel = request.POST.get('tel')
			cursor.execute('SELECT id FROM patients WHERE people_id = %s', [request.session['id_user']])
			patients_id = cursor.fetchone()
			if patients_id is not None:
				patient_id = patients_id[0]
			if patients_id is None:
				cursor.execute('INSERT INTO contact_details (phone_number, email) VALUES (%s, %s) RETURNING id',
											 [tel, email])
				contact_details_id = cursor.fetchone()[0]
				cursor.execute('INSERT INTO patients (people_id, contact_details_id) VALUES (%s, %s) RETURNING id',
											 [request.session['id_user'], contact_details_id])
				patient_id = cursor.fetchone()[0]
			cursor.execute('INSERT INTO appointments (date, patient_id, doctor_id, status)' ' VALUES (%s, %s, %s, %s)',
										 [chosen_datetime, patient_id, doc_id, 'active'])

	with connection.cursor() as cursor:
		cursor.execute('SELECT date FROM appointments ')
		all_time = ['08:00', '09:00', '10:00', '11:00',
								'12:00', '13:00', '14:00', '15:00',
								'16:00', '17:00', '18:00', '19:00']

	today = datetime.today()
	min_date = today.strftime('%Y-%m-%d')

	with connection.cursor() as cursor:
		cursor.callproc('get_doctors_list')
		doctors = namedTupleFetchAll(cursor)

	dict_obj = {
		'session': request.session,
		'doctors': doctors,
		'min_date': min_date,
		'lastdate': (today + timedelta(days=30)).strftime('%Y-%m-%d'),
		'all_time': all_time
	}

	return render(request, 'main/appointments.html', dict_obj)


def get_reviews(request):
	if request.method == 'POST':
		with connection.cursor() as cursor:
			cursor.callproc('get_reviews', [request.POST.get('doc_id')])
			reviews = namedTupleFetchAll(cursor)
		return render(request, 'main/reviews.html', {'session': request.session, 'reviews': reviews})
	return redirect('/')


def send_review(request):
	if request.method == 'POST':
		with connection.cursor() as cursor:
			cursor.execute('SELECT id FROM patients WHERE patients.people_id = %s', [request.session['id_user']])
			patient_id = cursor.fetchone()
			if patient_id is not None:
				cursor.execute('INSERT INTO reviews (review, mark, date, doctor_id, patient_id) VALUES (%s, %s, %s, %s, %s)',
											 [request.POST.get('review_text'), request.POST.get('mark'), date.today().strftime('%Y-%m-%d'), request.POST.get('doc_id'),
											 patient_id[0]])
				cursor.callproc('get_reviews', [request.POST.get('doc_id')])
				reviews = namedTupleFetchAll(cursor)
			return render(request, 'main/reviews.html', {'session': request.session, 'reviews': reviews})
	return redirect('/')
