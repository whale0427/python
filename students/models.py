from django.db import models
from django.contrib.auth.models import User
from grades.models import Grades

# Create your models here.
#必须这样写，必须是元组格式，格式是(值，显示文本)
#保存到数据库的是值；显示到网页的是显示文本
GENDER_CHOICES=[
    ("M","男"),
    ("F","女"),
]
class Students(models.Model):
    student_number=models.CharField("学号",max_length=10,unique=True)
    student_name=models.CharField("姓名",max_length=10)
    gender=models.CharField("性别",max_length=1,choices=GENDER_CHOICES)
    birthday=models.DateField("生日",help_text="格式：YYYY-MM-DD")
    phone=models.CharField("电话",max_length=11)
    address=models.CharField("地址",max_length=100)
    #一对一，用户表，auth_user
    user=models.OneToOneField(User,on_delete=models.CASCADE,verbose_name="用户")
    #一对多，班级表
    grade=models.ForeignKey(Grades,on_delete=models.CASCADE,related_name="students",verbose_name="班级")

    def __str__(self):
        return self.student_name+"_"+self.student_number

    class Meta:
        db_table="students"
        verbose_name="学生"
        verbose_name_plural="学生管理"
        ordering=["pk"]