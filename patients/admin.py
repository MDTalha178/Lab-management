from django.contrib import admin

from patients.models import Test, TestType, Patient

# Register your models here.
admin.site.register(Test)
admin.site.register(TestType)
admin.site.register(Patient)