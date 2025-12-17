from django.utils.functional import cached_property

from django.db import models
from students.models import Students
from grades.models import Grades

# Create your models here.
class Scores(models.Model):
    title=models.CharField("考试名称",max_length=50)
    student_name=models.CharField("学生姓名",max_length=10)
    student_number=models.CharField("学号",max_length=10)
    chinese_score=models.DecimalField("语文",max_digits=4,decimal_places=1,null=True,blank=True)
    math_score=models.DecimalField("数学",max_digits=4,decimal_places=1,null=True,blank=True)
    english_score=models.DecimalField("英语",max_digits=4,decimal_places=1,null=True,blank=True)
    student=models.ForeignKey(Students,on_delete=models.CASCADE,related_name="scores",verbose_name="学生")
    grade=models.ForeignKey(Grades,on_delete=models.CASCADE,related_name="scores",verbose_name="班级")


    class Meta:
        db_table="scores"
        verbose_name="成绩"
        verbose_name_plural="成绩管理"
        ordering=["-pk"]