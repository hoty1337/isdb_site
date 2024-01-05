from django.contrib import admin
from .models import Doctors, ContactDetails, People, Articles


admin.site.register(Doctors)
admin.site.register(ContactDetails)
admin.site.register(People)
admin.site.register(Articles)
