from django.db import models

# Create your models here.
class Grades(models.Model):
    grade_name=models.CharField("班级名称",max_length=50,unique=True)
    grade_code=models.CharField("班级编号",max_length=50,unique=True)

    def __str__(self):
        return self.grade_name

    class Meta:
        db_table="grades"
        verbose_name="班级"
        verbose_name_plural="班级管理"
