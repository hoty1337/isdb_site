from django.db import models


class People(models.Model):
	email = models.EmailField('Email', unique=True)
	password = models.CharField('Пароль', max_length=32, default='<PASSWORD>')
	name = models.CharField('Имя', max_length=50)
	surname = models.CharField('Фамилия', max_length=50)
	patronymic = models.CharField('Отчество', max_length=50)
	sex = models.CharField('Пол', max_length=10)
	dob = models.DateField('Дата рождения')

	def __str__(self):
		return self.name

	class Meta:
		verbose_name = 'Человек'
		verbose_name_plural = 'Люди'


class ContactDetails(models.Model):
	phone_number = models.CharField('Номер телефона', max_length=20)
	email = models.EmailField('Email', unique=True)

	def __str__(self):
		return self.email

	class Meta:
		verbose_name = 'Контактные данные'


class Patients(models.Model):
	people = models.ForeignKey(People, on_delete=models.CASCADE)
	contact_details = models.ForeignKey(ContactDetails, on_delete=models.CASCADE)

	class Meta:
		verbose_name = 'Пациент'
		verbose_name_plural = 'Пациенты'


class Doctors(models.Model):
	people = models.ForeignKey(People, on_delete=models.CASCADE)
	contact_details = models.ForeignKey(ContactDetails, on_delete=models.CASCADE)
	specialization = models.CharField('Специализация', max_length=50)
	qualification = models.CharField('Квалификация', max_length=64)
	areas_of_practice = models.CharField('Зоны практики', max_length=100)
	photo = models.TextField('Фото')
	short_bio = models.TextField('Биография')

	class Meta:
		verbose_name = 'Доктор'
		verbose_name_plural = 'Доктора'


class Appointments(models.Model):
	date = models.DateTimeField('Дата')
	status = models.CharField('Статус', max_length=20)
	patient = models.ForeignKey(Patients, on_delete=models.CASCADE)
	doctor = models.ForeignKey(Doctors, on_delete=models.CASCADE)

	class Meta:
		verbose_name = 'Встреча'
		verbose_name_plural = 'Встречи'


class AppointmentsSchedule(models.Model):
	work_days = models.CharField('Рабочие дни', max_length=50)
	business_hours = models.CharField('Рабочие часы', max_length=50)
	available_slots = models.CharField('Свободные места', max_length=50)
	doctor = models.ForeignKey(Doctors, on_delete=models.CASCADE)
	appointments = models.ForeignKey(Appointments, on_delete=models.CASCADE)

	class Meta:
		verbose_name = 'Расписание встречи'
		verbose_name_plural = 'Расписание встреч'


class Stuff(models.Model):
	people = models.ForeignKey(People, on_delete=models.CASCADE)
	role = models.CharField('Роль', max_length=50)
	admin_access = models.BooleanField('Администратор', default=False)

	class Meta:
		verbose_name = 'Персонал'


class Payments(models.Model):
	people = models.ForeignKey(People, on_delete=models.CASCADE)
	sum = models.DecimalField('Сумма', decimal_places=2, max_digits=10)
	date = models.DateTimeField('Дата')
	status = models.CharField('Статус', max_length=20)

	class Meta:
		verbose_name = 'Платёж'
		verbose_name_plural = 'Платежи'


class Reviews(models.Model):
	review = models.TextField('Отзыв')
	mark = models.IntegerField('Оценка')
	date = models.DateTimeField('Дата')
	doctor = models.ForeignKey(Doctors, on_delete=models.CASCADE)
	patient = models.ForeignKey(Patients, on_delete=models.CASCADE)

	class Meta:
		verbose_name = 'Отзыв'
		verbose_name_plural = 'Отзывы'


class Articles(models.Model):
	people = models.ForeignKey(People, on_delete=models.CASCADE, default=1)
	title = models.CharField('Название', max_length=50)
	short_description = models.CharField('Описание', max_length=255)
	full_text = models.TextField('Текст')
	date = models.DateTimeField('Дата публикации')

	def __str__(self):
		return self.title

	class Meta:
		verbose_name = 'Новость'
		verbose_name_plural = 'Новости'
