from django.db import models
from django.contrib.auth.models import User
from grades.models import Grades
# Create your models here.
GENDER_CHOICES=[
    ("M","男"),
    ("F","女")
]
class Teachers(models.Model):
    teacher_name=models.CharField(max_length=10,verbose_name="姓名")
    phone=models.CharField(max_length=11,verbose_name="电话",unique=True)
    gender=models.CharField(max_length=1,verbose_name="性别",choices=GENDER_CHOICES)
    birthday=models.DateField(verbose_name="生日",help_text="格式：YYYY-MM-DD")
    user=models.OneToOneField(User,on_delete=models.CASCADE,verbose_name="用户")
    grade=models.ForeignKey(Grades,on_delete=models.CASCADE,verbose_name="班级")


    class Meta:
        db_table="teachers"
        verbose_name="老师"
        verbose_name_plural="老师管理"
        ordering=["pk"]