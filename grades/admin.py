from django.contrib import admin
from .models import Grades
# Register your models here.
class GradesAdmin(admin.ModelAdmin):
    list_display=("grade_name","grade_code")
    search_fields=("grade_name","grade_code")
    ordering = ["id"]

admin.site.register(Grades,GradesAdmin)