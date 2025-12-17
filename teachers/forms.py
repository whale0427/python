from django import forms
from .models import Teachers
import datetime
from grades.models import Grades

class TeachersForm(forms.ModelForm):

    def clean_teacher_name(self):
        teacher_name=self.cleaned_data["teacher_name"]
        if len(teacher_name)<2 or len(teacher_name)>50:
            raise forms.ValidationError("姓名长度不符合规范（2-50）")
        return teacher_name

    def clean_phone(self):
        phone=self.cleaned_data["phone"]
        if len(phone)!=11:
            raise forms.ValidationError("电话长度要11位")
        return phone

    def clean_gender(self):
        gender=self.cleaned_data["gender"]
        if len(gender)!=1:
            raise forms.ValidationError("性别不允许为空")
        return gender

    def clean_birthday(self):
        birthday=self.cleaned_data["birthday"]
        if not isinstance(birthday,datetime.date):
            raise forms.ValidationError("生日格式不正确，格式：YYYY-MM-DD")
        if birthday > datetime.date.today():
            raise forms.ValidationError("生日要在今天之前")
        return birthday



    class Meta:
        model=Teachers
        fields=("teacher_name","phone","grade","gender","birthday")

        widgets={
            "birthday":forms.DateInput(attrs={"type":"date"},format="%Y-%m-%d"),
        }