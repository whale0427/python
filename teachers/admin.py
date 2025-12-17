from django.contrib import admin
from .models import Teachers

# Register your models here.
class TeachersAdmin(admin.ModelAdmin):
    list_display=("teacher_name","phone","gender","birthday","grade")
    search_fields=("teacher_name",)

admin.site.register(Teachers,TeachersAdmin)