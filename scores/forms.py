from django import forms
from scores.models import Scores
from students.models import Students

class ScoresForm(forms.ModelForm):
    def clean_student_name(self):
        student_name=self.cleaned_data["student_name"]
        students= Students.objects.filter(student_name=student_name)
        if not students.exists():
            raise forms.ValidationError("学生姓名不存在")
        return student_name

    def clean_student_number(self):
        student_number=self.cleaned_data["student_number"]
        students=Students.objects.filter(student_number=student_number)
        if not students.exists():
            raise forms.ValidationError("学号不存在")
        return student_number

    class Meta:
        model = Scores
        fields=["title","student_name","student_number","chinese_score","math_score","english_score"]