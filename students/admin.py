from django.contrib import admin
from .models import Students
# Register your models here.
class StudentsAdmin(admin.ModelAdmin):
    list_display=("student_number","student_name","gender","birthday","phone","address")
    search_fields=("student_number","student_name")

admin.site.register(Students,StudentsAdmin)