from django import forms
from .models import Students
from django.core.exceptions import ValidationError
import datetime
from grades.models import Grades

class StudentsForm(forms.ModelForm):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.fields.get("grade").queryset=Grades.objects.all().order_by("grade_code")

    def clean_student_name(self):
        student_name = self.cleaned_data["student_name"]
        if len(student_name) < 2 or len(student_name) > 50:
            raise ValidationError("姓名长度不符合规范（2-50）")
        return student_name

    def clean_student_number(self):
        student_number = self.cleaned_data["student_number"]
        if len(student_number) != 10:
            raise ValidationError("学号长度必须为10位")
        return student_number

    def clean_gender(self):
        gender = self.cleaned_data["gender"]
        if len(gender) == 0:
            raise ValidationError("性别不准为空")
        return gender

    def clean_birthday(self):
        birthday = self.cleaned_data["birthday"]
        if not isinstance(birthday, datetime.date):
            raise ValidationError("格式应为：YYYY-MM-DD")
        if birthday > datetime.date.today():
            raise ValidationError("出生日期要在今天之前")
        return birthday

    def clean_phone(self):
        phone = self.cleaned_data["phone"]
        if len(phone) != 11:
            raise ValidationError("电话长度必须为11位")
        return phone

    def clean_address(self):
        address = self.cleaned_data["address"]
        if not ("省" in address and "市" in address):
            raise ValidationError("地址必须包含省、市")
        return address

    class Meta:
        model=Students
        fields=[
            "student_name",
            "student_number",
            "grade",
            "gender",
            "birthday",
            "phone",
            "address",
        ]
        #用于页面显示的input是日期格式，并保证格式是一致的
        widgets={
            "birthday":forms.DateInput(attrs={"type":"date"},format="%Y-%m-%d"),
        }

