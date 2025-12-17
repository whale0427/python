from django import forms
from .models import Grades

class GradesForm(forms.ModelForm):

    class Meta:
        model=Grades
        fields=["grade_name","grade_code"]