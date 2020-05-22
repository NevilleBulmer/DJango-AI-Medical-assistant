# Class responsible for handling all application models.
from django.contrib import admin
from .models import *

# Register your models here.
# The model for users, I.e. display information, add, remove and/or modify.
admin.site.register(User)
# The model for appointments, I.e. display information, add, remove and/or modify.
admin.site.register(Appointment)
# The model for prescriptions, I.e. display information, add, remove and/or modify.
admin.site.register(Prescription)
# The model for insurance, I.e. display information, add, remove and/or modify.
admin.site.register(Insurance)
