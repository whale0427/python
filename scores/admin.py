from django.contrib import admin
from .models import Scores

# Register your models here.
class ScoresAdmin(admin.ModelAdmin):
    list_display=("title","student_name","student_number","chinese_score",
                  "math_score","english_score","grade")
    search_fields=("title","student_name","student_number")

admin.site.register(Scores,ScoresAdmin)